from sqlalchemy.orm import Session, joinedload
from app.models.user import User
from app.models.role import Role  # Import the Role model
from app.schemas.user import UserCreate
from app.core.hashing import get_password_hash
from .base import CRUDBase

class CRUDUser(CRUDBase[User, UserCreate]):
    def get_by_email(self, db: Session, email: str) -> User | None:
        return db.query(User).options(joinedload(User.role_ref)).filter(User.email == email).first()

    def create(self, db: Session, obj_in: UserCreate) -> User:
        hashed_password = get_password_hash(obj_in.password)
        print(f"Hashed password: {hashed_password}")
        
        # Query the "user" role from the roles table
        role_obj = db.query(Role).filter(Role.name == "user").first()
        if not role_obj:
            raise ValueError("Role 'user' does not exist")
        
        # Create the User object with role_id instead of role
        db_obj = User(
            email=obj_in.email,
            password_encrypted=hashed_password,
            full_name=obj_in.full_name,
            role_id=role_obj.id,  # Use role_id instead of role
            is_active=True
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Load the role relationship for the response
        user_with_role = db.query(User).options(joinedload(User.role_ref)).filter(User.id == db_obj.id).first()
        return user_with_role

user = CRUDUser(User)

def get_user_by_email(db: Session, email: str) -> User | None:
    return user.get_by_email(db, email)

def create_user(db: Session, user_in: UserCreate) -> User:
    return user.create(db, user_in)