import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserCreate
from app.core.hashing import get_password_hash
from app.core.security import create_access_token

class GuestService:
    @staticmethod
    def create_guest_user(db: Session) -> User:
        """Create a new guest user with temporary credentials"""
        # Get or create guest role
        guest_role = db.query(Role).filter(Role.name == "guest").first()
        if not guest_role:
            guest_role = Role(name="guest")
            db.add(guest_role)
            db.commit()
            db.refresh(guest_role)
        
        # Generate unique guest email
        guest_uuid = str(uuid.uuid4())
        guest_email = f"guest_{guest_uuid}@example.com"
        
        # Create guest user
        guest_user = User(
            email=guest_email,
            full_name="Guest User",
            password_encrypted=None,  # No password for guest users
            oauth_provider="guest",
            oauth_id=guest_uuid,
            role_id=guest_role.id,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(guest_user)
        db.commit()
        db.refresh(guest_user)
        
        # Load role relationship
        guest_user_with_role = db.query(User).options(joinedload(User.role_ref)).filter(User.id == guest_user.id).first()
        return guest_user_with_role
    
    @staticmethod
    def create_guest_session(db: Session, guest_user: User) -> dict:
        """Create a session for a guest user"""
        # Create access token with shorter expiry for guests (24 hours)
        access_token_expires = timedelta(hours=24)
        access_token = create_access_token(
            data={"sub": str(guest_user.id), "role": guest_user.role_ref.name},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": guest_user,
            "is_guest": True
        }
    
    @staticmethod
    def migrate_guest_to_user(db: Session, guest_user: User, user_data: UserCreate) -> User:
        """Migrate a guest account to a regular user account"""
        # Get user role
        user_role = db.query(Role).filter(Role.name == "user").first()
        if not user_role:
            raise ValueError("Role 'user' does not exist")
        
        # Hash the password
        hashed_password = get_password_hash(user_data.password)
        
        # Update the guest user to become a regular user
        guest_user.email = user_data.email
        guest_user.full_name = user_data.full_name
        guest_user.password_encrypted = hashed_password
        guest_user.oauth_provider = None  # Remove guest provider
        guest_user.oauth_id = None  # Remove guest ID
        guest_user.role_id = user_role.id  # Change to user role
        guest_user.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(guest_user)
        
        # Load role relationship
        user_with_role = db.query(User).options(joinedload(User.role_ref)).filter(User.id == guest_user.id).first()
        return user_with_role
    
    @staticmethod
    def is_guest_user(user: User) -> bool:
        """Check if a user is a guest user"""
        return user.oauth_provider == "guest" and user.password_encrypted is None
    
    @staticmethod
    def cleanup_expired_guests(db: Session, days_old: int = 7) -> int:
        """Clean up guest accounts older than specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        deleted_count = db.query(User).filter(
            User.oauth_provider == "guest",
            User.created_at < cutoff_date
        ).delete()
        db.commit()
        return deleted_count

guest_service = GuestService()
