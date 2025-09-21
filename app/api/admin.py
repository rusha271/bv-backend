from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import SessionLocal
from app.schemas.vastu import (
    ChakraPointCreate, ChakraPointRead, ChakraPointUpdate
)
from app.schemas.floorplan_analysis import FloorPlanAnalysisRead
from app.models.floorplan_analysis import FloorPlanAnalysis
from app.core.security import get_current_admin_user
from app.services.vastu_service import (
    create_chakra_point, get_all_chakra_points, get_chakra_point_by_id,
    update_chakra_point, delete_chakra_point
)

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ChakraPoint endpoints for admin
@router.get("/chakra-points", response_model=List[ChakraPointRead])
def get_all_chakra_points_endpoint(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """Get all chakra points (admin only)"""
    return get_all_chakra_points(db)

@router.get("/chakra-points/{chakra_id}", response_model=ChakraPointRead)
def get_chakra_point_by_id_endpoint(
    chakra_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """Get specific chakra point (admin only)"""
    chakra_point = get_chakra_point_by_id(db, chakra_id)
    if not chakra_point:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chakra point not found"
        )
    return chakra_point

@router.post("/chakra-points", response_model=ChakraPointRead, status_code=status.HTTP_201_CREATED)
def create_chakra_point_endpoint(
    chakra_point: ChakraPointCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """Create new chakra point (admin only)"""
    try:
        return create_chakra_point(db, chakra_point)
    except HTTPException as e:
        if e.status_code == 409:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Chakra point with this ID already exists"
            )
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create chakra point: {str(e)}"
        )

@router.put("/chakra-points/{chakra_id}", response_model=ChakraPointRead)
def update_chakra_point_endpoint(
    chakra_id: str,
    chakra_point_update: ChakraPointUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """Update existing chakra point (admin only)"""
    chakra_point = update_chakra_point(db, chakra_id, chakra_point_update)
    if not chakra_point:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chakra point not found"
        )
    return chakra_point

@router.delete("/chakra-points/{chakra_id}")
def delete_chakra_point_endpoint(
    chakra_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """Delete chakra point (admin only)"""
    success = delete_chakra_point(db, chakra_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chakra point not found"
        )
    return {"message": "Chakra point deleted successfully"}

# Floorplan Analysis endpoints for admin
@router.get("/floorplan-analyses", response_model=List[FloorPlanAnalysisRead])
def get_all_floorplan_analyses(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """Get all floorplan analyses (admin only)"""
    analyses = db.query(FloorPlanAnalysis).order_by(FloorPlanAnalysis.created_at.desc()).all()
    return [FloorPlanAnalysisRead.from_orm(analysis) for analysis in analyses]

@router.get("/floorplan-analyses/{analysis_id}", response_model=FloorPlanAnalysisRead)
def get_floorplan_analysis_by_id(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """Get specific floorplan analysis by ID (admin only)"""
    analysis = db.query(FloorPlanAnalysis).filter(FloorPlanAnalysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Floorplan analysis not found"
        )
    return FloorPlanAnalysisRead.from_orm(analysis)

@router.get("/floorplan-analyses/user/{user_id}", response_model=List[FloorPlanAnalysisRead])
def get_floorplan_analyses_by_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """Get all floorplan analyses for a specific user (admin only)"""
    analyses = db.query(FloorPlanAnalysis).filter(
        FloorPlanAnalysis.user_id == user_id
    ).order_by(FloorPlanAnalysis.created_at.desc()).all()
    return [FloorPlanAnalysisRead.from_orm(analysis) for analysis in analyses]

@router.delete("/floorplan-analyses/{analysis_id}")
def delete_floorplan_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """Delete floorplan analysis (admin only)"""
    analysis = db.query(FloorPlanAnalysis).filter(FloorPlanAnalysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Floorplan analysis not found"
        )
    
    db.delete(analysis)
    db.commit()
    return {"message": "Floorplan analysis deleted successfully"}
