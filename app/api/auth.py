from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.hashing import verify_password
from app.db.session import SessionLocal
from app.schemas.user import UserCreate, UserRead, Token, UserProfile, PasswordResetRequest, PasswordResetConfirm,LoginRequest
from app.models.user import User
from app.core.security import create_access_token, get_current_user, get_current_user_optional
from app.services.user_service import get_user_by_email, create_user
from app.services.guest_service import guest_service
from fastapi.security import OAuth2PasswordRequestForm
from typing import Dict, Any, Optional
import requests
from app.core import settings
from sqlalchemy.orm import joinedload

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/signup", response_model=UserRead)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    if get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    user = create_user(db, user_in)  # This must hash password before storing
    return user

# Define a response model for login
class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserRead
    is_guest: Optional[bool] = False

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    print(f"Login attempt for email: {request.email}")
    user = db.query(User).options(joinedload(User.role_ref)).filter(User.email == request.email).first()
    if not user:
        print("User not found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    if not verify_password(request.password, user.password_encrypted):
        print("Password verification failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    print("Login successful")
    print(f"DEBUG: User object: {user}")
    print(f"DEBUG: User role_ref: {user.role_ref}")
    print(f"DEBUG: User role_ref type: {type(user.role_ref)}")
    print(f"DEBUG: User role_ref name: {user.role_ref.name if user.role_ref else 'None'}")
    print(f"DEBUG: User role property: {user.role}")
    print(f"DEBUG: User role property type: {type(user.role)}")
    
    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role_ref.name}, expires_delta=access_token_expires
    )
    
    # Create a dict representation to debug
    user_dict = {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "phone": user.phone,
        "avatar_url": user.avatar_url,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "role": user.role_ref
    }
    print(f"DEBUG: User dict: {user_dict}")
    print(f"DEBUG: About to return response with user object")
    
    try:
        response_data = {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
        print(f"DEBUG: Response data created successfully")
        return response_data
    except Exception as e:
        print(f"ERROR: Exception occurred while creating response: {e}")
        print(f"ERROR: Exception type: {type(e)}")
        import traceback
        print(f"ERROR: Traceback: {traceback.format_exc()}")
        raise

@router.get("/me", response_model=UserProfile)
def get_me(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current user profile"""
    user = db.query(User).options(joinedload(User.role_ref)).filter(User.id == int(current_user.sub)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
@router.post("/logout")
def logout():
    """Logout endpoint (client should discard token)"""
    return {"message": "Successfully logged out"}

@router.post("/refresh", response_model=Token)
def refresh_token(current_user=Depends(get_current_user)):
    """Refresh access token"""
    token = create_access_token({"sub": current_user.sub, "role": current_user.role})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/forgot-password")
def forgot_password(request: PasswordResetRequest, db: Session = Depends(get_db)):
    """Request password reset"""
    user = get_user_by_email(db, request.email)
    if not user:
        # Don't reveal if email exists or not
        return {"message": "If the email exists, a password reset link has been sent"}
    
    # TODO: Implement email sending with reset token
    # For now, just return success message
    return {"message": "If the email exists, a password reset link has been sent"}

@router.post("/reset-password")
def reset_password(request: PasswordResetConfirm, db: Session = Depends(get_db)):
    """Reset password with token"""
    # TODO: Implement token verification
    # For now, just return success message
    return {"message": "Password reset successfully"}

@router.get("/check-auth")
def check_auth(current_user=Depends(get_current_user)):
    """Check if user is authenticated and return basic info"""
    return {
        "authenticated": True,
        "user_id": current_user.sub,
        "role": current_user.role
    }

@router.post("/guest/create", response_model=LoginResponse)
def create_guest_account(db: Session = Depends(get_db)):
    """Create a new guest account and return session"""
    try:
        # Create guest user
        guest_user = guest_service.create_guest_user(db)
        
        # Create session for guest
        session_data = guest_service.create_guest_session(db, guest_user)
        
        return session_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create guest account: {str(e)}")

@router.post("/guest/migrate", response_model=LoginResponse)
def migrate_guest_to_user(
    user_data: UserCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Migrate a guest account to a regular user account"""
    try:
        # Get current user from database
        user = db.query(User).options(joinedload(User.role_ref)).filter(User.id == int(current_user.sub)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if current user is a guest
        if not guest_service.is_guest_user(user):
            raise HTTPException(status_code=400, detail="Only guest users can migrate to regular accounts")
        
        # Check if email is already taken
        existing_user = get_user_by_email(db, user_data.email)
        if existing_user and existing_user.id != user.id:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Migrate guest to user
        migrated_user = guest_service.migrate_guest_to_user(db, user, user_data)
        
        # Create new session for migrated user
        access_token_expires = timedelta(minutes=60)
        access_token = create_access_token(
            data={"sub": str(migrated_user.id), "role": migrated_user.role_ref.name},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": migrated_user,
            "is_guest": False
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to migrate guest account: {str(e)}")

@router.get("/guest/check")
def check_guest_status(current_user=Depends(get_current_user_optional), db: Session = Depends(get_db)):
    """Check if current user is a guest user"""
    if not current_user:
        return {"is_guest": False, "authenticated": False}
    
    user = db.query(User).filter(User.id == int(current_user.sub)).first()
    if not user:
        return {"is_guest": False, "authenticated": False}
    
    is_guest = guest_service.is_guest_user(user)
    return {
        "is_guest": is_guest,
        "authenticated": True,
        "user_id": current_user.sub,
        "role": current_user.role
    }