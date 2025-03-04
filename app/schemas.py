# app/schemas.py
import random
import string
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

def generate_key():
    characters = string.ascii_letters + string.digits + "_"
    return "".join(random.choice(characters) for _ in range(43))

class KeyBase(BaseModel):
    key: Optional[str] = None
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    max_uses: Optional[int] = None
    current_uses: Optional[int] = 0
    hwid: Optional[str] = None

class KeyCreate(KeyBase):
    expires_at: datetime
    max_uses: int
    hwid: str

class KeyResponse(KeyBase):
    key: str
    created_at: datetime

    class Config:
        from_attributes = True

class KeyValidate(BaseModel):
    key: str
    hwid: str

class BlacklistBase(BaseModel):
    key: Optional[str] = None
    reason: Optional[str] = None

class BlacklistCreate(BlacklistBase):
    key: str
    reason: str

class Blacklist(BlacklistBase):
    key: str
    reason: str

    class Config:
        from_attributes = True

class BlacklistDelete(BaseModel):  # Add this new class
    key: str

class UserBase(BaseModel):
    username: str
    role: str = "user"

class UserCreate(UserBase):
    hashed_password: str

class User(UserBase):
    hashed_password: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None