from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.db.session import SessionLocal
from app.models.user import User
from app.schemas.user import UserRead, UserUpdate
from app.core.security import get_current_user, require_role

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/me", response_model=UserRead)
def get_my_profile(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).options(joinedload(User.role_ref)).filter(User.id == int(current_user.sub)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/me", response_model=UserRead)
def update_my_profile(update: UserUpdate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).options(joinedload(User.role_ref)).filter(User.id == int(current_user.sub)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for field, value in update.dict(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user

@router.get("/", response_model=list[UserRead], dependencies=[Depends(require_role("admin"))])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).options(joinedload(User.role_ref)).all()

@router.get("/{user_id}", response_model=UserRead, dependencies=[Depends(require_role("admin"))])
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).options(joinedload(User.role_ref)).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user 