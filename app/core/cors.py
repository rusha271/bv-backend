from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

def setup_cors(app):
    # Production-ready CORS configuration
    allowed_origins = settings.FRONTEND_ORIGINS or []
    
    # Add production domains from environment if available
    if hasattr(settings, 'FRONTEND_URL') and settings.FRONTEND_URL:
        allowed_origins.append(settings.FRONTEND_URL.strip().rstrip("/"))

    print(">>> CORS Allowed Origins:", allowed_origins)  # Add for debug
    print(">>> CORS setup complete")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.FRONTEND_ORIGINS,
        allow_credentials=True,  # Enable for authentication
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Total-Count", "X-Page-Count"],
        max_age=3600,  # Cache preflight requests for 1 hour
    )
