from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.chat import ChatSession
from app.schemas.chat import ChatMessage
from app.core.security import get_current_user
from app.services.chat_service import chat_ai_stub

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=dict)
def chat_endpoint(
    message: ChatMessage,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Track chat usage
    session = db.query(ChatSession).filter(ChatSession.user_id == int(current_user.sub)).first()
    if not session:
        session = ChatSession(user_id=int(current_user.sub), chat_count=0)
        db.add(session)
    if session.chat_count >= 100:
        raise HTTPException(status_code=429, detail="Chat limit reached for this session.")
    session.chat_count += 1
    db.commit()
    response = chat_ai_stub(message.message, message.history)
    return {"response": response}

@router.get("/status")
def chat_status():
    return {"status": "ok"} 