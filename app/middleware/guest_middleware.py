from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.services.guest_service import guest_service
from app.db.session import SessionLocal
from app.core.security import create_access_token
from datetime import timedelta
import json

class GuestMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, auto_guest_endpoints=None):
        super().__init__(app)
        # Endpoints that should automatically create guest accounts
        self.auto_guest_endpoints = auto_guest_endpoints or [
            "/api/floorplan/upload",
            "/api/chat/send",
            "/api/vastu/consultation",
            "/api/analytics/track"
        ]
    
    async def dispatch(self, request: Request, call_next):
        # Check if this endpoint should auto-create guest accounts
        should_create_guest = any(request.url.path.startswith(endpoint) for endpoint in self.auto_guest_endpoints)
        
        if should_create_guest:
            # Check if user is already authenticated
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                # No valid token, create guest account
                db = SessionLocal()
                try:
                    guest_user = guest_service.create_guest_user(db)
                    session_data = guest_service.create_guest_session(db, guest_user)
                    
                    # Add guest token to request headers
                    request.headers.__dict__["_list"].append(
                        (b"x-guest-token", session_data["access_token"].encode())
                    )
                    request.headers.__dict__["_list"].append(
                        (b"x-guest-user-id", str(guest_user.id).encode())
                    )
                finally:
                    db.close()
        
        response = await call_next(request)
        return response
