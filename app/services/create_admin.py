import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from datetime import datetime
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.core.hashing import get_password_hash

def create_admin_user(email: str, password: str, full_name: str, phone: str = None):
    db = SessionLocal()
    try:
        # Check if admin role exists
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if not admin_role:
            print("Admin role not found. Creating admin role...")
            admin_role = Role(name="admin", description="Administrator role")
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)
            print(f"Created admin role with ID: {admin_role.id}")

        # Check if user role exists (for reference, not used here)
        user_role = db.query(Role).filter(Role.name == "user").first()
        if not user_role:
            print("User role not found. Creating user role...")
            user_role = Role(name="user", description="Standard user role")
            db.add(user_role)
            db.commit()
            db.refresh(user_role)
            print(f"Created user role with ID: {user_role.id}")

        # Check if user already exists
        if db.query(User).filter(User.email == email).first():
            print(f"User with email {email} already exists")
            return

        # Hash the password
        hashed_password = get_password_hash(password)

        # Create the admin user
        admin_user = User(
            email=email,
            password_encrypted=hashed_password,
            full_name=full_name,
            phone=phone,
            role_id=admin_role.id,  # Assign admin role
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        print(f"Admin user {email} created successfully with ID: {admin_user.id}")

    except Exception as e:
        print(f"Error creating admin user: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user(
        email="admin@gmail.com",
        password="Admin@Secure!46",
        full_name="AdminUser",
        phone="+919834208548"
    )