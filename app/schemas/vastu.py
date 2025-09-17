from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class PlanetaryDataBase(BaseModel):
    name: str
    radius: float
    distance: float
    orbital_period: float
    color: int
    description: str
    facts: str
    mean_longitude: float
    daily_motion: float
    eccentricity: float
    inclination: float
    remedy: str

class PlanetaryDataCreate(PlanetaryDataBase):
    pass

class PlanetaryDataUpdate(BaseModel):
    name: Optional[str] = None
    radius: Optional[float] = None
    distance: Optional[float] = None
    orbital_period: Optional[float] = None
    color: Optional[int] = None
    description: Optional[str] = None
    facts: Optional[str] = None
    mean_longitude: Optional[float] = None
    daily_motion: Optional[float] = None
    eccentricity: Optional[float] = None
    inclination: Optional[float] = None
    remedy: Optional[str] = None

class PlanetaryDataRead(PlanetaryDataBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class VastuTipBase(BaseModel):
    title: str
    description: str
    details: str
    category: str
    image_url: str
    is_published: bool = True

class VastuTipCreate(BaseModel):
    title: str
    description: str
    image_url: str
    details: Optional[str] = None
    category: Optional[str] = "general"
    is_published: bool = True
    # author_id: Optional[int] = None

class VastuTipUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    details: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    is_published: Optional[bool] = None

class VastuTipRead(VastuTipBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class VastuCalculationBase(BaseModel):
    location_data: Dict[str, float]  # {"lat": float, "lng": float}
    calculation_date: datetime
    planetary_positions: List[Dict[str, Any]]
    vastu_recommendations: List[str]
    chakra_alignment: Dict[str, Any]

class VastuCalculationCreate(VastuCalculationBase):
    pass

class VastuCalculationRead(VastuCalculationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class VastuAnalysisResult(BaseModel):
    overall_score: float
    room_analysis: Dict[str, Any]
    direction_analysis: Dict[str, Any]
    recommendations: List[str]
    chakra_positions: List[Dict[str, Any]]
    planet_influences: List[Dict[str, Any]]

class VastuAnalysisRequest(BaseModel):
    location: Dict[str, float]
    date_time: datetime
    floor_plan_data: Optional[Dict[str, Any]] = None

# ChakraPoint Schemas
class ChakraPointBase(BaseModel):
    id: str
    name: str
    direction: str
    description: str
    remedies: str
    is_auspicious: bool = True
    should_avoid: bool = False

class ChakraPointCreate(ChakraPointBase):
    pass

class ChakraPointUpdate(BaseModel):
    name: Optional[str] = None
    direction: Optional[str] = None
    description: Optional[str] = None
    remedies: Optional[str] = None
    is_auspicious: Optional[bool] = None
    should_avoid: Optional[bool] = None

class ChakraPointRead(ChakraPointBase):
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True