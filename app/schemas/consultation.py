from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class ConsultationBase(BaseModel):
    name: str
    email: EmailStr
    phone: str
    consultation_type: str
    message: str
    preferred_date: Optional[datetime] = None

class ConsultationCreate(ConsultationBase):
    pass

class ConsultationUpdate(BaseModel):
    status: Optional[str] = None
    preferred_date: Optional[datetime] = None

class ConsultationRead(ConsultationBase):
    id: int
    user_id: Optional[int] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ConsultantBase(BaseModel):
    name: str
    title: str
    description: str
    expertise: List[str]
    experience: str
    clients: str
    image_url: str
    video_url: Optional[str] = None
    is_active: bool = True

class ConsultantCreate(ConsultantBase):
    pass

class ConsultantUpdate(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    expertise: Optional[List[str]] = None
    experience: Optional[str] = None
    clients: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    is_active: Optional[bool] = None

class ConsultantRead(ConsultantBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
