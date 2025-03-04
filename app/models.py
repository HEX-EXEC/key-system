# app/models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean  # Add Boolean here
from sqlalchemy.orm import relationship
from .database import Base

class Key(Base):
    __tablename__ = "keys"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    created_at = Column(DateTime)
    expires_at = Column(DateTime, nullable=True)
    max_uses = Column(Integer, nullable=True)
    current_uses = Column(Integer, default=0)
    logs = relationship("Log", back_populates="key")

class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)
    key_id = Column(Integer, ForeignKey("keys.id"))
    hwid = Column(String)
    ip = Column(String)
    timestamp = Column(DateTime)
    success = Column(Boolean, default=True)  # New column: True for success, False for failure
    key = relationship("Key", back_populates="logs")

class Blacklist(Base):
    __tablename__ = "blacklist"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, index=True)
    reason = Column(String, nullable=True)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String)  # e.g., "admin" or "user"