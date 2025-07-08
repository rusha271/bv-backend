from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import SessionLocal
from app.schemas.vastu import (
    PlanetaryDataCreate, PlanetaryDataRead, PlanetaryDataUpdate,
    VastuTipCreate, VastuTipRead, VastuTipUpdate,
    VastuCalculationCreate, VastuCalculationRead,
    VastuAnalysisResult, VastuAnalysisRequest
)
from app.core.security import get_current_user, get_current_admin_user
from app.services.vastu_service import (
    create_planetary_data, get_all_planetary_data, get_planetary_data_by_id,
    update_planetary_data, delete_planetary_data,
    create_vastu_tip, get_all_vastu_tips, get_vastu_tip_by_id,
    update_vastu_tip, delete_vastu_tip,
    create_vastu_calculation, calculate_vastu_analysis,
    get_vastu_remedies, get_zodiac_data
)

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Planetary Data endpoints
@router.post("/planetary-data", response_model=PlanetaryDataRead)
def create_planetary_data_endpoint(
    planetary_data: PlanetaryDataCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """Create planetary data (admin only)"""
    return create_planetary_data(db, planetary_data)

@router.get("/planetary-data", response_model=List[PlanetaryDataRead])
def get_planetary_data(
    db: Session = Depends(get_db)
):
    """Get all planetary data"""
    return get_all_planetary_data(db)

@router.get("/planetary-data/{planet_id}", response_model=PlanetaryDataRead)
def get_planetary_data_by_id_endpoint(
    planet_id: int,
    db: Session = Depends(get_db)
):
    """Get specific planetary data"""
    planetary_data = get_planetary_data_by_id(db, planet_id)
    if not planetary_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Planetary data not found"
        )
    return planetary_data

@router.put("/planetary-data/{planet_id}", response_model=PlanetaryDataRead)
def update_planetary_data_endpoint(
    planet_id: int,
    planetary_data_update: PlanetaryDataUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """Update planetary data (admin only)"""
    planetary_data = update_planetary_data(db, planet_id, planetary_data_update)
    if not planetary_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Planetary data not found"
        )
    return planetary_data

@router.delete("/planetary-data/{planet_id}")
def delete_planetary_data_endpoint(
    planet_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """Delete planetary data (admin only)"""
    success = delete_planetary_data(db, planet_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Planetary data not found"
        )
    return {"message": "Planetary data deleted successfully"}

# Vastu Tips endpoints
@router.post("/tips", response_model=VastuTipRead)
def create_vastu_tip_endpoint(
    tip: VastuTipCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """Create Vastu tip (admin only)"""
    return create_vastu_tip(db, tip)

@router.get("/tips", response_model=List[VastuTipRead])
def get_vastu_tips(
    category: Optional[str] = None,
    published_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get Vastu tips"""
    return get_all_vastu_tips(db, category, published_only)

@router.get("/tips/{tip_id}", response_model=VastuTipRead)
def get_vastu_tip(
    tip_id: int,
    db: Session = Depends(get_db)
):
    """Get specific Vastu tip"""
    tip = get_vastu_tip_by_id(db, tip_id)
    if not tip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vastu tip not found"
        )
    return tip

@router.put("/tips/{tip_id}", response_model=VastuTipRead)
def update_vastu_tip_endpoint(
    tip_id: int,
    tip_update: VastuTipUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """Update Vastu tip (admin only)"""
    tip = update_vastu_tip(db, tip_id, tip_update)
    if not tip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vastu tip not found"
        )
    return tip

@router.delete("/tips/{tip_id}")
def delete_vastu_tip_endpoint(
    tip_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """Delete Vastu tip (admin only)"""
    success = delete_vastu_tip(db, tip_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vastu tip not found"
        )
    return {"message": "Vastu tip deleted successfully"}

# Vastu Calculation endpoints
@router.post("/calculate", response_model=VastuAnalysisResult)
def calculate_vastu(
    analysis_request: VastuAnalysisRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Calculate Vastu analysis"""
    try:
        result = calculate_vastu_analysis(db, analysis_request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to calculate Vastu analysis: {str(e)}"
        )

@router.get("/remedies")
def get_vastu_remedies_endpoint(
    db: Session = Depends(get_db)
):
    """Get Vastu remedies"""
    return get_vastu_remedies(db)

@router.get("/zodiac-data")
def get_zodiac_data_endpoint(
    db: Session = Depends(get_db)
):
    """Get zodiac sign information"""
    return get_zodiac_data(db)

@router.get("/categories")
def get_vastu_categories(
    db: Session = Depends(get_db)
):
    """Get Vastu tip categories"""
    categories = db.query(VastuTip.category).distinct().all()
    return {"categories": [cat[0] for cat in categories]}
