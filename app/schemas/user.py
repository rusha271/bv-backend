from pydantic    import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class RoleSchema(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = "user"
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = None

class UserRead(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    phone: Optional[str]
    avatar_url: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    role: RoleSchema  # Ensure role is included as a nested object

    class Config:
        from_attributes = True


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
    role: RoleSchema

    class Config:
        from_attributes = True

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class GuestMigrationRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
