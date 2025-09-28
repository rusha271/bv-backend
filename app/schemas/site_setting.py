from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class SiteSettingCategory(str, Enum):
    LOGO = "logo"
    TOUR_VIDEO = "tour_video"
    CHAKRA_POINTS = "chakra_points"

class SiteSettingBase(BaseModel):
    category: SiteSettingCategory
    file_path: str = Field(..., description="Relative path to the file")
    meta_data: Optional[Dict[str, Any]] = Field(None, description="Additional metadata about the file")

class SiteSettingCreate(SiteSettingBase):
    pass

class SiteSettingUpdate(BaseModel):
    category: Optional[SiteSettingCategory] = None
    file_path: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None

class SiteSettingRead(SiteSettingBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class SiteSettingUpload(BaseModel):
    category: SiteSettingCategory
    file_name: Optional[str] = Field(None, description="Original file name")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    uploader: Optional[str] = Field(None, description="Who uploaded the file")
    version: Optional[str] = Field(None, description="Version of the file")
    description: Optional[str] = Field(None, description="Description of the file")

class SiteSettingResponse(BaseModel):
    success: bool
    message: str
    data: Optional[SiteSettingRead] = None
    file_url: Optional[str] = Field(None, description="Public URL to access the file")

class SiteSettingListResponse(BaseModel):
    success: bool
    message: str
    data: list[SiteSettingRead]
    total: int
    category: Optional[str] = None

class SiteSettingBulkLatestResponse(BaseModel):
    success: bool
    message: str
    data: Dict[str, Optional[SiteSettingRead]] = Field(..., description="Dictionary with category as key and latest setting as value")
    file_urls: Dict[str, Optional[str]] = Field(..., description="Dictionary with category as key and file URL as value")