from fastapi import APIRouter
from .analytics import router as analytics_router

router = APIRouter()

@router.get("/")
def root():
    return {"message": "API is up and running!"}

# Include analytics router
router.include_router(analytics_router, prefix="/analytics", tags=["analytics"]) 