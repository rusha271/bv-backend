from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import SessionLocal
from app.schemas.consultation import (
    ConsultationCreate, ConsultationRead, ConsultationUpdate,
    ConsultantCreate, ConsultantRead, ConsultantUpdate
)
from app.models.consultation import Consultation, Consultant
from app.core.security import get_current_user, get_current_admin_user
from app.services.consultation_service import (
    create_consultation, get_consultation_by_id, get_user_consultations,
    update_consultation_status, get_all_consultations,
    create_consultant, get_consultant_by_id, get_all_consultants,
    update_consultant, delete_consultant
)
#   import json

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Consultation endpoints
@router.post("/consultation", response_model=ConsultationRead)
def submit_consultation_request(
    consultation: ConsultationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Submit a consultation request"""
    try:
        user_id = int(current_user.sub) if current_user else None
        return create_consultation(db, consultation, user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create consultation: {str(e)}"
        )

@router.post("/consultation/simple")
def submit_simple_consultation(
    consultation_data: dict,
    db: Session = Depends(get_db)
):
    try:
        name = consultation_data.get("name")
        email = consultation_data.get("email")
        phone = consultation_data.get("phone", "")
        message = consultation_data.get("message")
        concern_type = consultation_data.get("concernType") or consultation_data.get("subject", "general")  # Accept both
        preferred_date = consultation_data.get("preferred_date")
        if not name or not email or not message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Name, email, and message are required"
            )

        consultation_info = {
            "name": name,
            "email": email,
            "phone": phone,
            "message": message,
            "concern_type": concern_type,
            "preferred_date" : preferred_date,
            "status": "received"
        }

        # Save to database
        db_consultation = Consultation(
            name=name,
            email=email,
            phone=phone,
            consultation_type=concern_type,
            message=message,
            preferred_date = preferred_date,
            status="received"
        )
        db.add(db_consultation)
        db.commit()
        db.refresh(db_consultation)

        return {
            "message": "Consultation request submitted successfully",
            "status": "received",
            "data": consultation_info
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to submit consultation: {str(e)}"
        )
    
@router.get("/consultation/{consultation_id}", response_model=ConsultationRead)
def get_consultation(
    consultation_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific consultation"""
    consultation = get_consultation_by_id(db, consultation_id)
    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultation not found"
        )
    
    # Check if user owns this consultation or is admin
    if consultation.user_id != int(current_user.sub) and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this consultation"
        )
    
    return consultation

@router.get("/consultations", response_model=List[ConsultationRead])
def get_consultations(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get user's consultations"""
    if current_user.role == "admin":
        return get_all_consultations(db)
    else:
        return get_user_consultations(db, int(current_user.sub))

@router.put("/consultation/{consultation_id}", response_model=ConsultationRead)
def update_consultation(
    consultation_id: int,
    consultation_update: ConsultationUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """Update consultation status (admin only)"""
    consultation = update_consultation_status(db, consultation_id, consultation_update)
    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultation not found"
        )
    return consultation

# Consultant endpoints
@router.post("/consultant", response_model=ConsultantRead)
def create_new_consultant(
    consultant: ConsultantCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """Create a new consultant (admin only)"""
    return create_consultant(db, consultant)

@router.get("/consultants", response_model=List[ConsultantRead])
def get_consultants(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get all consultants"""
    return get_all_consultants(db, active_only)

@router.get("/consultant/{consultant_id}", response_model=ConsultantRead)
def get_consultant(
    consultant_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific consultant"""
    consultant = get_consultant_by_id(db, consultant_id)
    if not consultant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultant not found"
        )
    return consultant

@router.put("/consultant/{consultant_id}", response_model=ConsultantRead)
def update_consultant_info(
    consultant_id: int,
    consultant_update: ConsultantUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """Update consultant information (admin only)"""
    consultant = update_consultant(db, consultant_id, consultant_update)
    if not consultant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultant not found"
        )
    return consultant

@router.delete("/consultant/{consultant_id}")
def delete_consultant_endpoint(
    consultant_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """Delete a consultant (admin only)"""
    success = delete_consultant(db, consultant_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultant not found"
        )
    return {"message": "Consultant deleted successfully"}
