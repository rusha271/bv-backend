from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class PageAccess(Base):
    __tablename__ = "page_access"
    
    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    page_name = Column(String(100), nullable=False)  # e.g., "dashboard", "analytics", "admin"
    can_access = Column(Boolean, default=True)
    can_read = Column(Boolean, default=True)
    can_write = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    role = relationship("Role", back_populates="page_access") 