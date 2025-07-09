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
import os
from datetime import datetime
from pydantic import BaseModel

router = APIRouter()

# TinyLlama model integration
class ChatRequest(BaseModel):
    prompt: str
    max_tokens: Optional[int] = 150
    temperature: Optional[float] = 0.7

class ChatResponseSimple(BaseModel):
    response: str
    model: str = "TinyLlama-1.1B-Chat"

# Global variable to store the model (loaded once)
llm_model = None

def load_tinyllama_model():
    """Load TinyLlama model using ctransformers"""
    global llm_model
    if llm_model is None:
        try:
            from ctransformers import AutoModelForCausalLM
            model_path = "models/tinyllama"
            
            # Check if model file exists
            if not os.path.exists(model_path):
                print(f"Warning: Model path {model_path} does not exist")
                return None
                
            llm_model = AutoModelForCausalLM.from_pretrained(
                model_path,
                model_type="llama",
                local_files_only=True,
                context_length=512
            )
            print("TinyLlama model loaded successfully")
        except Exception as e:
            print(f"Error loading TinyLlama model: {e}")
            return None
    return llm_model

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/simple", response_model=ChatResponseSimple)
def simple_chat_endpoint(request: ChatRequest):
    """Simple chat endpoint using TinyLlama model"""
    try:
        # Load model if not already loaded
        model = load_tinyllama_model()
        
        if model is None:
            # Fallback response if model is not available
            return ChatResponseSimple(
                response="I'm sorry, the AI model is currently unavailable. Please try again later.",
                model="fallback"
            )
        
        # Prepare the prompt for Vastu consultation
        system_prompt = "You are a helpful Vastu consultant. Provide brief, practical advice about Vastu Shastra principles. Keep responses concise and helpful."
        full_prompt = f"{system_prompt}\n\nUser: {request.prompt}\nAssistant:"
        
        # Generate response using TinyLlama
        response = model(
            full_prompt,
            max_new_tokens=request.max_tokens,
            temperature=request.temperature,
            stop=["User:", "\n\n"]
        )
        
        # Clean up the response
        cleaned_response = response.strip()
        if not cleaned_response:
            cleaned_response = "I'm here to help with Vastu questions. Could you please rephrase your question?"
        
        return ChatResponseSimple(
            response=cleaned_response,
            model="TinyLlama-1.1B-Chat"
        )
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return ChatResponseSimple(
            response="I'm sorry, I'm having trouble processing your request. Please try again.",
            model="error"
        )

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
        print(f"Chat endpoint error: {e}")
        # Return a graceful error response instead of raising exception
        return ChatResponse(
            response="I'm sorry, I'm experiencing technical difficulties. Please try again in a moment.",
            session_id=message.session_id or str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            mode="error"
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
