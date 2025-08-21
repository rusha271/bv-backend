import uvicorn
from fastapi import FastAPI
from app.core.config import settings
from app.core.cors import setup_cors
from app.core.logging import setup_logging
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

#from app.api import auth, users, files, floorplan, chat, blog, legal, analytics
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
from app.api.roles import router as roles_router
# from app.api.videos import router as videos_router

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
app.include_router(roles_router, prefix="/api/roles", tags=["roles"])
# app.include_router(videos_router, prefix="/api/videos", tags=["videos"])

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    print(f"[StarletteHTTPException] {exc.detail}")
    origin = request.headers.get("origin") or "*"
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers={"Access-Control-Allow-Origin": origin}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f"[ValidationError] {exc.errors()}")
    origin = request.headers.get("origin") or "*"
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
        headers={"Access-Control-Allow-Origin": origin}
    )

@app.on_event("startup")
def on_startup():
    import logging
    logging.info("Starting FastAPI backend...")

@app.on_event("shutdown")
def on_shutdown():
    import logging
    logging.info("Shutting down FastAPI backend...")

@app.middleware("http")
async def log_requests(request, call_next):
    print(">>> Request:", request.method, request.url)
    response = await call_next(request)
    print(">>> Response status:", response.status_code)
    return response

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
