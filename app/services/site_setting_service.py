from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.site_setting import SiteSetting
from app.schemas.site_setting import SiteSettingCreate, SiteSettingUpdate, SiteSettingCategory
from typing import List, Optional, Dict, Any
import os
import uuid
from datetime import datetime

class SiteSettingService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_site_setting(self, site_setting: SiteSettingCreate) -> SiteSetting:
        """Create a new site setting record"""
        try:
            db_site_setting = SiteSetting(
                category=site_setting.category,
                file_path=site_setting.file_path,
                meta_data=site_setting.meta_data
            )
            self.db.add(db_site_setting)
            self.db.commit()
            self.db.refresh(db_site_setting)
            return db_site_setting
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Failed to create site setting: {str(e)}")
    
    def get_site_setting_by_id(self, site_setting_id: int) -> Optional[SiteSetting]:
        """Get a site setting by ID"""
        return self.db.query(SiteSetting).filter(SiteSetting.id == site_setting_id).first()
    
    def get_site_settings_by_category(self, category: SiteSettingCategory) -> List[SiteSetting]:
        """Get all site settings by category"""
        return self.db.query(SiteSetting).filter(SiteSetting.category == category).order_by(SiteSetting.created_at.desc()).all()
    
    def get_all_site_settings(self, skip: int = 0, limit: int = 100) -> List[SiteSetting]:
        """Get all site settings with pagination"""
        return self.db.query(SiteSetting).order_by(SiteSetting.created_at.desc()).offset(skip).limit(limit).all()
    
    def update_site_setting(self, site_setting_id: int, site_setting_update: SiteSettingUpdate) -> Optional[SiteSetting]:
        """Update a site setting"""
        db_site_setting = self.get_site_setting_by_id(site_setting_id)
        if not db_site_setting:
            return None
        
        update_data = site_setting_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_site_setting, field, value)
        
        db_site_setting.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_site_setting)
        return db_site_setting
    
    def delete_site_setting(self, site_setting_id: int) -> bool:
        """Delete a site setting"""
        db_site_setting = self.get_site_setting_by_id(site_setting_id)
        if not db_site_setting:
            return False
        
        # Delete the physical file if it exists
        file_path = db_site_setting.file_path
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass  # Continue even if file deletion fails
        
        self.db.delete(db_site_setting)
        self.db.commit()
        return True
    
    def get_latest_by_category(self, category: SiteSettingCategory) -> Optional[SiteSetting]:
        """Get the latest site setting by category"""
        return self.db.query(SiteSetting).filter(
            SiteSetting.category == category
        ).order_by(SiteSetting.created_at.desc()).first()
    
    def count_by_category(self, category: SiteSettingCategory) -> int:
        """Count site settings by category"""
        return self.db.query(SiteSetting).filter(SiteSetting.category == category).count()
    
    def get_site_setting_history(self, category: Optional[SiteSettingCategory] = None) -> List[SiteSetting]:
        """Get site setting history, optionally filtered by category"""
        query = self.db.query(SiteSetting)
        if category:
            query = query.filter(SiteSetting.category == category)
        return query.order_by(SiteSetting.created_at.desc()).all()

# Utility functions for file management
def get_category_folder(category: SiteSettingCategory) -> str:
    """Get the folder path for a specific category"""
    category_folders = {
        SiteSettingCategory.LOGO: "logos",
        SiteSettingCategory.TOUR_VIDEO: "tour_videos",
        SiteSettingCategory.CHAKRA_POINTS: "chakra_points"
    }
    return f"app/static/site_settings/{category_folders[category]}"

def get_allowed_extensions(category: SiteSettingCategory) -> List[str]:
    """Get allowed file extensions for each category"""
    extensions = {
        SiteSettingCategory.LOGO: [".png", ".jpg", ".jpeg", ".svg", ".webp"],
        SiteSettingCategory.TOUR_VIDEO: [".mp4", ".avi", ".mov", ".wmv", ".webm"],
        SiteSettingCategory.CHAKRA_POINTS: [".png", ".jpg", ".jpeg", ".pdf", ".svg"]
    }
    return extensions[category]

def get_max_file_size(category: SiteSettingCategory) -> int:
    """Get maximum file size in bytes for each category"""
    sizes = {
        SiteSettingCategory.LOGO: 5 * 1024 * 1024,  # 5MB
        SiteSettingCategory.TOUR_VIDEO: 100 * 1024 * 1024,  # 100MB
        SiteSettingCategory.CHAKRA_POINTS: 10 * 1024 * 1024  # 10MB
    }
    return sizes[category]

def generate_unique_filename(original_filename: str, category: SiteSettingCategory) -> str:
    """Generate a unique filename for the uploaded file"""
    file_ext = os.path.splitext(original_filename)[1]
    unique_id = str(uuid.uuid4())
    return f"{category}_{unique_id}{file_ext}"

def create_category_folders():
    """Create all necessary category folders"""
    categories = [SiteSettingCategory.LOGO, SiteSettingCategory.TOUR_VIDEO, SiteSettingCategory.CHAKRA_POINTS]
    base_path = "app/static/site_settings"
    
    # Create base site_settings folder
    os.makedirs(base_path, exist_ok=True)
    
    # Create category folders
    for category in categories:
        folder_path = get_category_folder(category)
        os.makedirs(folder_path, exist_ok=True)
