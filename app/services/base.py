from typing import Any, Generic, TypeVar, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")

class CRUDBase(Generic[ModelType, CreateSchemaType]):
    def __init__(self, model: type[ModelType]):
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        return db.get(self.model, id)

    def get_by_email(self, db: Session, email: str) -> Optional[ModelType]:
        return db.scalars(select(self.model).filter(self.model.email == email)).first()

    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        db_obj = self.model(**obj_in.dict(exclude_unset=True))
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj