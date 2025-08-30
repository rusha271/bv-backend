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

@router.delete("/{file_id}")
def delete_file(file_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Delete a file and its associated data"""
    file_obj = db.query(FileModel).filter(FileModel.id == file_id).first()
    if not file_obj:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Check if user owns the file or is admin
    if file_obj.user_id != int(current_user.sub):
        raise HTTPException(status_code=403, detail="Not authorized to delete this file")
    
    try:
        # Delete the physical file
        if os.path.exists(file_obj.path):
            os.remove(file_obj.path)
        
        # Delete the database record (cascade will handle related records)
        db.delete(file_obj)
        db.commit()
        
        return {"message": "File deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")

@router.delete("/cleanup/orphaned")
def cleanup_orphaned_files(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Clean up orphaned files that exist on disk but not in database"""
    try:
        # Get all files in the upload directory
        uploaded_files = []
        for filename in os.listdir(UPLOAD_DIR):
            file_path = os.path.join(UPLOAD_DIR, filename)
            if os.path.isfile(file_path):
                uploaded_files.append(file_path)
        
        # Get all file paths from database
        db_files = db.query(FileModel.path).all()
        db_file_paths = [file.path for file in db_files]
        
        # Find orphaned files
        orphaned_files = [f for f in uploaded_files if f not in db_file_paths]
        
        deleted_count = 0
        for orphaned_file in orphaned_files:
            try:
                os.remove(orphaned_file)
                deleted_count += 1
            except Exception as e:
                print(f"Error deleting orphaned file {orphaned_file}: {e}")
        
        return {
            "message": f"Cleanup completed. Deleted {deleted_count} orphaned files.",
            "deleted_count": deleted_count,
            "total_orphaned": len(orphaned_files)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during cleanup: {str(e)}")

@router.get("/list/user")
def list_user_files(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """List all files for the current user"""
    files = db.query(FileModel).filter(FileModel.user_id == int(current_user.sub)).all()
    return files
