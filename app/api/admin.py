from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File as FastAPIFile
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
from app.services.floorplan_service import analyze_floorplan_stub
from fastapi import BackgroundTasks
from datetime import datetime

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
    db: Session = Depends(get_db)
):
    """Get all chakra points (public access)"""
    return get_all_chakra_points(db)

@router.get("/chakra-points/{chakra_id}", response_model=ChakraPointRead)
def get_chakra_point_by_id_endpoint(
    chakra_id: str,
    db: Session = Depends(get_db)
):
    """Get specific chakra point (public access)"""
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
    db: Session = Depends(get_db)
):
    """Create new chakra point (public access)"""
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
    db: Session = Depends(get_db)
):
    """Update existing chakra point (public access)"""
    try:
        chakra_point = update_chakra_point(db, chakra_id, chakra_point_update)
        if not chakra_point:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chakra point not found"
            )
        
        # Return the complete updated chakra point data
        # The ChakraPointRead schema will automatically include all fields:
        # id, name, direction, description, remedies, is_auspicious, should_avoid, created_at, updated_at
        return chakra_point
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update chakra point: {str(e)}"
        )

@router.delete("/chakra-points/{chakra_id}")
def delete_chakra_point_endpoint(
    chakra_id: str,
    db: Session = Depends(get_db)
):
    """Delete chakra point (public access)"""
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

# Floorplan Analysis endpoint for admin
@router.post("/floorplan/{analysis_id}/analyze", response_model=FloorPlanAnalysisRead)
def analyze_floorplan_admin(
    analysis_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """Analyze floorplan (admin only)"""
    analysis = db.query(FloorPlanAnalysis).filter(FloorPlanAnalysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Floorplan analysis not found"
        )
    
    # Update analysis status to pending and trigger analysis
    analysis.status = "pending"
    analysis.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(analysis)
    
    # Start background analysis
    background_tasks.add_task(analyze_floorplan_stub, analysis.id, db)
    
    return FloorPlanAnalysisRead.from_orm(analysis)

# Logo/Image management endpoints for admin
@router.get("/get-image")
def get_logo_image(
    current_user = Depends(get_current_admin_user)
):
    """Get logo image (admin only)"""
    # This is a placeholder - you may need to implement actual logo retrieval
    # based on your site settings or file storage system
    return {"image_url": "/static/default-logo.png"}

@router.post("/upload-image")
def upload_logo_image(
    file: UploadFile = FastAPIFile(...),
    current_user = Depends(get_current_admin_user)
):
    """Upload logo image (admin only)"""
    # This is a placeholder - you may need to implement actual file upload
    # and storage logic based on your file handling system
    return {"image_url": f"/static/uploads/{file.filename}"}
