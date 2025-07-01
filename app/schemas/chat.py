from pydantic import BaseModel
from typing import Optional, List

class ChatSessionBase(BaseModel):
    chat_count: int

class ChatSessionRead(ChatSessionBase):
    id: int
    user_id: int
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        orm_mode = True

class ChatMessage(BaseModel):
    session_id: Optional[int]
    message: str
    history: Optional[List[str]] = None 