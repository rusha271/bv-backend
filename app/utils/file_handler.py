"""
File handling utilities for multiple file uploads
Supports backward compatibility with single file uploads
"""
import os
import uuid
import mimetypes
from typing import List, Optional, Dict, Any, Tuple
from fastapi import UploadFile, HTTPException
from datetime import datetime


class MultipleFileHandler:
    """Handles multiple file uploads with unique naming and folder organization"""
    
    def __init__(self, base_upload_dir: str = "app/static/media"):
        self.base_upload_dir = base_upload_dir
    
    def create_unique_filename(self, original_filename: str, file_type: str = "file") -> str:
        """Create a unique filename with proper extension"""
        file_ext = os.path.splitext(original_filename)[1]
        if not file_ext:
            # Try to guess extension from content type
            content_type = getattr(original_filename, 'content_type', None)
            if content_type:
                file_ext = mimetypes.guess_extension(content_type) or ".bin"
            else:
                file_ext = ".bin"
        
        return f"{file_type}_{uuid.uuid4()}{file_ext}"
    
    def create_content_folder(self, content_type: str, content_id: Optional[int] = None) -> str:
        """Create a folder for specific content type and optionally content ID"""
        if content_id:
            folder_path = os.path.join(self.base_upload_dir, content_type, f"content_{content_id}")
        else:
            folder_path = os.path.join(self.base_upload_dir, content_type, f"temp_{uuid.uuid4()}")
        
        os.makedirs(folder_path, exist_ok=True)
        return folder_path
    
    async def save_multiple_files(
        self, 
        files: List[UploadFile], 
        content_type: str, 
        content_id: Optional[int] = None,
        file_type: str = "file"
    ) -> List[str]:
        """
        Save multiple files and return list of relative URLs
        
        Args:
            files: List of UploadFile objects
            content_type: Type of content (books, videos, tips, etc.)
            content_id: Optional content ID for folder organization
            file_type: Type of file (image, video, pdf, etc.)
        
        Returns:
            List of relative URLs for saved files
        """
        if not files:
            return []
        
        # Create content-specific folder
        folder_path = self.create_content_folder(content_type, content_id)
        saved_urls = []
        
        for i, file in enumerate(files):
            try:
                # Validate file
                if not file.filename:
                    continue
                
                # Create unique filename
                unique_filename = self.create_unique_filename(file.filename, f"{file_type}_{i}")
                file_path = os.path.join(folder_path, unique_filename)
                
                # Save file
                content = await file.read()
                with open(file_path, "wb") as f:
                    f.write(content)
                
                # Create relative URL
                relative_path = file_path.replace("app/static/", "/static/")
                saved_urls.append(relative_path)
                
            except Exception as e:
                # Clean up any partially saved files
                for url in saved_urls:
                    full_path = url.replace("/static/", "app/static/")
                    if os.path.exists(full_path):
                        os.remove(full_path)
                raise HTTPException(
                    status_code=500, 
                    detail=f"Failed to save file {file.filename}: {str(e)}"
                )
        
        return saved_urls
    
    async def save_single_file(
        self, 
        file: UploadFile, 
        content_type: str, 
        content_id: Optional[int] = None,
        file_type: str = "file"
    ) -> str:
        """
        Save a single file and return relative URL (backward compatibility)
        
        Args:
            file: UploadFile object
            content_type: Type of content (books, videos, tips, etc.)
            content_id: Optional content ID for folder organization
            file_type: Type of file (image, video, pdf, etc.)
        
        Returns:
            Relative URL for saved file
        """
        if not file or not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Create content-specific folder
        folder_path = self.create_content_folder(content_type, content_id)
        
        # Create unique filename
        unique_filename = self.create_unique_filename(file.filename, file_type)
        file_path = os.path.join(folder_path, unique_filename)
        
        try:
            # Save file
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            
            # Create relative URL
            relative_path = file_path.replace("app/static/", "/static/")
            return relative_path
            
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to save file {file.filename}: {str(e)}"
            )
    
    def validate_files(
        self, 
        files: List[UploadFile], 
        allowed_types: List[str], 
        max_size: int = 10 * 1024 * 1024,  # 10MB default
        max_files: int = 10
    ) -> Tuple[List[UploadFile], List[str]]:
        """
        Validate multiple files
        
        Args:
            files: List of UploadFile objects
            allowed_types: List of allowed MIME types
            max_size: Maximum file size in bytes
            max_files: Maximum number of files allowed
        
        Returns:
            Tuple of (valid_files, error_messages)
        """
        if len(files) > max_files:
            return [], [f"Too many files. Maximum {max_files} files allowed."]
        
        valid_files = []
        errors = []
        
        for i, file in enumerate(files):
            if not file.filename:
                errors.append(f"File {i+1}: No filename provided")
                continue
            
            # Check file size
            if hasattr(file, 'size') and file.size > max_size:
                errors.append(f"File {i+1} ({file.filename}): File too large. Maximum {max_size} bytes allowed.")
                continue
            
            # Check MIME type
            if file.content_type not in allowed_types:
                errors.append(f"File {i+1} ({file.filename}): Invalid file type. Allowed: {', '.join(allowed_types)}")
                continue
            
            valid_files.append(file)
        
        return valid_files, errors
    
    def cleanup_files(self, urls: List[str]) -> None:
        """Clean up files by their URLs"""
        for url in urls:
            try:
                full_path = url.replace("/static/", "app/static/")
                if os.path.exists(full_path):
                    os.remove(full_path)
            except Exception as e:
                print(f"Warning: Could not delete file {url}: {str(e)}")


# File type configurations
FILE_TYPE_CONFIGS = {
    "images": {
        "allowed_types": ["image/jpeg", "image/png", "image/gif", "image/webp", "image/jpg"],
        "max_size": 5 * 1024 * 1024,  # 5MB
        "max_files": 10
    },
    "videos": {
        "allowed_types": ["video/mp4", "video/avi", "video/mov", "video/wmv", "video/webm"],
        "max_size": 100 * 1024 * 1024,  # 100MB
        "max_files": 5
    },
    "documents": {
        "allowed_types": ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"],
        "max_size": 20 * 1024 * 1024,  # 20MB
        "max_files": 10
    },
    "audio": {
        "allowed_types": ["audio/mpeg", "audio/wav", "audio/ogg", "audio/mp3"],
        "max_size": 50 * 1024 * 1024,  # 50MB
        "max_files": 5
    }
}


def get_file_handler() -> MultipleFileHandler:
    """Get a file handler instance"""
    return MultipleFileHandler()


def validate_and_save_files(
    files: List[UploadFile], 
    file_type: str, 
    content_type: str, 
    content_id: Optional[int] = None
) -> List[str]:
    """
    Convenience function to validate and save multiple files
    
    Args:
        files: List of UploadFile objects
        file_type: Type of files (images, videos, documents, audio)
        content_type: Type of content (books, videos, tips, etc.)
        content_id: Optional content ID for folder organization
    
    Returns:
        List of relative URLs for saved files
    """
    handler = get_file_handler()
    
    # Get configuration for file type
    config = FILE_TYPE_CONFIGS.get(file_type, FILE_TYPE_CONFIGS["images"])
    
    # Validate files
    valid_files, errors = handler.validate_files(
        files, 
        config["allowed_types"], 
        config["max_size"], 
        config["max_files"]
    )
    
    if errors:
        raise HTTPException(
            status_code=400, 
            detail=f"File validation errors: {'; '.join(errors)}"
        )
    
    # Save files
    return handler.save_multiple_files(valid_files, content_type, content_id, file_type)
