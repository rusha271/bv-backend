from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session, joinedload
from app.db.session import SessionLocal
from app.models.user import User
from app.schemas.user import UserRead, UserUpdate
from app.core.security import (
    get_current_user, require_role, rate_limit_dependency, 
    validate_input, validate_json_payload, security_validation_dependency
)

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

@router.get("/profile", response_model=UserRead)
def get_profile(
    request: Request,
    current_user=Depends(get_current_user), 
    db: Session = Depends(get_db),
    _: str = Depends(rate_limit_dependency("general")),
    __: bool = Depends(security_validation_dependency())
):
    """Get user profile - alternative endpoint with rate limiting and security"""
    user = db.query(User).options(joinedload(User.role_ref)).filter(User.id == int(current_user.sub)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/me", response_model=UserRead)
def update_my_profile(update: UserUpdate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).options(joinedload(User.role_ref)).filter(User.id == int(current_user.sub)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Handle the update data
    update_data = update.dict(exclude_unset=True)
    
    # Map 'name' to 'full_name' for frontend compatibility
    if 'name' in update_data:
        update_data['full_name'] = update_data.pop('name')
    
    # Update user fields
    for field, value in update_data.items():
        if hasattr(user, field):
            setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user

@router.put("/profile", response_model=UserRead)
def update_profile(
    update: UserUpdate, 
    request: Request,
    current_user=Depends(get_current_user), 
    db: Session = Depends(get_db),
    _: str = Depends(rate_limit_dependency("general")),
    __: bool = Depends(security_validation_dependency())
):
    """Update user profile - alternative endpoint with rate limiting and security"""
    user = db.query(User).options(joinedload(User.role_ref)).filter(User.id == int(current_user.sub)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Handle the update data
    update_data = update.dict(exclude_unset=True)
    
    # Validate and sanitize input data
    if 'email' in update_data:
        update_data['email'] = validate_input(update_data['email'], 'email', 'email')
    
    if 'full_name' in update_data:
        update_data['full_name'] = validate_input(update_data['full_name'], 'name', 'full name')
    
    if 'name' in update_data:
        update_data['full_name'] = validate_input(update_data.pop('name'), 'name', 'name')
    
    if 'phone' in update_data:
        update_data['phone'] = validate_input(update_data['phone'], 'phone', 'phone')
    
    # Update user fields
    for field, value in update_data.items():
        if hasattr(user, field):
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