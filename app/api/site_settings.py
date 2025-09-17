from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.site_setting import SiteSetting
from app.schemas.site_setting import (
    SiteSettingCreate, SiteSettingUpdate, SiteSettingRead, 
    SiteSettingResponse, SiteSettingListResponse, SiteSettingCategory,
    SiteSettingUpload
)
from app.services.site_setting_service import (
    SiteSettingService, get_category_folder, get_allowed_extensions,
    get_max_file_size, generate_unique_filename, create_category_folders
)
from app.core.security import get_current_user, require_role
from typing import List, Optional
import os
import mimetypes

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_public_url(category: str, filename: str) -> str:
    """Generate public URL for a file based on category and filename"""
    category_folder_map = {
        "logo": "logos",
        "tour_video": "tour_videos", 
        "chakra_points": "chakra_points"
    }
    return f"/static/site_settings/{category_folder_map[category]}/{filename}"

@router.post("/upload", response_model=SiteSettingResponse)
async def upload_site_setting_file(
    category: str = Form(...),
    file: UploadFile = File(...),
    file_name: Optional[str] = Form(None),
    uploader: Optional[str] = Form(None),
    version: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    """
    Upload a file for site settings (logos, tour videos, chakra points)
    """
    try:
        # Validate category
        try:
            category_enum = SiteSettingCategory(category)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category. Must be one of: {[c.value for c in SiteSettingCategory]}"
            )
        
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        # Check file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        allowed_extensions = get_allowed_extensions(category_enum)
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Check file size
        file_content = await file.read()
        file_size = len(file_content)
        max_size = get_max_file_size(category_enum)
        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size: {max_size // (1024*1024)}MB"
            )
        
        # Create category folders if they don't exist
        create_category_folders()
        
        # Generate unique filename
        unique_filename = generate_unique_filename(file.filename, category_enum)
        folder_path = get_category_folder(category_enum)
        file_path = os.path.join(folder_path, unique_filename)
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Prepare metadata
        metadata = {
            "original_filename": file.filename,
            "file_size": file_size,
            "mime_type": file.content_type,
            "uploader": uploader or getattr(current_user, "sub", "unknown"),
            "version": version,
            "description": description
        }
        
        # Create database record
        site_setting_service = SiteSettingService(db)
        site_setting_data = SiteSettingCreate(
            category=category_enum,
            file_path=file_path,
            meta_data=metadata
        )
        
        db_site_setting = site_setting_service.create_site_setting(site_setting_data)
        
        # Generate public URL
        public_url = get_public_url(category_enum.value, unique_filename)
        
        return SiteSettingResponse(
            success=True,
            message="File uploaded successfully",
            data=db_site_setting,
            file_url=public_url
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up file if database operation fails
        if 'file_path' in locals() and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )

@router.get("/", response_model=SiteSettingListResponse)
def get_site_settings(
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get site settings with optional category filter
    """
    try:
        site_setting_service = SiteSettingService(db)
        
        if category:
            try:
                category_enum = SiteSettingCategory(category)
                site_settings = site_setting_service.get_site_settings_by_category(category_enum)
                total = site_setting_service.count_by_category(category_enum)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid category. Must be one of: {[c.value for c in SiteSettingCategory]}"
                )
        else:
            site_settings = site_setting_service.get_all_site_settings(skip, limit)
            total = len(site_settings)
        
        return SiteSettingListResponse(
            success=True,
            message=f"Retrieved {len(site_settings)} site settings",
            data=site_settings,
            total=total,
            category=category
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve site settings: {str(e)}"
        )

@router.get("/{site_setting_id}", response_model=SiteSettingResponse)
def get_site_setting(
    site_setting_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific site setting by ID
    """
    try:
        site_setting_service = SiteSettingService(db)
        site_setting = site_setting_service.get_site_setting_by_id(site_setting_id)
        
        if not site_setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Site setting not found"
            )
        
        # Generate public URL
        filename = os.path.basename(site_setting.file_path)
        public_url = get_public_url(site_setting.category, filename)
        
        return SiteSettingResponse(
            success=True,
            message="Site setting retrieved successfully",
            data=site_setting,
            file_url=public_url
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve site setting: {str(e)}"
        )

@router.get("/category/{category}/latest", response_model=SiteSettingResponse)
def get_latest_site_setting_by_category(
    category: str,
    db: Session = Depends(get_db)
):
    """
    Get the latest site setting for a specific category
    """
    try:
        try:
            category_enum = SiteSettingCategory(category)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category. Must be one of: {[c.value for c in SiteSettingCategory]}"
            )
        
        site_setting_service = SiteSettingService(db)
        site_setting = site_setting_service.get_latest_by_category(category_enum)
        
        if not site_setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No site settings found for category: {category}"
            )
        
        # Generate public URL
        filename = os.path.basename(site_setting.file_path)
        public_url = get_public_url(site_setting.category, filename)
        
        return SiteSettingResponse(
            success=True,
            message=f"Latest {category} retrieved successfully",
            data=site_setting,
            file_url=public_url
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve latest site setting: {str(e)}"
        )

@router.put("/{site_setting_id}", response_model=SiteSettingResponse)
def update_site_setting(
    site_setting_id: int,
    site_setting_update: SiteSettingUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    """
    Update a site setting
    """
    try:
        site_setting_service = SiteSettingService(db)
        updated_site_setting = site_setting_service.update_site_setting(site_setting_id, site_setting_update)
        
        if not updated_site_setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Site setting not found"
            )
        
        # Generate public URL
        filename = os.path.basename(updated_site_setting.file_path)
        public_url = get_public_url(updated_site_setting.category, filename)
        
        return SiteSettingResponse(
            success=True,
            message="Site setting updated successfully",
            data=updated_site_setting,
            file_url=public_url
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update site setting: {str(e)}"
        )

@router.delete("/{site_setting_id}")
def delete_site_setting(
    site_setting_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    """
    Delete a site setting and its associated file
    """
    try:
        site_setting_service = SiteSettingService(db)
        success = site_setting_service.delete_site_setting(site_setting_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Site setting not found"
            )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "message": "Site setting deleted successfully"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete site setting: {str(e)}"
        )

@router.get("/history/{category}", response_model=SiteSettingListResponse)
def get_site_setting_history(
    category: str,
    db: Session = Depends(get_db)
):
    """
    Get upload history for a specific category
    """
    try:
        try:
            category_enum = SiteSettingCategory(category)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category. Must be one of: {[c.value for c in SiteSettingCategory]}"
            )
        
        site_setting_service = SiteSettingService(db)
        history = site_setting_service.get_site_setting_history(category_enum)
        
        return SiteSettingListResponse(
            success=True,
            message=f"Retrieved {len(history)} historical records for {category}",
            data=history,
            total=len(history),
            category=category
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve history: {str(e)}"
        )