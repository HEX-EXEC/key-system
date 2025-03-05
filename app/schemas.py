from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    role: str = "user"

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"

class User(UserBase):
    id: int
    hashed_password: str

    class Config:
        from_attributes = True

class KeyBase(BaseModel):
    key: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    max_uses: Optional[int] = None
    current_uses: int = 0
    hwid: Optional[str] = None

class KeyCreate(BaseModel):
    expires_at: Optional[datetime] = None
    max_uses: Optional[int] = None

class Key(KeyBase):
    class Config:
        from_attributes = True

class KeyValidation(BaseModel):
    key: str
    hwid: str

class BlacklistBase(BaseModel):
    key: str
    reason: str

class BlacklistCreate(BlacklistBase):
    pass

class Blacklist(BlacklistBase):
    class Config:
        from_attributes = True