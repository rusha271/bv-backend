from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.models.chat import ChatSession
from app.schemas.chat import ChatMessage, ChatResponse
from datetime import datetime
import uuid
import json

def create_chat_session(db: Session, user_id: Optional[int] = None) -> ChatSession:
    """Create a new chat session"""
    session_id = str(uuid.uuid4())
    db_session = ChatSession(
        user_id=user_id,
        session_id=session_id,
        messages=[],
        chat_count=0
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_chat_session(db: Session, session_id: str, user_id: Optional[int] = None) -> Optional[ChatSession]:
    """Get chat session by session_id"""
    query = db.query(ChatSession).filter(ChatSession.session_id == session_id)
    if user_id:
        query = query.filter(ChatSession.user_id == user_id)
    return query.first()

def send_chat_message(db: Session, message: ChatMessage, user_id: Optional[int] = None) -> ChatResponse:
    """Send a chat message and get AI response"""
    # Get or create session
    session = None
    if message.session_id:
        session = get_chat_session(db, message.session_id, user_id)
    
    if not session:
        session = create_chat_session(db, user_id)
    
    # Check chat limits
    if session.chat_count >= 100:
        raise Exception("Chat limit reached for this session")
    
    # Add user message to session
    user_message = {
        "role": "user",
        "content": message.message,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if session.messages is None:
        session.messages = []
    session.messages.append(user_message)
    
    # Generate AI response
    ai_response = chat_ai_stub(message.message, session.messages)
    
    # Add AI response to session
    assistant_message = {
        "role": "assistant",
        "content": ai_response,
        "timestamp": datetime.utcnow().isoformat()
    }
    session.messages.append(assistant_message)
    
    # Update session
    session.chat_count += 1
    db.commit()
    
    return ChatResponse(
        response=ai_response,
        session_id=session.session_id,
        timestamp=datetime.utcnow(),
        mode="ai"
    )

def get_chat_history(db: Session, session_id: Optional[str] = None, user_id: Optional[int] = None) -> List[dict]:
    """Get chat history for a session"""
    if session_id:
        session = get_chat_session(db, session_id, user_id)
        if session and session.messages:
            return session.messages
    else:
        # Get all sessions for user
        sessions = get_user_chat_sessions(db, user_id)
        all_messages = []
        for session in sessions:
            if session.messages:
                all_messages.extend(session.messages)
        return all_messages
    
    return []

def get_user_chat_sessions(db: Session, user_id: int) -> List[ChatSession]:
    """Get all chat sessions for a user"""
    return db.query(ChatSession).filter(ChatSession.user_id == user_id).all()

def delete_chat_session(db: Session, session_id: Optional[str] = None, user_id: Optional[int] = None) -> bool:
    """Delete chat session"""
    if session_id:
        session = get_chat_session(db, session_id, user_id)
        if session:
            db.delete(session)
            db.commit()
            return True
    else:
        # Delete all sessions for user
        sessions = get_user_chat_sessions(db, user_id)
        for session in sessions:
            db.delete(session)
        db.commit()
        return True
    
    return False

def chat_ai_stub(message: str, history: List[dict]) -> str:
    """Placeholder AI chat function"""
    # TODO: Implement actual AI logic here
    # For now, return a simple response based on the message
    responses = {
        "hello": "Hello! How can I help you with Vastu today?",
        "vastu": "Vastu Shastra is an ancient Indian system of architecture and design. How can I assist you?",
        "help": "I can help you with Vastu principles, floor plan analysis, and recommendations. What would you like to know?"
    }
    
    message_lower = message.lower()
    for key, response in responses.items():
        if key in message_lower:
            return response
    
    return f"Thank you for your message: '{message}'. I'm here to help with Vastu-related questions!"
