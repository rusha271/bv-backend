import uvicorn
from fastapi import FastAPI
from app.core.config import settings
from app.core.cors import setup_cors
from app.core.logging import setup_logging
from app.api import auth, users, files, floorplan, chat, blog, legal, analytics, reload

app = FastAPI(title="FastAPI Backend Boilerplate", version="1.0.0")

setup_logging()
setup_cors(app)

print(">>> FRONTEND_ORIGINS loaded from .env:", settings.FRONTEND_ORIGINS)

# Include routers (to be implemented in api/)
app.include_router(auth, prefix="/auth", tags=["auth"])
app.include_router(users, prefix="/users", tags=["users"])
app.include_router(files, prefix="/files", tags=["files"])
app.include_router(floorplan, prefix="/floorplan", tags=["floorplan"])
app.include_router(chat, prefix="/chat", tags=["chat"])
app.include_router(blog, prefix="/content", tags=["content"])
app.include_router(legal, prefix="/legal", tags=["legal"])
app.include_router(analytics, prefix="/analytics", tags=["analytics"])
app.include_router(reload, tags=["reload"])

@app.on_event("startup")
def on_startup():
    import logging
    logging.info("Starting FastAPI backend...")
    # Optionally: DB connection checks, etc.

@app.on_event("shutdown")
def on_shutdown():
    import logging
    logging.info("Shutting down FastAPI backend...")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
