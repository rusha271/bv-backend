from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ChatSessionBase(BaseModel):
    session_id: str
    chat_count: int
    messages: List[Dict[str, Any]] = []

class ChatSessionRead(ChatSessionBase):
    id: int
    user_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ChatMessage(BaseModel):
    session_id: Optional[str] = None
    message: str
    history: Optional[List[Dict[str, Any]]] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: datetime
    mode: str = "ai"  # "ai" or "fallback"

class ChatHistoryMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
