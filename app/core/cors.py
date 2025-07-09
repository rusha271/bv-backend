from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

def setup_cors(app):
    # Production-ready CORS configuration
    allowed_origins = [
        "http://localhost:3000",  # React development server
        "http://localhost:3001",  # Alternative React port
        "https://youtu.be",       # YouTube shortened URLs
        "https://www.youtube.com", # YouTube full URLs
        "https://youtube.com",    # YouTube without www
        "https://via.placeholder.com", # Placeholder images
    ]
    
    # Add production domains from environment if available
    if hasattr(settings, 'FRONTEND_URL') and settings.FRONTEND_URL:
        allowed_origins.append(settings.FRONTEND_URL)
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,  # Enable for authentication
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=[
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "Origin",
            "X-CSRF-Token",
        ],
        expose_headers=["X-Total-Count", "X-Page-Count"],
        max_age=3600,  # Cache preflight requests for 1 hour
    )
