from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class User(BaseModel):
    username: str
    role: str

class KeyCreate(BaseModel):
    expires_at: Optional[datetime] = None
    max_uses: Optional[int] = None

class Key(BaseModel):
    key: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    max_uses: Optional[int] = None
    current_uses: int
    hwid: Optional[str] = None

class KeyValidation(BaseModel):
    key: str
    hwid: str

class Blacklist(BaseModel):
    key: str
    reason: str

class BlacklistRemove(BaseModel):  # New schema for DELETE
    key: str