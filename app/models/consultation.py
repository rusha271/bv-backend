from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class Consultation(Base):
    __tablename__ = "consultations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    consultation_type = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String, default="pending", nullable=False)  # pending, scheduled, completed, cancelled
    preferred_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="consultations")

class Consultant(Base):
    __tablename__ = "consultants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    expertise = Column(Text, nullable=False)  # JSON string of expertise list
    experience = Column(String, nullable=False)
    clients = Column(String, nullable=False)
    image_url = Column(String, nullable=False)
    video_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
