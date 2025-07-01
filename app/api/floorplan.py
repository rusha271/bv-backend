from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.floorplan_analysis import FloorPlanAnalysis
from app.schemas.floorplan_analysis import FloorPlanAnalysisRead
from app.core.security import get_current_user
from app.services.floorplan_service import analyze_floorplan_stub

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/analyze/floorplan", response_model=FloorPlanAnalysisRead)
def analyze_floorplan(
    file_id: int,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    analysis = FloorPlanAnalysis(user_id=int(current_user.sub), file_id=file_id)
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