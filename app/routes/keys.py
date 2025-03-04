# app/routes/keys.py
from fastapi import APIRouter, Request, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from .. import crud, schemas
from ..database import get_db
from ..auth import get_current_user
from ..models import Key, Log
from sqlalchemy.future import select
from datetime import datetime  # Already added
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/validate")
async def validate_key(request: schemas.KeyValidate, req: Request, db: AsyncSession = Depends(get_db)):
    logger.debug("Starting validate_key")
    client_ip = req.client.host
    logger.debug(f"Client IP: {client_ip}")
    
    if await crud.is_blacklisted(db, request.key):
        logger.debug("Key is blacklisted")
        raise HTTPException(status_code=403, detail="Key is blacklisted")
    
    logger.debug("Checking auto-blacklist")
    was_blacklisted, reason = await crud.auto_blacklist_check(db, request.key, request.hwid, client_ip)
    logger.debug(f"Auto-blacklist result: {was_blacklisted}, reason: {reason}")
    
    if was_blacklisted:
        raise HTTPException(status_code=403, detail=f"Key auto-blacklisted: {reason}")
    elif reason == "Invalid HWID":
        # Get the key ID
        db_key = (await db.execute(select(Key).filter_by(key=request.key))).scalars().first()
        if not db_key:
            raise HTTPException(status_code=404, detail="Key not found")
        
        # Count failed attempts
        logs = (await db.execute(select(Log).filter_by(key_id=db_key.id))).scalars().all()
        failed_count = len([log for log in logs if not log.success]) + 1  # Fixed: Removed "Indicate a"
        if failed_count <= 3:
            raise HTTPException(status_code=403, detail=f"Invalid HWID (attempt {failed_count}/3)")
        # If this line is reached, it should already be blacklisted by auto_blacklist_check

    # Increment use and log success
    db_key = await crud.increment_key_use(db, request.key, request.hwid, client_ip)
    if not db_key:
        raise HTTPException(status_code=404, detail="Key not found")

    # Final validation (redundant due to auto-blacklist, but kept for safety)
    if db_key.expires_at and datetime.now() > db_key.expires_at:
        raise HTTPException(status_code=403, detail="Key expired")
    if db_key.max_uses is not None and db_key.current_uses > db_key.max_uses:
        raise HTTPException(status_code=403, detail="Max uses exceeded")

    return {"valid": True, "message": "Key validated successfully"}

@router.post("/", response_model=schemas.KeyResponse)
async def create_key(key: schemas.KeyCreate, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return await crud.create_key(db, key)

@router.get("/")
async def get_all_keys(db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return await crud.get_all_keys(db)

@router.delete("/{key}")
async def delete_key(key: str, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    if not key:
        raise HTTPException(status_code=404, detail="Key cannot be empty")
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    db_key = await crud.delete_key(db, key)
    if db_key is None:
        raise HTTPException(status_code=404, detail="Key not found")
    return {"message": "Key deleted"}

@router.post("/{key}/reset-hwid")
async def reset_hwid(key: str, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    if not key:
        raise HTTPException(status_code=404, detail="Key cannot be empty")
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    # Clear HWID logs
    await db.execute("DELETE FROM logs WHERE key_id = (SELECT id FROM keys WHERE key = :key)", {"key": key})
    await db.commit()
    return {"message": f"HWID reset for key: {key}"}