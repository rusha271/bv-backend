from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from typing import List, Set

def get_allowed_origins() -> List[str]:
    """
    Get a clean list of allowed origins with no duplicates.
    Combines FRONTEND_ORIGINS and FRONTEND_URL if provided.
    """
    origins: Set[str] = set()
    
    # Add origins from settings (environment-aware)
    frontend_origins = settings.get_frontend_origins()
    for origin in frontend_origins:
        if origin and origin.strip():
            # Normalize origin: remove trailing slash and ensure proper format
            normalized = origin.strip().rstrip("/")
            if normalized:
                origins.add(normalized)
    
    # Add FRONTEND_URL if provided and not already in the set
    if settings.FRONTEND_URL and settings.FRONTEND_URL.strip():
        normalized_url = settings.FRONTEND_URL.strip().rstrip("/")
        if normalized_url:
            origins.add(normalized_url)
    
    # Convert back to sorted list for consistent ordering
    return sorted(list(origins))

def setup_cors(app):
    """
    Setup CORS middleware with clean, environment-aware configuration.
    Prevents duplicate origins and ensures proper header handling.
    """
    allowed_origins = get_allowed_origins()
    
    # Log the final configuration for debugging
    print(f">>> CORS Environment: {settings.ENV}")
    print(f">>> CORS Allowed Origins: {allowed_origins}")
    
    # Add CORS middleware with comprehensive configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,  # Required for cookies and JWT
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=[
            "Accept",
            "Accept-Language", 
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-CSRFToken",
            "X-Forwarded-For",
            "X-Real-IP"
        ],
        expose_headers=[
            "X-Total-Count", 
            "X-Page-Count",
            "X-Rate-Limit-Remaining",
            "X-Rate-Limit-Reset"
        ],
        max_age=3600,  # Cache preflight requests for 1 hour
    )
    
    print(">>> CORS middleware setup complete")