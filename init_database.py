#!/usr/bin/env python3
"""
Database initialization script for Brahmavastu application.
This script sets up the database with initial roles and page access permissions.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models import Base, Role, PageAccess
from app.services.role_service import create_role, create_page_access

def init_database():
    """Initialize the database with tables and initial data"""
    
    # Create database engine
    engine = create_engine(settings.DATABASE_URL)
    
    # Create all tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if roles already exist
        existing_roles = db.query(Role).all()
        if existing_roles:
            print("Roles already exist, skipping initialization...")
            return
        
        print("Creating initial roles...")
        
        # Create default roles
        admin_role = create_role(db, "admin")
        user_role = create_role(db, "user")
        consultant_role = create_role(db, "consultant")
        
        print("Creating page access permissions...")
        
        # Define pages and their access permissions
        pages_config = {
            "dashboard": {
                "admin": {"access": True, "read": True, "write": True, "delete": True},
                "user": {"access": True, "read": True, "write": False, "delete": False},
                "consultant": {"access": True, "read": True, "write": True, "delete": False}
            },
            "analytics": {
                "admin": {"access": True, "read": True, "write": True, "delete": True},
                "user": {"access": False, "read": False, "write": False, "delete": False},
                "consultant": {"access": True, "read": True, "write": False, "delete": False}
            },
            "admin": {
                "admin": {"access": True, "read": True, "write": True, "delete": True},
                "user": {"access": False, "read": False, "write": False, "delete": False},
                "consultant": {"access": False, "read": False, "write": False, "delete": False}
            },
            "consultations": {
                "admin": {"access": True, "read": True, "write": True, "delete": True},
                "user": {"access": True, "read": True, "write": True, "delete": False},
                "consultant": {"access": True, "read": True, "write": True, "delete": False}
            },
            "vastu_calculator": {
                "admin": {"access": True, "read": True, "write": True, "delete": True},
                "user": {"access": True, "read": True, "write": True, "delete": False},
                "consultant": {"access": True, "read": True, "write": True, "delete": False}
            },
            "blog": {
                "admin": {"access": True, "read": True, "write": True, "delete": True},
                "user": {"access": True, "read": True, "write": False, "delete": False},
                "consultant": {"access": True, "read": True, "write": False, "delete": False}
            }
        }
        
        # Create page access permissions for each role
        for page_name, role_permissions in pages_config.items():
            for role_name, permissions in role_permissions.items():
                role = db.query(Role).filter(Role.name == role_name).first()
                if role:
                    create_page_access(
                        db,
                        role.id,
                        page_name,
                        permissions["access"],
                        permissions["read"],
                        permissions["write"],
                        permissions["delete"]
                    )
        
        print("Database initialization completed successfully!")
        
    except Exception as e:
        print(f"Error during database initialization: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Initializing Brahmavastu database...")
    init_database()
    print("Database initialization complete!") 