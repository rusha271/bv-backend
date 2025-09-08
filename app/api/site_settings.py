from fastapi import APIRouter, Depends, UploadFile, File as FastAPIFile, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.core.security import get_current_admin_user
from app.utils.helpers import validate_file_upload
import os
import shutil
from typing import Optional

router = APIRouter()

# Site settings configuration
UPLOAD_DIR = "uploads"
LOGO_FILENAME = "logo.png"
ALLOWED_IMAGE_TYPES = ["image/png", "image/jpeg", "image/jpg"]
MAX_IMAGE_SIZE_MB = 5

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def validate_site_image_upload(file: UploadFile):
    """Validate image file for site settings (logo)"""
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400, 
            detail="Invalid file type. Only PNG, JPG, and JPEG files are allowed."
        )
    
    file.file.seek(0, 2)  # Seek to end
    size = file.file.tell()
    file.file.seek(0)
    
    if size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400, 
            detail=f"File too large. Maximum size is {MAX_IMAGE_SIZE_MB}MB."
        )

def ensure_upload_directory():
    """Ensure the uploads directory exists"""
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

@router.post("/admin/upload-image")
def upload_site_image(
    file: UploadFile = FastAPIFile(...),
    current_user=Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Upload site image (logo) - Admin only
    Accepts multipart/form-data with image file
    Validates file type (PNG, JPG, JPEG only) and size (max 5MB)
    Stores image in uploads directory
    """
    try:
        # Validate file
        validate_site_image_upload(file)
        
        # Ensure upload directory exists
        ensure_upload_directory()
        
        # Determine file extension
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in ['.png', '.jpg', '.jpeg']:
            raise HTTPException(
                status_code=400,
                detail="Invalid file extension. Only .png, .jpg, and .jpeg files are allowed."
            )
        
        # Use logo.png as the filename (replace existing if any)
        logo_path = os.path.join(UPLOAD_DIR, LOGO_FILENAME)
        
        # Remove existing logo if it exists
        if os.path.exists(logo_path):
            os.remove(logo_path)
        
        # Save the new file
        with open(logo_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Return success response with image URL
        return {
            "message": "Image uploaded successfully",
            "image_url": f"/uploads/{LOGO_FILENAME}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload image: {str(e)}"
        )

@router.get("/get-image")
def get_site_image():
    """
    Get current site image (logo) URL
    Public endpoint - no authentication required
    Returns empty response if no image exists
    """
    try:
        logo_path = os.path.join(UPLOAD_DIR, LOGO_FILENAME)
        
        if os.path.exists(logo_path):
            return {
                "image_url": f"/uploads/{LOGO_FILENAME}"
            }
        else:
            return {
                "image_url": None,
                "message": "No site image found"
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve image: {str(e)}"
        )
