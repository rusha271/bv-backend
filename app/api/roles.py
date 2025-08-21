from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.role import Role
from app.models.page_access import PageAccess
from app.core.security import get_current_admin_user
from typing import List
from pydantic import BaseModel

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models for API
class RoleCreate(BaseModel):
    name: str

class RoleRead(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True

class PageAccessCreate(BaseModel):
    role_id: int
    page_name: str
    can_access: bool = True
    can_read: bool = True
    can_write: bool = False
    can_delete: bool = False

class PageAccessRead(BaseModel):
    id: int
    role_id: int
    page_name: str
    can_access: bool
    can_read: bool
    can_write: bool
    can_delete: bool
    
    class Config:
        from_attributes = True

# Role management endpoints
@router.post("/roles", response_model=RoleRead)
def create_role(role: RoleCreate, db: Session = Depends(get_db), 
                current_user=Depends(get_current_admin_user)):
    """Create a new role (admin only)"""
    from app.services.role_service import create_role as create_role_service
    return create_role_service(db, role.name)

@router.get("/roles", response_model=List[RoleRead])
def get_roles(db: Session = Depends(get_db), 
              current_user=Depends(get_current_admin_user)):
    """Get all roles (admin only)"""
    from app.services.role_service import get_all_roles
    return get_all_roles(db)

# Page access management endpoints
@router.post("/page-access", response_model=PageAccessRead)
def create_page_access(page_access: PageAccessCreate, db: Session = Depends(get_db),
                      current_user=Depends(get_current_admin_user)):
    """Create page access permission (admin only)"""
    from app.services.role_service import create_page_access
    return create_page_access(
        db, 
        page_access.role_id, 
        page_access.page_name,
        page_access.can_access,
        page_access.can_read,
        page_access.can_write,
        page_access.can_delete
    )

@router.get("/page-access/{role_id}", response_model=List[PageAccessRead])
def get_role_page_access(role_id: int, db: Session = Depends(get_db),
                        current_user=Depends(get_current_admin_user)):
    """Get page access for a specific role (admin only)"""
    page_access_list = db.query(PageAccess).filter(PageAccess.role_id == role_id).all()
    return page_access_list

@router.get("/user-page-access/{user_id}")
def get_user_page_access(user_id: int, db: Session = Depends(get_db),
                        current_user=Depends(get_current_admin_user)):
    """Get all accessible pages for a user (admin only)"""
    from app.services.role_service import get_user_accessible_pages
    return get_user_accessible_pages(db, user_id)

@router.get("/check-permission/{user_id}/{page_name}/{permission}")
def check_user_permission(user_id: int, page_name: str, permission: str, 
                         db: Session = Depends(get_db),
                         current_user=Depends(get_current_admin_user)):
    """Check if user has specific permission for a page (admin only)"""
    from app.services.role_service import check_user_permission as check_permission
    has_permission = check_permission(db, user_id, page_name, permission)
    return {"user_id": user_id, "page_name": page_name, "permission": permission, "has_permission": has_permission} 