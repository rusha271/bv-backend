from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from fastapi import status
from app.core.config import settings
from app.schemas.user import TokenPayload
from app.db.session import SessionLocal
from app.models.user import User
from app.models.role import Role
import time
import re
from collections import defaultdict
import logging

# OAuth2 scheme for required authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
# HTTPBearer for optional authentication
oauth2_scheme_optional = HTTPBearer(auto_error=False)

# Rate limiting configuration
RATE_LIMIT_WINDOW = 60  # 60 seconds
RATE_LIMIT_MAX_REQUESTS = 100  # Max 100 requests per minute for general endpoints
RATE_LIMIT_AUTH_MAX_REQUESTS = 10  # Max 10 requests per minute for auth endpoints
RATE_LIMIT_ADMIN_MAX_REQUESTS = 200  # Max 200 requests per minute for admin endpoints

# Rate limiting storage
request_times = defaultdict(list)
auth_request_times = defaultdict(list)
admin_request_times = defaultdict(list)

# Security patterns for validation
SECURITY_PATTERNS = {
    'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    'phone': r'^\+?[\d\s\-\(\)]{10,15}$',
    'name': r'^[a-zA-Z\s\u00C0-\u017F\u0100-\u017F\u0180-\u024F\u1E00-\u1EFF]{2,50}$',  # Unicode support for names
    'password': r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',
    'username': r'^[a-zA-Z0-9_]{3,30}$',
    'chakra_id': r'^[A-Z]\d+$',  # E1, N2, etc.
    'safe_text': r'^[a-zA-Z0-9\s\-_.,!?@#$%^&*()+=\[\]{}|\\:";\'<>?/~`]{1,1000}$',
    'url': r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
}

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    
    # If data already contains sub and role, use them directly (for guest users)
    if "sub" in data and "role" in data:
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt
    
    # Fetch user to get ID and role (for regular users)
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

def get_current_user_optional(token: Optional[HTTPAuthorizationCredentials] = Depends(oauth2_scheme_optional)) -> Optional[TokenPayload]:
    """Get current user if token is provided, otherwise return None"""
    if not token:
        return None
    
    # Extract the token string from HTTPAuthorizationCredentials
    payload = decode_access_token(token.credentials)
    if not payload:
        return None
    
    try:
        return TokenPayload(**payload)
    except Exception:
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

# Rate limiting functions
def get_client_ip(request: Request) -> str:
    """Extract client IP address from request"""
    # Check for forwarded headers first (for reverse proxies)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to direct connection
    if hasattr(request.client, 'host'):
        return request.client.host
    
    return "unknown"

def check_rate_limit(client_ip: str, endpoint_type: str = "general") -> None:
    """Check rate limit for client IP based on endpoint type"""
    current_time = time.time()
    
    # Choose the appropriate rate limit storage and limits
    if endpoint_type == "auth":
        storage = auth_request_times
        max_requests = RATE_LIMIT_AUTH_MAX_REQUESTS
    elif endpoint_type == "admin":
        storage = admin_request_times
        max_requests = RATE_LIMIT_ADMIN_MAX_REQUESTS
    else:
        storage = request_times
        max_requests = RATE_LIMIT_MAX_REQUESTS
    
    # Clean old requests
    storage[client_ip] = [t for t in storage[client_ip] if current_time - t < RATE_LIMIT_WINDOW]
    
    # Check if too many requests
    if len(storage[client_ip]) >= max_requests:
        logging.warning(f"Rate limit exceeded for IP: {client_ip} on {endpoint_type} endpoint")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many requests. Please wait {RATE_LIMIT_WINDOW} seconds before making more requests."
        )
    
    # Add current request
    storage[client_ip].append(current_time)

def rate_limit_dependency(endpoint_type: str = "general"):
    """Dependency for rate limiting"""
    def rate_limiter(request: Request):
        client_ip = get_client_ip(request)
        check_rate_limit(client_ip, endpoint_type)
        return client_ip
    return rate_limiter

# Security validation functions
def validate_input(data: Any, field_type: str, field_name: str = "field") -> Any:
    """Validate input data against security patterns"""
    if data is None:
        return data
    
    # Convert to string for validation
    data_str = str(data).strip()
    
    # Check if pattern exists
    if field_type not in SECURITY_PATTERNS:
        logging.warning(f"Unknown field type for validation: {field_type}")
        return data
    
    # Validate against pattern
    pattern = SECURITY_PATTERNS[field_type]
    if not re.match(pattern, data_str):
        logging.warning(f"Invalid {field_name} format: {data_str[:50]}...")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {field_name} format. Please check your input."
        )
    
    return data

def sanitize_input(data: str) -> str:
    """Sanitize input data to prevent injection attacks"""
    if not isinstance(data, str):
        return data
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '|', '`', '$']
    for char in dangerous_chars:
        data = data.replace(char, '')
    
    # Limit length
    if len(data) > 1000:
        data = data[:1000]
    
    return data.strip()

def validate_json_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and sanitize JSON payload"""
    if not isinstance(payload, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload format. Expected JSON object."
        )
    
    # Check payload size
    payload_str = str(payload)
    if len(payload_str) > 10000:  # 10KB limit
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Payload too large. Maximum size is 10KB."
        )
    
    # Sanitize string values
    for key, value in payload.items():
        if isinstance(value, str):
            payload[key] = sanitize_input(value)
    
    return payload

def security_validation_dependency():
    """Dependency for security validation"""
    def validator(request: Request):
        # Log request for security monitoring
        client_ip = get_client_ip(request)
        logging.info(f"Request from {client_ip}: {request.method} {request.url.path}")
        
        # Check for suspicious patterns in headers
        user_agent = request.headers.get("User-Agent", "")
        if len(user_agent) > 500:  # Suspiciously long user agent
            logging.warning(f"Suspicious User-Agent from {client_ip}: {user_agent[:100]}...")
        
        return True
    return validator