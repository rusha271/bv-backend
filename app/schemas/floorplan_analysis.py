from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import base64

class FloorPlanUpload(BaseModel):
    image_data: str
    image_format: str
    original_filename: str

class FloorPlanAnalysisBase(BaseModel):
    user_id: Optional[int] = None
    file_id: int
    image_data: Optional[str] = None
    original_image_url: Optional[str] = None
    cropped_image_url: Optional[str] = None
    analysis_result: Optional[Dict[str, Any]] = None
    vastu_score: Optional[float] = None
    recommendations: Optional[List[str]] = None
    chakra_positions: Optional[List[Dict[str, Any]]] = None
    planet_influences: Optional[List[Dict[str, Any]]] = None
    status: Optional[str] = None

class FloorPlanAnalysisCreate(FloorPlanAnalysisBase):
    pass

class FloorPlanAnalysisRead(FloorPlanAnalysisBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        image_data_b64 = None
        if getattr(obj, 'image_data', None):
            try:
                image_data_b64 = base64.b64encode(obj.image_data).decode('utf-8')
                # Get image_format from File model
                image_format = 'jpeg'  # Default
                if hasattr(obj, 'file') and obj.file and hasattr(obj.file, 'content_type'):
                    image_format = obj.file.content_type.split('/')[-1]
                image_data_b64 = f"data:image/{image_format};base64,{image_data_b64}"
            except Exception as e:
                logger.error(f"Error encoding image_data to base64: {str(e)}")
                image_data_b64 = None
        return cls(
            id=obj.id,
            user_id=obj.user_id,
            file_id=obj.file_id,
            image_data=image_data_b64,
            original_image_url=obj.original_image_url,
            cropped_image_url=obj.cropped_image_url,
            analysis_result=obj.analysis_result,
            vastu_score=obj.vastu_score,
            recommendations=obj.recommendations,
            chakra_positions=obj.chakra_positions,
            planet_influences=obj.planet_influences,
            status=obj.status,
            created_at=obj.created_at,
            updated_at=obj.updated_at
        )
    
class FloorPlanAnalysisUpdate(BaseModel):
    analysis_result: Optional[Dict[str, Any]] = None
    vastu_score: Optional[float] = None
    recommendations: Optional[List[str]] = None
    chakra_positions: Optional[List[Dict[str, Any]]] = None
    planet_influences: Optional[List[Dict[str, Any]]] = None
    status: Optional[str] = None

class CropRequest(BaseModel):
    image_url: str
    crop_data: Dict[str, float]

class VastuAnalysisResult(BaseModel):
    overall_score: float
    room_analysis: Dict[str, Any]
    direction_analysis: Dict[str, Any]
    recommendations: List[str]
    chakra_positions: List[Dict[str, Any]]
    planet_influences: List[Dict[str, Any]]
    id: int
    user_id: Optional[int] = None
    created_at: Optional[str]

    class Config:
        from_attributes = True