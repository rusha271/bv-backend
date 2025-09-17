from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.models.blog import VastuTip
from app.models.vastu import PlanetaryData, VastuCalculation, ChakraPoint
from app.schemas.vastu import (
    PlanetaryDataCreate, PlanetaryDataUpdate,
    VastuTipCreate, VastuTipUpdate,
    VastuAnalysisResult, VastuAnalysisRequest,
    ChakraPointCreate, ChakraPointUpdate
)

# Planetary Data Services
def create_planetary_data(db: Session, planetary_data: PlanetaryDataCreate) -> PlanetaryData:
    db_planetary = PlanetaryData(**planetary_data.dict())
    db.add(db_planetary)
    db.commit()
    db.refresh(db_planetary)
    return db_planetary

def get_planetary_data_by_id(db: Session, planet_id: int) -> Optional[PlanetaryData]:
    return db.query(PlanetaryData).filter(PlanetaryData.id == planet_id).first()

def get_all_planetary_data(db: Session) -> List[PlanetaryData]:
    return db.query(PlanetaryData).all()

def update_planetary_data(db: Session, planet_id: int, planetary_data_update: PlanetaryDataUpdate) -> Optional[PlanetaryData]:
    db_planetary = db.query(PlanetaryData).filter(PlanetaryData.id == planet_id).first()
    if not db_planetary:
        return None

    update_data = planetary_data_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_planetary, field, value)

    db.commit()
    db.refresh(db_planetary)
    return db_planetary

def delete_planetary_data(db: Session, planet_id: int) -> bool:
    db_planetary = db.query(PlanetaryData).filter(PlanetaryData.id == planet_id).first()
    if not db_planetary:
        return False

    db.delete(db_planetary)
    db.commit()
    return True

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Vastu Tip Services
def create_vastu_tip(db: Session, tip: VastuTipCreate, current_user) -> VastuTip:
    logger.info(f"Received tip data: {tip.dict()}")
    # Check for required fields (custom validation for debugging)
    required_fields = {"title", "description", "image_url"}  # Adjust based on schema
    missing_fields = [field for field in required_fields if not getattr(tip, field, None)]
    if missing_fields:
        raise HTTPException(status_code=400, detail=f"Missing required fields: {', '.join(missing_fields)}")
    
    db_tip = VastuTip(**tip.dict())
    db.add(db_tip)
    db.commit()
    db.refresh(db_tip)
    return db_tip

def get_vastu_tip_by_id(db: Session, tip_id: int) -> Optional[VastuTip]:
    return db.query(VastuTip).filter(VastuTip.id == tip_id).first()

def get_all_vastu_tips(db: Session, category: Optional[str] = None, published_only: bool = True) -> List[VastuTip]:
    query = db.query(VastuTip)
    if category:
        query = query.filter(VastuTip.category.ilike(f"%{category}%"))
    if published_only:
        query = query.filter(VastuTip.is_published == True)
    return query.all()

def update_vastu_tip(db: Session, tip_id: int, tip_update: VastuTipUpdate) -> Optional[VastuTip]:
    db_tip = db.query(VastuTip).filter(VastuTip.id == tip_id).first()
    if not db_tip:
        return None

    update_data = tip_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_tip, field, value)

    db.commit()
    db.refresh(db_tip)
    return db_tip

def delete_vastu_tip(db: Session, tip_id: int) -> bool:
    db_tip = db.query(VastuTip).filter(VastuTip.id == tip_id).first()
    if not db_tip:
        return False

    db.delete(db_tip)
    db.commit()
    return True

# Vastu Calculation Services
def create_vastu_calculation(db: Session, calculation: VastuCalculation) -> VastuCalculation:
    db_calculation = VastuCalculation(**calculation.dict())
    db.add(db_calculation)
    db.commit()
    db.refresh(db_calculation)
    return db_calculation

def calculate_vastu_analysis(db: Session, request: VastuAnalysisRequest) -> VastuAnalysisResult:
    # Placeholder implementation, should be replaced by actual Vastu analysis logic
    return VastuAnalysisResult(
        overall_score=85.0,
        room_analysis={"Living Room": "Good", "Kitchen": "Average"},
        direction_analysis={"North": "Strong", "East": "Weak"},
        recommendations=["Improve lighting in the south", "Reinforce east wall"],
        chakra_positions=[{"name": "Root Chakra", "position": "center"}],
        planet_influences=[{"name": "Mars", "influence": "moderate"}]
    )

def get_vastu_remedies(db: Session) -> List[str]:
    # Placeholder implementation
    return ["Keep a water fountain", "Place a plant in the east"]

def get_zodiac_data(db: Session) -> Dict[str, Any]:
    # Placeholder implementation
    return {
        "Aries": {"element": "Fire", "compatible": ["Leo", "Sagittarius"]},
        "Taurus": {"element": "Earth", "compatible": ["Virgo", "Capricorn"]}
    }

# ChakraPoint Services
def create_chakra_point(db: Session, chakra_point: ChakraPointCreate) -> ChakraPoint:
    # Check if chakra point with this ID already exists
    existing = db.query(ChakraPoint).filter(ChakraPoint.id == chakra_point.id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Chakra point with this ID already exists")
    
    db_chakra_point = ChakraPoint(**chakra_point.dict())
    db.add(db_chakra_point)
    db.commit()
    db.refresh(db_chakra_point)
    return db_chakra_point

def get_chakra_point_by_id(db: Session, chakra_id: str) -> Optional[ChakraPoint]:
    return db.query(ChakraPoint).filter(ChakraPoint.id == chakra_id).first()

def get_all_chakra_points(db: Session) -> List[ChakraPoint]:
    return db.query(ChakraPoint).all()

def update_chakra_point(db: Session, chakra_id: str, chakra_point_update: ChakraPointUpdate) -> Optional[ChakraPoint]:
    db_chakra_point = db.query(ChakraPoint).filter(ChakraPoint.id == chakra_id).first()
    if not db_chakra_point:
        return None

    update_data = chakra_point_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_chakra_point, field, value)

    db.commit()
    db.refresh(db_chakra_point)
    return db_chakra_point

def delete_chakra_point(db: Session, chakra_id: str) -> bool:
    db_chakra_point = db.query(ChakraPoint).filter(ChakraPoint.id == chakra_id).first()
    if not db_chakra_point:
        return False

    db.delete(db_chakra_point)
    db.commit()
    return True
