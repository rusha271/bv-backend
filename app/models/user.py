from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    password_hash = Column(String, nullable=True)
    oauth_provider = Column(String, nullable=True)
    oauth_id = Column(String, nullable=True)
    role = Column(String, default="user", nullable=False)
    avatar_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    files = relationship("File", back_populates="user")
    consultations = relationship("Consultation", back_populates="user")
