from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime
from app.db.base import Base

class SiteSetting(Base):
    __tablename__ = "site_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), nullable=False, index=True)  # 'logo', 'tour_video', 'chakra_points'
    file_path = Column(String(500), nullable=False)  # Relative path like 'static/site_settings/logos/logo1.png'
    meta_data = Column(JSON, nullable=True)  # Store file name, version, uploader, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<SiteSetting(id={self.id}, category='{self.category}', file_path='{self.file_path}')>"
