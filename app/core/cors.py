from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

def setup_cors(app):
    # Start with origins from settings
    allowed_origins = settings.FRONTEND_ORIGINS.copy() if settings.FRONTEND_ORIGINS else []

    # Optional: add FRONTEND_URL from env
    if hasattr(settings, 'FRONTEND_URL') and settings.FRONTEND_URL:
        allowed_origins.append(settings.FRONTEND_URL.strip().rstrip("/"))

    # Remove duplicates and strip trailing slashes
    allowed_origins = list({origin.rstrip("/") for origin in allowed_origins})

    print(">>> CORS Allowed Origins:", allowed_origins)  # debug

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,   # ✅ use the final list here
        allow_credentials=True,          # for cookies/JWT
        allow_methods=["GET", "POST", "PUT", "DELETE"],  # specify allowed methods
        allow_headers=["Authorization", "Content-Type"], # specify allowed headers
        expose_headers=["X-Total-Count", "X-Page-Count"],
        max_age=3600,  # cache preflight for 1 hour
    )
    print(">>> CORS setup complete")