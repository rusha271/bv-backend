from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON
from datetime import datetime
from app.db.base import Base

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    session_id = Column(String(255), unique=True, index=True, nullable=False)
    messages = Column(JSON, nullable=False, default=list)
    chat_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
