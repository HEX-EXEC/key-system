# app/routes/keys.py
from fastapi import APIRouter, Depends, HTTPException, status
from app import schemas, crud
from app.auth import get_current_user
from app.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy.sql import text  # Import text function
from app.models import Key, KeyValidationAttempt
from datetime import datetime, timezone
import uuid

router = APIRouter()

@router.post("/", response_model=schemas.Key)
def create_key(key: schemas.KeyCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to create keys")
    new_key = Key(
        key=str(uuid.uuid4()),
        created_at=datetime.now(timezone.utc),
        expires_at=key.expires_at,
        max_uses=key.max_uses,
        current_uses=0
    )
    db.add(new_key)
    db.commit()
    db.refresh(new_key)
    return new_key

@router.get("/")
def get_all_keys(db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return crud.get_all_keys(db)

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

@router.post("/validate")
def validate_key(validation: schemas.KeyValidation, db: Session = Depends(get_db)):
    key = crud.get_key(db, validation.key)
    if not key:
        raise HTTPException(status_code=404, detail="Key not found")
    if crud.is_key_blacklisted(db, validation.key):
        raise HTTPException(status_code=403, detail="Key is blacklisted")
    if key.expires_at and key.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=403, detail="Key has expired")
    if key.max_uses and key.current_uses >= key.max_uses:
        raise HTTPException(status_code=403, detail="Key usage limit exceeded")

    # Log the validation attempt using KeyValidationAttempt
    attempt = KeyValidationAttempt(
        key=validation.key,
        hwid=validation.hwid,
        attempt_time=datetime.now(timezone.utc)
    )
    db.add(attempt)

    if key.hwid and key.hwid != validation.hwid:
        failed_attempts = crud.get_failed_attempts(db, validation.key, validation.hwid)
        if len(failed_attempts) >= 2:  # 3rd failed attempt
            crud.add_to_blacklist(db, validation.key, "Too many failed HWID attempts")
            raise HTTPException(status_code=403, detail="Key auto-blacklisted: Too many failed HWID attempts")
        raise HTTPException(status_code=400, detail=f"Invalid HWID (attempt {len(failed_attempts) + 1}/3)")

    key.hwid = validation.hwid
    key.current_uses += 1
    db.commit()
    return {"valid": True, "message": "Key validated successfully"}

@router.post("/{key}/reset-hwid")
def reset_hwid(key: str, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    if not key:
        raise HTTPException(status_code=404, detail="Key cannot be empty")
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    # Clear HWID logs from key_validation_attempts table
    db.execute(text("DELETE FROM key_validation_attempts WHERE key = :key"), {"key": key})
    db.commit()
    return {"message": f"HWID reset for key: {key}"}