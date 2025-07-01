from fastapi import APIRouter
from app.legal.privacy import PRIVACY_POLICY

router = APIRouter()

@router.get("/privacy")
def get_privacy():
    return {"privacy": PRIVACY_POLICY}

@router.get("/terms")
def get_terms():
    return {"terms": "Sample terms of service. Replace with your own."}

@router.get("/disclaimer")
def get_disclaimer():
    return {"disclaimer": "Sample disclaimer. Replace with your own."} 