from sqlalchemy.orm import Session
from app.models.role import Role
from app.models.page_access import PageAccess
from app.models.user import User
from typing import List, Optional

def create_role(db: Session, name: str) -> Role:
    """Create a new role"""
    role = Role(name=name)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role

def get_role_by_id(db: Session, role_id: int) -> Optional[Role]:
    """Get role by ID"""
    return db.query(Role).filter(Role.id == role_id).first()

def get_role_by_name(db: Session, name: str) -> Optional[Role]:
    """Get role by name"""
    return db.query(Role).filter(Role.name == name).first()

def get_all_roles(db: Session) -> List[Role]:
    """Get all roles"""
    return db.query(Role).all()

def create_page_access(db: Session, role_id: int, page_name: str, 
                      can_access: bool = True, can_read: bool = True, 
                      can_write: bool = False, can_delete: bool = False) -> PageAccess:
    """Create page access permission for a role"""
    page_access = PageAccess(
        role_id=role_id,
        page_name=page_name,
        can_access=can_access,
        can_read=can_read,
        can_write=can_write,
        can_delete=can_delete
    )
    db.add(page_access)
    db.commit()
    db.refresh(page_access)
    return page_access

def get_user_page_access(db: Session, user_id: int, page_name: str) -> Optional[PageAccess]:
    """Get page access for a specific user and page"""
    return db.query(PageAccess).join(Role).join(User).filter(
        User.id == user_id,
        PageAccess.page_name == page_name
    ).first()

def get_user_accessible_pages(db: Session, user_id: int) -> List[PageAccess]:
    """Get all accessible pages for a user"""
    return db.query(PageAccess).join(Role).join(User).filter(
        User.id == user_id,
        PageAccess.can_access == True
    ).all()

def check_user_permission(db: Session, user_id: int, page_name: str, permission: str) -> bool:
    """Check if user has specific permission for a page"""
    page_access = get_user_page_access(db, user_id, page_name)
    if not page_access:
        return False
    
    if permission == "access":
        return page_access.can_access
    elif permission == "read":
        return page_access.can_read
    elif permission == "write":
        return page_access.can_write
    elif permission == "delete":
        return page_access.can_delete
    return False 