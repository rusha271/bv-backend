from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, JSON, LargeBinary
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class FloorPlanAnalysis(Base):
    __tablename__ = "floorplan_analyses"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    image_data = Column(LargeBinary, nullable=False)
    original_image_url = Column(String(500), nullable=True)
    cropped_image_url = Column(String(500))
    analysis_result = Column(JSON)
    vastu_score = Column(Float)
    recommendations = Column(JSON)
    chakra_positions = Column(JSON)
    planet_influences = Column(JSON)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", back_populates="floorplan_analyses")
    file = relationship("File")  # Add relationship to File