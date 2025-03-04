# app/crud.py
from sqlalchemy import select
from sqlalchemy.orm import Session
from . import schemas
from .models import Key, Log, Blacklist, User
from datetime import datetime

def is_blacklisted(db: Session, key: str):
    blacklist = db.execute(select(Blacklist).filter_by(key=key)).scalars().first()
    return blacklist is not None

def auto_blacklist_check(db: Session, key: str, hwid: str, ip: str):
    should_blacklist = False
    reason = None

    # Get the key
    db_key = db.execute(select(Key).filter_by(key=key)).scalars().first()
    if not db_key:
        return False, "Key not found"

    # Check logs for this key
    logs = db.execute(select(Log).filter_by(key_id=db_key.id)).scalars().all()
    if not logs:
        # First use of the key
        if hwid != db_key.hwid:
            reason = "Invalid HWID"
        return should_blacklist, reason

    # Check for HWID mismatch
    if hwid != db_key.hwid:
        failed_attempts = len([log for log in logs if not log.success])
        if failed_attempts >= 3:
            should_blacklist = True
            reason = "Too many failed HWID attempts"
            # Add to blacklist
            blacklist = Blacklist(key=key, reason=reason)
            db.add(blacklist)
            db.commit()
        else:
            reason = "Invalid HWID"
        return should_blacklist, reason

    # Check for IP change (potential key sharing)
    ips = set(log.ip for log in logs)
    if ip not in ips:
        # New IP detected
        if len(ips) >= 1:  # Allow one IP change before blacklisting
            should_blacklist = True
            reason = "IP change detected, possible key sharing"
            # Add to blacklist
            blacklist = Blacklist(key=key, reason=reason)
            db.add(blacklist)
            db.commit()
        return should_blacklist, reason

    # Check for multiple HWIDs with different IPs (key sharing)
    hwids = set(log.hwid for log in logs)
    if len(hwids) > 1 and len(ips) > 1:
        should_blacklist = True
        reason = "Multiple HWIDs and IPs detected, possible key sharing"
        # Add to blacklist
        blacklist = Blacklist(key=key, reason=reason)
        db.add(blacklist)
        db.commit()

    return should_blacklist, reason

def increment_key_use(db: Session, key: str, hwid: str, ip: str):
    db_key = db.execute(select(Key).filter_by(key=key)).scalars().first()
    if not db_key:
        return None

    # Increment current uses
    db_key.current_uses += 1
    db_key.last_used = datetime.utcnow()

    # Log the attempt
    success = hwid == db_key.hwid
    log = Log(key_id=db_key.id, hwid=hwid, ip=ip, success=success)
    db.add(log)
    db.commit()
    db.refresh(db_key)
    return db_key

def create_key(db: Session, key: schemas.KeyCreate):
    db_key = Key(
        key=schemas.generate_key(),
        created_at=datetime.utcnow(),
        expires_at=key.expires_at,
        max_uses=key.max_uses,
        hwid=key.hwid,
        current_uses=0
    )
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    return db_key

def get_all_keys(db: Session):
    return db.execute(select(Key)).scalars().all()

def delete_key(db: Session, key: str):
    db_key = db.execute(select(Key).filter_by(key=key)).scalars().first()
    if not db_key:
        return None
    db.delete(db_key)
    db.commit()
    return db_key

def get_blacklist(db: Session):
    return db.execute(select(Blacklist)).scalars().all()

def add_to_blacklist(db: Session, blacklist: schemas.BlacklistCreate):
    db_blacklist = Blacklist(key=blacklist.key, reason=blacklist.reason)
    db.add(db_blacklist)
    db.commit()
    db.refresh(db_blacklist)
    return db_blacklist

def remove_from_blacklist(db: Session, blacklist: schemas.BlacklistDelete):
    db_blacklist = db.execute(select(Blacklist).filter_by(key=blacklist.key)).scalars().first()
    if not db_blacklist:
        return {"message": "Key not found in blacklist"}
    db.delete(db_blacklist)
    db.commit()
    return {"message": "Key removed from blacklist"}

def create_user(db: Session, user: schemas.UserCreate):
    db_user = User(username=user.username, hashed_password=user.hashed_password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, username: str):
    return db.execute(select(User).filter_by(username=username)).scalars().first()