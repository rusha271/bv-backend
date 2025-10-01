from datetime import datetime
from pydantic import BaseModel, validator
from typing import Optional, List

# ---------------------- BOOK ----------------------
class BookBase(BaseModel):
    title: str
    author: str
    summary: str
    isbn: Optional[str] = None
    image_url: Optional[str] = None  # Keep for backward compatibility
    image_urls: Optional[List[str]] = None  # New field for multiple images
    pdf_url: Optional[str] = None  # Keep for backward compatibility
    pdf_urls: Optional[List[str]] = None  # New field for multiple PDFs
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
    image_url: Optional[str] = None  # Keep for backward compatibility
    image_urls: Optional[List[str]] = None  # New field for multiple images
    pdf_url: Optional[str] = None  # Keep for backward compatibility
    pdf_urls: Optional[List[str]] = None  # New field for multiple PDFs
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


# ---------------------- VIDEO ----------------------
class VideoBase(BaseModel):
    title: str
    description: str
    url: Optional[str] = None  # Keep for backward compatibility
    video_urls: Optional[List[str]] = None  # New field for multiple videos
    category: Optional[str] = None
    video_type: str = "blob"
    thumbnail_url: Optional[str] = None  # Keep for backward compatibility
    thumbnail_urls: Optional[List[str]] = None  # New field for multiple thumbnails
    duration: Optional[str] = None
    views: int = 0
    is_published: bool = True


# request model only for metadata (files are handled by UploadFile in routes)
class VideoCreate(VideoBase):
    pass


class VideoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    video_type: Optional[str] = None
    url: Optional[str] = None  # Keep for backward compatibility
    video_urls: Optional[List[str]] = None  # New field for multiple videos
    thumbnail_url: Optional[str] = None  # Keep for backward compatibility
    thumbnail_urls: Optional[List[str]] = None  # New field for multiple thumbnails
    duration: Optional[str] = None
    views: Optional[int] = None
    is_published: Optional[bool] = None


class VideoRead(VideoBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ---------------------- MEDIA ASSET ----------------------
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


# ---------------------- BLOG POST ----------------------
class BlogPostBase(BaseModel):
    title: str
    content: str
    published: Optional[bool] = False

class BlogPostCreate(BlogPostBase):
    pass

class BlogPostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    published: Optional[bool] = None

class BlogPostRead(BlogPostBase):
    id: int
    author_id: int
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        orm_mode = True


# ---------------------- VIDEO VIEW TRACKING ----------------------
class VideoViewTrackRequest(BaseModel):
    videoId: int
    watchTime: float
    duration: float
    percentage: float
    timestamp: int
    sessionId: str
    userAgent: Optional[str] = None
    referrer: Optional[str] = None

class VideoViewTrackResponse(BaseModel):
    success: bool
    message: str
    viewCount: int