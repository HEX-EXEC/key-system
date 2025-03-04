# app/models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)  # Ensure this matches the column name in the database
    role = Column(String, default="user")

class Key(Base):
    __tablename__ = "keys"
    key = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime)
    expires_at = Column(DateTime, nullable=True)
    max_uses = Column(Integer)
    current_uses = Column(Integer, default=0)
    hwid = Column(String, nullable=True)

class KeyValidationAttempt(Base):
    __tablename__ = "key_validation_attempts"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, ForeignKey("keys.key"))
    hwid = Column(String)
    attempt_time = Column(DateTime)

class Blacklist(Base):
    __tablename__ = "blacklist"
    key = Column(String, ForeignKey("keys.key"), primary_key=True)
    reason = Column(String)