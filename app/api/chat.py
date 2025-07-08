from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import SessionLocal
from app.models.chat import ChatSession
from app.schemas.chat import ChatMessage, ChatSessionRead, ChatResponse
from app.core.security import get_current_user
from app.services.chat_service import (
    send_chat_message, get_chat_history, create_chat_session,
    get_user_chat_sessions, delete_chat_session
)
import uuid

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ChatResponse)
def chat_endpoint(
    message: ChatMessage,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Send a chat message"""
    try:
        user_id = int(current_user.sub) if current_user else None
        response = send_chat_message(db, message, user_id)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to send message: {str(e)}"
        )

@router.get("/history", response_model=List[dict])
def get_chat_history_endpoint(
    session_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get chat history for a session"""
    user_id = int(current_user.sub) if current_user else None
    return get_chat_history(db, session_id, user_id)

@router.delete("/history")
def clear_chat_history(
    session_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Clear chat history"""
    user_id = int(current_user.sub) if current_user else None
    success = delete_chat_session(db, session_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    return {"message": "Chat history cleared successfully"}

@router.get("/sessions", response_model=List[ChatSessionRead])
def get_user_sessions(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get user's chat sessions"""
    user_id = int(current_user.sub)
    return get_user_chat_sessions(db, user_id)

@router.get("/health")
def chat_health():
    """Chat service health check"""
    return {"status": "healthy", "service": "chat"}

@router.get("/status")
def chat_status():
    """Legacy endpoint for compatibility"""
    return {"status": "ok"}
