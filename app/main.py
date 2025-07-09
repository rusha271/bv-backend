import uvicorn
from fastapi import FastAPI
from app.core.config import settings
from app.core.cors import setup_cors
from app.core.logging import setup_logging

from app.api import auth, users, files, floorplan, chat, blog, legal, analytics
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.files import router as files_router
from app.api.floorplan import router as floorplan_router
from app.api.chat import router as chat_router
from app.api.blog import router as blog_router
from app.api.legal import router as legal_router
from app.api.analytics import router as analytics_router
from app.api.contact import router as contact_router
from app.api.vastu import router as vastu_router

app = FastAPI(
    title="Brahma Vastu Backend API", 
    version="1.0.0",
    description="Backend API for Brahma Vastu - Floor Plan Analysis and Vastu Consultation Platform"
)

setup_logging()
setup_cors(app)

print(">>> FRONTEND_ORIGINS loaded from .env:", settings.FRONTEND_ORIGINS)

# Add a simple health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Backend is running"}

# Include routers (to be implemented in api/)
app.include_router(auth, prefix="/auth", tags=["auth"])
app.include_router(users, prefix="/users", tags=["users"])
app.include_router(files, prefix="/files", tags=["files"])
app.include_router(floorplan, prefix="/floorplan", tags=["floorplan"])
app.include_router(chat, prefix="/chat", tags=["chat"])
app.include_router(blog, prefix="/content", tags=["content"])
app.include_router(legal, prefix="/legal", tags=["legal"])
app.include_router(analytics, prefix="/analytics", tags=["analytics"])
# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(users_router, prefix="/api/users", tags=["users"])
app.include_router(files_router, prefix="/api/files", tags=["files"])
app.include_router(floorplan_router, prefix="/api/floorplan", tags=["floorplan"])
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
app.include_router(blog_router, prefix="/api/blog", tags=["blog"])
app.include_router(legal_router, prefix="/api/legal", tags=["legal"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["analytics"])
app.include_router(contact_router, prefix="/api/contact", tags=["contact"])
app.include_router(vastu_router, prefix="/api/vastu", tags=["vastu"])


@app.on_event("startup")
def on_startup():
    import logging
    logging.info("Starting FastAPI backend...")

@app.on_event("shutdown")
def on_shutdown():
    import logging
    logging.info("Shutting down FastAPI backend...")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
