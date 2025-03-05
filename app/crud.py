from sqlalchemy.orm import Session
from app.models import Key as KeyModel, Blacklist, KeyValidationAttempt  # Absolute import

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

def get_failed_attempts(db: Session, key: str, hwid: str):
    return db.query(KeyValidationAttempt).filter(KeyValidationAttempt.key == key, KeyValidationAttempt.hwid == hwid).all()

def is_key_blacklisted(db: Session, key: str):
    return db.query(Blacklist).filter(Blacklist.key == key).first() is not None

def add_to_blacklist(db: Session, key: str, reason: str):
    from datetime import datetime, timezone
    db_blacklist = Blacklist(
        key=key,
        reason=reason,
        blacklisted_at=datetime.now(timezone.utc)
    )
    db.add(db_blacklist)
    db.commit()
    db.refresh(db_blacklist)
    return db_blacklist

def remove_from_blacklist(db: Session, key: str):
    db_blacklist = db.query(Blacklist).filter(Blacklist.key == key).first()
    if db_blacklist:
        db.delete(db_blacklist)
        db.commit()