from sqlalchemy import Column, Integer, ForeignKey, DateTime, JSON
from datetime import datetime
from app.db.base import Base

class FloorPlanAnalysis(Base):
    __tablename__ = "floorplan_analyses"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    result_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow) 