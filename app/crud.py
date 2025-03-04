# app/crud.py
from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime, timezone
from app.auth import get_password_hash  # Use absolute import instead of relative

def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_key(db: Session, key: str):
    return db.query(models.Key).filter(models.Key.key == key).first()

def get_all_keys(db: Session):
    return db.query(models.Key).all()

def delete_key(db: Session, key: str):
    db_key = db.query(models.Key).filter(models.Key.key == key).first()
    if db_key:
        db.delete(db_key)
        db.commit()
    return db_key

def is_key_blacklisted(db: Session, key: str):
    return db.query(models.Blacklist).filter(models.Blacklist.key == key).first() is not None

def add_to_blacklist(db: Session, key: str, reason: str):
    blacklist = models.Blacklist(key=key, reason=reason)
    db.add(blacklist)
    db.commit()
    return blacklist

def get_failed_attempts(db: Session, key: str, hwid: str):
    return db.query(models.KeyValidationAttempt).filter(
        models.KeyValidationAttempt.key == key,
        models.KeyValidationAttempt.hwid == hwid
    ).all()

def increment_key_use(db: Session, key: str, hwid: str, client_ip: str = None):
    db_key = get_key(db, key)
    if not db_key:
        return None
    db_key.current_uses += 1
    db_key.hwid = hwid
    db.commit()
    db.refresh(db_key)
    return db_key