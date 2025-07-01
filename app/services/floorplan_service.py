from app.db.session import SessionLocal
from app.models.floorplan_analysis import FloorPlanAnalysis

def analyze_floorplan_stub(analysis_id: int, db_session=None):
    db = db_session or SessionLocal()
    analysis = db.query(FloorPlanAnalysis).filter(FloorPlanAnalysis.id == analysis_id).first()
    if analysis:
        # Simulate analysis result
        analysis.result_json = {"confidence": 0.99, "features": ["room", "door", "window"]}
        db.commit() 