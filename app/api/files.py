from fastapi import APIRouter, Depends, UploadFile, File as FastAPIFile, HTTPException, status, Response
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.file import File as FileModel
from app.models.user import User
from app.schemas.file import FileRead
from app.core.security import get_current_user
from app.utils.helpers import validate_file_upload
import os
from uuid import uuid4

UPLOAD_DIR = "app/static"

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload/floorplan", response_model=FileRead)
def upload_floorplan(
    file: UploadFile = FastAPIFile(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    validate_file_upload(file)
    filename = f"{uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    file_obj = FileModel(
        user_id=int(current_user.sub),
        filename=filename,
        content_type=file.content_type,
        size=os.path.getsize(file_path),
        path=file_path
    )
    db.add(file_obj)
    db.commit()
    db.refresh(file_obj)
    return file_obj

@router.get("/{file_id}")
def serve_file(file_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    file_obj = db.query(FileModel).filter(FileModel.id == file_id).first()
    if not file_obj:
        raise HTTPException(status_code=404, detail="File not found")
    with open(file_obj.path, "rb") as f:
        content = f.read()
    return Response(content, media_type=file_obj.content_type)
