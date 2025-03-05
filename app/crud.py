from sqlalchemy.orm import Session
from .schemas import User, Key, KeyValidation, Blacklist
from .models import User as UserModel, Key as KeyModel, KeyValidationAttempt, Blacklist as BlacklistModel
from .auth import get_password_hash

def get_db():
    from .database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user(db: Session, username: str):
    return db.query(UserModel).filter(UserModel.username == username).first()

def get_key(db: Session, key: str):
    return db.query(KeyModel).filter(KeyModel.key == key).first()

def get_all_keys(db: Session):
    return db.query(KeyModel).all()

def delete_key(db: Session, key: str):
    db_key = db.query(KeyModel).filter(KeyModel.key == key).first()
    if db_key:
        db.delete(db_key)
        db.commit()
    return db_key

def is_key_blacklisted(db: Session, key: str):
    return db.query(BlacklistModel).filter(BlacklistModel.key == key).first() is not None

def add_to_blacklist(db: Session, key: str, reason: str):
    blacklist = BlacklistModel(key=key, reason=reason)
    db.add(blacklist)
    db.commit()
    return blacklist

def remove_from_blacklist(db: Session, key: str):
    blacklist = db.query(BlacklistModel).filter(BlacklistModel.key == key).first()
    if blacklist:
        db.delete(blacklist)
        db.commit()
    return blacklist

def get_failed_attempts(db: Session, key: str, hwid: str):
    return db.query(KeyValidationAttempt).filter(
        KeyValidationAttempt.key == key,
        KeyValidationAttempt.hwid == hwid
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