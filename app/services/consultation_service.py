from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.consultation import Consultation, Consultant
from app.schemas.consultation import ConsultationCreate, ConsultationUpdate, ConsultantCreate, ConsultantUpdate
import json

# Consultation services
def create_consultation(db: Session, consultation: ConsultationCreate, user_id: Optional[int] = None) -> Consultation:
    """Create a new consultation request"""
    db_consultation = Consultation(
        user_id=user_id,
        name=consultation.name,
        email=consultation.email,
        phone=consultation.phone,
        consultation_type=consultation.consultation_type,
        message=consultation.message,
        preferred_date=consultation.preferred_date
    )
    db.add(db_consultation)
    db.commit()
    db.refresh(db_consultation)
    return db_consultation

def get_consultation_by_id(db: Session, consultation_id: int) -> Optional[Consultation]:
    """Get consultation by ID"""
    return db.query(Consultation).filter(Consultation.id == consultation_id).first()

def get_user_consultations(db: Session, user_id: int) -> List[Consultation]:
    """Get all consultations for a user"""
    return db.query(Consultation).filter(Consultation.user_id == user_id).all()

def get_all_consultations(db: Session, skip: int = 0, limit: int = 100) -> List[Consultation]:
    """Get all consultations (admin only)"""
    return db.query(Consultation).offset(skip).limit(limit).all()

def update_consultation_status(db: Session, consultation_id: int, consultation_update: ConsultationUpdate) -> Optional[Consultation]:
    """Update consultation status"""
    db_consultation = db.query(Consultation).filter(Consultation.id == consultation_id).first()
    if not db_consultation:
        return None
    
    update_data = consultation_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_consultation, field, value)
    
    db.commit()
    db.refresh(db_consultation)
    return db_consultation

def delete_consultation(db: Session, consultation_id: int) -> bool:
    """Delete consultation"""
    db_consultation = db.query(Consultation).filter(Consultation.id == consultation_id).first()
    if not db_consultation:
        return False
    
    db.delete(db_consultation)
    db.commit()
    return True

# Consultant services
def create_consultant(db: Session, consultant: ConsultantCreate) -> Consultant:
    """Create a new consultant"""
    db_consultant = Consultant(
        name=consultant.name,
        title=consultant.title,
        description=consultant.description,
        expertise=json.dumps(consultant.expertise),  # Store as JSON string
        experience=consultant.experience,
        clients=consultant.clients,
        image_url=consultant.image_url,
        video_url=consultant.video_url,
        is_active=consultant.is_active
    )
    db.add(db_consultant)
    db.commit()
    db.refresh(db_consultant)
    return db_consultant

def get_consultant_by_id(db: Session, consultant_id: int) -> Optional[Consultant]:
    """Get consultant by ID"""
    return db.query(Consultant).filter(Consultant.id == consultant_id).first()

def get_all_consultants(db: Session, active_only: bool = True) -> List[Consultant]:
    """Get all consultants"""
    query = db.query(Consultant)
    if active_only:
        query = query.filter(Consultant.is_active == True)
    return query.all()

def update_consultant(db: Session, consultant_id: int, consultant_update: ConsultantUpdate) -> Optional[Consultant]:
    """Update consultant information"""
    db_consultant = db.query(Consultant).filter(Consultant.id == consultant_id).first()
    if not db_consultant:
        return None
    
    update_data = consultant_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "expertise" and value is not None:
            value = json.dumps(value)  # Store as JSON string
        setattr(db_consultant, field, value)
    
    db.commit()
    db.refresh(db_consultant)
    return db_consultant

def delete_consultant(db: Session, consultant_id: int) -> bool:
    """Delete consultant"""
    db_consultant = db.query(Consultant).filter(Consultant.id == consultant_id).first()
    if not db_consultant:
        return False
    
    db.delete(db_consultant)
    db.commit()
    return True

def get_consultation_stats(db: Session) -> dict:
    """Get consultation statistics"""
    total_consultations = db.query(Consultation).count()
    pending_consultations = db.query(Consultation).filter(Consultation.status == "pending").count()
    completed_consultations = db.query(Consultation).filter(Consultation.status == "completed").count()
    
    return {
        "total": total_consultations,
        "pending": pending_consultations,
        "completed": completed_consultations,
        "scheduled": db.query(Consultation).filter(Consultation.status == "scheduled").count(),
        "cancelled": db.query(Consultation).filter(Consultation.status == "cancelled").count()
    }
