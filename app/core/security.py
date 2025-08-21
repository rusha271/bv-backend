from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi import status
from app.core.config import settings
from app.schemas.user import TokenPayload
from app.db.session import SessionLocal
from app.models.user import User
from app.models.role import Role

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    # Fetch user to get ID and role
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == to_encode["sub"]).first()
        if user:
            to_encode["sub"] = str(user.id)  # Use user ID as sub
            if user.role_id:
                role = db.query(Role).filter(Role.id == user.role_id).first()
                to_encode["role"] = role.name if role else "user"
    finally:
        db.close()
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None

def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenPayload:
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return TokenPayload(**payload)

def get_current_admin_user(token: str = Depends(oauth2_scheme)) -> TokenPayload:
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if payload.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    return TokenPayload(**payload)

def require_role(role: str):
    def role_checker(user: TokenPayload = Depends(get_current_user)):
        if user.role != role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user
    return role_checker