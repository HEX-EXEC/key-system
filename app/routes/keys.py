from fastapi import APIRouter, Depends, HTTPException, status
from .. import schemas, crud
from ..auth import get_current_user
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from ..models import Key, KeyValidationAttempt
from datetime import datetime, timezone
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Loading keys.py module")

router = APIRouter()

logger.info("Defining create_key endpoint")
@router.post("/", response_model=schemas.Key)
def create_key(key: schemas.KeyCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    logger.info(f"create_key called with key: {key}, user: {current_user}")
    if current_user.role != "admin":
        logger.warning(f"User {current_user.username} does not have admin role")
        raise HTTPException(status_code=403, detail="Not authorized to create keys")
    
    # Ensure expires_at is timezone-aware
    expires_at = key.expires_at
    if expires_at and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    new_key = Key(
        key=str(uuid.uuid4()),
        created_at=datetime.now(timezone.utc),
        expires_at=expires_at,
        max_uses=key.max_uses,
        current_uses=0
    )
    logger.info(f"Creating new key: {new_key.key}")
    db.add(new_key)
    db.commit()
    db.refresh(new_key)
    logger.info(f"Created key: {new_key.key}")
    return new_key

logger.info("Defining get_all_keys endpoint")
@router.get("/")
def get_all_keys(db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return crud.get_all_keys(db)

logger.info("Defining delete_key endpoint")
@router.delete("/{key}")
def delete_key(key: str, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    if not key:
        raise HTTPException(status_code=404, detail="Key cannot be empty")
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    db_key = crud.delete_key(db, key)
    if db_key is None:
        raise HTTPException(status_code=404, detail="Key not found")
    return {"message": "Key deleted"}

logger.info("Defining validate_key endpoint")
@router.post("/validate")
def validate_key(validation: schemas.KeyValidation, db: Session = Depends(get_db)):
    key = crud.get_key(db, validation.key)
    if not key:
        raise HTTPException(status_code=404, detail="Key not found")
    if crud.is_key_blacklisted(db, validation.key):
        raise HTTPException(status_code=403, detail="Key is blacklisted")
    
    # Ensure expires_at is timezone-aware before comparison
    expires_at = key.expires_at
    if expires_at and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if expires_at and expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=403, detail="Key has expired")
    if key.max_uses and key.current_uses >= key.max_uses:
        raise HTTPException(status_code=403, detail="Key usage limit exceeded")

    attempt = KeyValidationAttempt(
        key=validation.key,
        hwid=validation.hwid,
        attempt_time=datetime.now(timezone.utc)
    )
    db.add(attempt)

    if key.hwid and key.hwid != validation.hwid:
        failed_attempts = crud.get_failed_attempts(db, validation.key, validation.hwid)
        if len(failed_attempts) >= 2:
            crud.add_to_blacklist(db, validation.key, "Too many failed HWID attempts")
            raise HTTPException(status_code=403, detail="Key auto-blacklisted: Too many failed HWID attempts")
        raise HTTPException(status_code=400, detail=f"Invalid HWID (attempt {len(failed_attempts) + 1}/3)")

    key.hwid = validation.hwid
    key.current_uses += 1
    db.commit()
    return {"valid": True, "message": "Key validated successfully"}

logger.info("Defining reset_hwid endpoint")
@router.post("/{key}/reset-hwid")
def reset_hwid(key: str, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    if not key:
        raise HTTPException(status_code=404, detail="Key cannot be empty")
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    db.execute(text("DELETE FROM key_validation_attempts WHERE key = :key"), {"key": key})
    db.commit()
    return {"message": f"HWID reset for key: {key}"}

if __name__ == "__main__":
    print("Successfully loaded keys.py")