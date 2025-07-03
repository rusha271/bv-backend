from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

def setup_cors(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.FRONTEND_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
