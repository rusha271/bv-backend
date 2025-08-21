from slugify import slugify
from fastapi import UploadFile, HTTPException
import os

ALLOWED_IMAGE_TYPES = ["image/png", "image/jpeg", "image/jpg"]
ALLOWED_VIDEO_TYPES = ["video/mp4", "video/avi", "video/mov", "video/wmv", "video/flv", "video/webm", "video/mkv"]
MAX_IMAGE_SIZE_MB = 10
MAX_VIDEO_SIZE_MB = 500  # 500MB for videos

def generate_slug(text: str) -> str:
    return slugify(text)

def validate_file_upload(file: UploadFile):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type.")
    file.file.seek(0, 2)  # Seek to end
    size = file.file.tell()
    file.file.seek(0)
    if size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 10MB).")

def validate_video_upload(file: UploadFile):
    """Validate video file upload"""
    if file.content_type not in ALLOWED_VIDEO_TYPES:
        raise HTTPException(status_code=400, detail="Invalid video file type. Allowed types: MP4, AVI, MOV, WMV, FLV, WebM, MKV")
    
    file.file.seek(0, 2)  # Seek to end
    size = file.file.tell()
    file.file.seek(0)
    
    if size > MAX_VIDEO_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"Video file too large (max {MAX_VIDEO_SIZE_MB}MB).")
    
    # Check file extension
    allowed_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv']
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Invalid video file extension.")

def get_video_duration(file_path: str) -> str:
    """Get video duration using ffprobe (requires ffmpeg to be installed)"""
    try:
        import subprocess
        result = subprocess.run([
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration', 
            '-of', 'default=noprint_wrappers=1:nokey=1', file_path
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            duration_seconds = float(result.stdout.strip())
            minutes = int(duration_seconds // 60)
            seconds = int(duration_seconds % 60)
            return f"{minutes:02d}:{seconds:02d}"
    except (ImportError, FileNotFoundError, subprocess.SubprocessError):
        pass
    
    return "00:00"  # Default if ffprobe not available

def generate_video_thumbnail(video_path: str, thumbnail_path: str) -> bool:
    """Generate thumbnail from video using ffmpeg"""
    try:
        import subprocess
        result = subprocess.run([
            'ffmpeg', '-i', video_path, '-ss', '00:00:01', '-vframes', '1', 
            '-vf', 'scale=320:240', thumbnail_path, '-y'
        ], capture_output=True)
        return result.returncode == 0
    except (ImportError, FileNotFoundError, subprocess.SubprocessError):
        return False 