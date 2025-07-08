from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class FloorPlanUpload(BaseModel):
    image_data: str  # Base64 encoded image
    image_format: str  # "png", "jpg", "jpeg"
    original_filename: str

class FloorPlanAnalysisBase(BaseModel):
    user_id: int
    file_id: int
    original_image_url: str
    cropped_image_url: Optional[str] = None
    analysis_result: Optional[Dict[str, Any]] = None
    vastu_score: Optional[float] = None
    recommendations: Optional[List[str]] = None
    chakra_positions: Optional[List[Dict[str, Any]]] = None
    planet_influences: Optional[List[Dict[str, Any]]] = None

class FloorPlanAnalysisCreate(FloorPlanAnalysisBase):
    pass

class FloorPlanAnalysisRead(FloorPlanAnalysisBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class FloorPlanAnalysisUpdate(BaseModel):
    analysis_result: Optional[Dict[str, Any]] = None
    vastu_score: Optional[float] = None
    recommendations: Optional[List[str]] = None
    chakra_positions: Optional[List[Dict[str, Any]]] = None
    planet_influences: Optional[List[Dict[str, Any]]] = None

class CropRequest(BaseModel):
    image_url: str
    crop_data: Dict[str, float]  # x, y, width, height

class VastuAnalysisResult(BaseModel):
    overall_score: float
    room_analysis: Dict[str, Any]
    direction_analysis: Dict[str, Any]
    recommendations: List[str]
    chakra_positions: List[Dict[str, Any]]
    planet_influences: List[Dict[str, Any]]
    id: int
    user_id: int
    created_at: Optional[str]

    class Config:
        orm_mode = True 