from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON
from datetime import datetime
from app.db.base import Base

class FloorPlanAnalysis(Base):
    __tablename__ = "floorplan_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    original_image_url = Column(String(500), nullable=False)
    cropped_image_url = Column(String(500), nullable=True)
    analysis_result = Column(JSON, nullable=True)
    vastu_score = Column(Float, nullable=True)
    recommendations = Column(JSON, nullable=True)
    chakra_positions = Column(JSON, nullable=True)
    planet_influences = Column(JSON, nullable=True)
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
