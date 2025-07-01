from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.chat import ChatSession
from app.core.security import require_role

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/chat-usage", dependencies=[Depends(require_role("admin"))])
def chat_usage(db: Session = Depends(get_db)):
    usage = db.query(ChatSession).all()
    return [{"user_id": s.user_id, "chat_count": s.chat_count} for s in usage] 