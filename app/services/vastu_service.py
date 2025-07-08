from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.models.vastu import PlanetaryData, VastuTip, VastuCalculation
from app.schemas.vastu import (
    PlanetaryDataCreate, PlanetaryDataUpdate,
    VastuTipCreate, VastuTipUpdate,
    VastuAnalysisResult, VastuAnalysisRequest
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

# Vastu Tip Services
def create_vastu_tip(db: Session, tip: VastuTipCreate) -> VastuTip:
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
