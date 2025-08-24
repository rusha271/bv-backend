from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.floorplan_analysis import FloorPlanAnalysis
from app.models.file import File  # Import the File model
from app.schemas.floorplan_analysis import FloorPlanAnalysisRead, FloorPlanUpload
from app.core.security import get_current_user, get_current_user_optional
from app.services.floorplan_service import analyze_floorplan_stub
import base64
from datetime import datetime
import os
import uuid

import logging
logger = logging.getLogger(__name__)

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload", response_model=FloorPlanAnalysisRead)
async def upload_floorplan(
    floorplan: FloorPlanUpload,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    try:
        # Decode base64 image
        try:
            image_data = base64.b64decode(floorplan.image_data.split(",")[1])
            logger.debug(f"Decoded image data, size: {len(image_data)} bytes")
        except Exception as e:
            logger.error(f"Invalid base64 image data: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Invalid base64 image data: {str(e)}")

        # Save file to disk
        file_extension = floorplan.image_format
        file_name = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join("uploads", file_name)
        os.makedirs("uploads", exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(image_data)

        # Create File record
        file_record = File(
            user_id=int(current_user.sub) if current_user else None,
            filename=floorplan.original_filename,
            content_type=f"image/{floorplan.image_format}",
            size=len(image_data),
            path=file_path,
            created_at=datetime.utcnow()
        )
        db.add(file_record)
        db.commit()
        db.refresh(file_record)
        logger.debug(f"Created File record with ID: {file_record.id}")

        # Create FloorPlanAnalysis record
        analysis = FloorPlanAnalysis(
            user_id=int(current_user.sub) if current_user else None,
            file_id=file_record.id,
            image_data=image_data,
            original_image_url=None,
            status="pending",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis, attribute_names=['file', 'user'])
        logger.debug(f"Created FloorPlanAnalysis record with ID: {analysis.id}")

        # Trigger background analysis
        background_tasks.add_task(analyze_floorplan_stub, analysis.id, db)

        # Explicitly use from_orm for serialization
        return FloorPlanAnalysisRead.from_orm(analysis)
    except Exception as e:
        logger.exception(f"Error uploading floorplan: {str(e)}")  # Use logger.exception for stack trace
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")

@router.post("/analyze/floorplan", response_model=FloorPlanAnalysisRead)
def analyze_floorplan(
    file_id: int,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify that file_id exists
    file_record = db.query(File).filter(File.id == file_id).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")

    analysis = FloorPlanAnalysis(
        user_id=int(current_user.sub),
        file_id=file_id,
        status="pending",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    background_tasks.add_task(analyze_floorplan_stub, analysis.id, db)
    return analysis

@router.get("/analysis/{analysis_id}", response_model=FloorPlanAnalysisRead)
def get_analysis(analysis_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    analysis = db.query(FloorPlanAnalysis).filter(FloorPlanAnalysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis