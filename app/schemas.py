from datetime import datetime
from pydantic import BaseModel

class KeyCreate(BaseModel):
    max_uses: int
    expires_at: datetime

class KeyResponse(BaseModel):
    key: str
    created_at: datetime
    expires_at: datetime
    max_uses: int
    current_uses: int

    class Config:
        from_attributes = True

class BlacklistCreate(BaseModel):
    key: str
    reason: str

class BlacklistResponse(BaseModel):
    key: str
    reason: str

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    username: str
    password: str
    role: str

class UserResponse(BaseModel):
    username: str
    role: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class KeyValidate(BaseModel):  # Add this new model
    key: str
    hwid: str