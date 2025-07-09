from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime

class BookBase(BaseModel):
    title: str
    author: str
    summary: str
    isbn: Optional[str] = None
    image_url: Optional[str] = None
    image_alt: Optional[str] = None
    rating: float = 0.0
    pages: Optional[int] = None
    publication_year: Optional[int] = None
    publisher: Optional[str] = None
    price: Optional[float] = None
    is_available: bool = True
    is_published: bool = True

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    summary: Optional[str] = None
    isbn: Optional[str] = None
    image_url: Optional[str] = None
    image_alt: Optional[str] = None
    rating: Optional[float] = None
    pages: Optional[int] = None
    publication_year: Optional[int] = None
    publisher: Optional[str] = None
    price: Optional[float] = None
    is_available: Optional[bool] = None
    is_published: Optional[bool] = None

class BookRead(BookBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class VideoBase(BaseModel):
    title: str
    description: str
    url: str
    video_type: str = "youtube"
    youtube_id: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration: Optional[str] = None
    views: int = 0
    category: Optional[str] = None
    is_published: bool = True

class VideoCreate(VideoBase):
    @validator('url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v

class VideoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    video_type: Optional[str] = None
    youtube_id: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration: Optional[str] = None
    views: Optional[int] = None
    category: Optional[str] = None
    is_published: Optional[bool] = None

class VideoRead(VideoBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MediaAssetBase(BaseModel):
    filename: str
    original_name: str
    file_path: str
    file_size: int
    mime_type: str
    asset_type: str
    content_type: Optional[str] = None
    content_id: Optional[int] = None
    is_active: bool = True

class MediaAssetCreate(MediaAssetBase):
    pass

class MediaAssetUpdate(BaseModel):
    filename: Optional[str] = None
    original_name: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    asset_type: Optional[str] = None
    content_type: Optional[str] = None
    content_id: Optional[int] = None
    is_active: Optional[bool] = None

class MediaAssetRead(MediaAssetBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
