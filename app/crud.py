# app/crud.py
import secrets
from datetime import datetime
from sqlalchemy.future import select
from sqlalchemy import text
from .models import Key, Log, Blacklist, User
from .schemas import KeyCreate, BlacklistCreate, UserCreate
from .auth import get_password_hash
from fastapi import HTTPException

async def create_key(db, key_data: KeyCreate):
    key = secrets.token_urlsafe(32)
    while (await db.execute(select(Key).filter_by(key=key))).scalars().first():
        key = secrets.token_urlsafe(32)
    db_key = Key(key=key, created_at=datetime.now(), **key_data.dict())
    db.add(db_key)
    await db.commit()
    await db.refresh(db_key)
    return db_key

async def delete_key(db, key: str):
    db_key = (await db.execute(select(Key).filter_by(key=key))).scalars().first()
    if db_key:
        await db.delete(db_key)
        await db.commit()
    return db_key

async def is_blacklisted(db, key: str):
    return (await db.execute(select(Blacklist).filter_by(key=key))).scalars().first() is not None

async def blacklist_key(db, blacklist_data: BlacklistCreate):
    db_blacklist = Blacklist(**blacklist_data.dict())
    db.add(db_blacklist)
    await db.commit()
    await db.refresh(db_blacklist)
    return db_blacklist

async def create_user(db, user_data: UserCreate):
    hashed_password = get_password_hash(user_data.password)
    db_user = User(username=user_data.username, password_hash=hashed_password, role=user_data.role)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def get_all_keys(db):
    keys = (await db.execute(select(Key))).scalars().all()
    result = []
    for key in keys:
        blacklisted = await is_blacklisted(db, key.key)
        result.append({
            "key": key.key,
            "created_at": key.created_at,
            "expires_at": key.expires_at,
            "max_uses": key.max_uses,
            "current_uses": key.current_uses,
            "status": "blacklisted" if blacklisted else "active"
        })
    return result

async def auto_blacklist_check(db, key: str, hwid: str, ip: str):
    db_key = (await db.execute(select(Key).filter_by(key=key))).scalars().first()
    if not db_key:
        raise HTTPException(status_code=404, detail="Key not found")

    logs = (await db.execute(select(Log).filter_by(key_id=db_key.id))).scalars().all()
    hwids = {log.hwid for log in logs if log.hwid}
    ips = {log.ip for log in logs if log.ip}
    failed_attempts = len([log for log in logs if not log.success])

    should_blacklist = False
    reason = None

    # Expired
    if db_key.expires_at and datetime.now() > db_key.expires_at:
        should_blacklist = True
        reason = "Key expired"

    # Exceeded max uses
    elif db_key.max_uses is not None and db_key.current_uses >= db_key.max_uses:
        should_blacklist = True
        reason = "Max uses exceeded"

    # IP change detection (allow 1 IP only)
    elif ip not in ips and len(ips) >= 1:
        should_blacklist = True
        reason = "IP change detected"

    # Key sharing detection (multiple HWIDs and IPs)
    elif len(hwids) > 1 and len(ips) > 1:
        should_blacklist = True
        reason = "Key sharing detected (multiple HWIDs and IPs)"

    # Multiple false HWID requests (blacklist after 3 failures)
    elif failed_attempts >= 3:
        should_blacklist = True
        reason = "Too many failed HWID attempts"

    # HWID mismatch (log failure but don’t blacklist yet if under 3)
    elif hwids and hwid not in hwids and failed_attempts < 3:
        db_log = Log(key_id=db_key.id, hwid=hwid, ip=ip, timestamp=datetime.now(), success=False)
        db.add(db_log)
        await db.commit()
        return False, "Invalid HWID"

    if should_blacklist and not await is_blacklisted(db, key):
        blacklist_data = BlacklistCreate(key=key, reason=reason)
        await blacklist_key(db, blacklist_data)
        return True, reason

    return False, None

async def increment_key_use(db, key: str, hwid: str, ip: str):
    db_key = (await db.execute(select(Key).filter_by(key=key))).scalars().first()
    if db_key:
        db_key.current_uses += 1
        db_log = Log(key_id=db_key.id, hwid=hwid, ip=ip, timestamp=datetime.now(), success=True)
        db.add(db_log)
        await db.commit()
        await db.refresh(db_key)
    return db_key