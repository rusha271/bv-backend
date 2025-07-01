from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.schemas.user import UserCreate, UserRead, Token, OAuthRequest
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token, get_current_user, verify_google_token
from app.services.user_service import get_user_by_email, create_user
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/signup", response_model=UserRead)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    user = create_user(db, user_in)
    return user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/oauth", response_model=Token)
def oauth_login(oauth: OAuthRequest, db: Session = Depends(get_db)):
    if oauth.provider == "google":
        user_info = verify_google_token(oauth.token)
        if not user_info or "email" not in user_info:
            raise HTTPException(status_code=400, detail="Invalid Google token")
        user = get_user_by_email(db, user_info["email"])
        if not user:
            user = create_user(db, UserCreate(email=user_info["email"], password="", full_name=user_info.get("name")))
        token = create_access_token({"sub": str(user.id), "role": user.role})
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="Unsupported OAuth provider")

@router.get("/me", response_model=UserRead)
def get_me(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == int(current_user.sub)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user 