from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = "user"
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = None

class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[int] = None

class OAuthRequest(BaseModel):
    provider: str  # "google", "facebook", "apple"
    token: str

class OAuthUser(BaseModel):
    email: EmailStr
    full_name: str
    provider: str
    provider_id: str
    avatar_url: Optional[str] = None

class UserProfile(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
