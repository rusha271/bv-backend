from fastapi import APIRouter, Depends, UploadFile, File as FastAPIFile, HTTPException, status, Response, Form
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.vastu import Video, MediaAsset
from app.models.user import User
from app.schemas.blog import VideoCreate, VideoRead, VideoUpdate
from app.core.security import get_current_user, require_role
from app.utils.helpers import validate_video_upload, get_video_duration, generate_video_thumbnail
import os
from uuid import uuid4
from typing import List, Optional
from datetime import datetime

UPLOAD_DIR = "app/static/videos"
THUMBNAIL_DIR = "app/static/thumbnails"

# Create directories if they don't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(THUMBNAIL_DIR, exist_ok=True)

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=VideoRead)
async def create_video(
    title: str = Form(...),
    description: str = Form(...),
    video: UploadFile = FastAPIFile(...),
    thumbnail: UploadFile = FastAPIFile(None),
    category: str = Form(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Create a new video with file upload and optional thumbnail"""
    # Save video file
    file_ext = os.path.splitext(video.filename)[1]
    video_name = f"{uuid4()}{file_ext}"
    video_path = os.path.join(UPLOAD_DIR, video_name)
    with open(video_path, "wb") as f:
        f.write(await video.read())
    # Save thumbnail if provided
    thumbnail_url = None
    if thumbnail:
        thumb_ext = os.path.splitext(thumbnail.filename)[1]
        thumb_name = f"{uuid4()}{thumb_ext}"
        thumb_path = os.path.join(THUMBNAIL_DIR, thumb_name)
        with open(thumb_path, "wb") as f:
            f.write(await thumbnail.read())
        thumbnail_url = f"/static/thumbnails/{thumb_name}"
    # Get video duration (optional, if you have a helper)
    duration = None
    try:
        duration = get_video_duration(video_path)
    except Exception:
        pass
    # Create Video record
    video_obj = Video(
        title=title,
        description=description,
        url=f"/static/videos/{video_name}",
        video_type="direct",
        thumbnail_url=thumbnail_url,
        duration=duration,
        category=category,
        is_published=True
    )
    db.add(video_obj)
    db.commit()
    db.refresh(video_obj)
    # Create media asset record
    file_size = os.path.getsize(video_path)
    media_asset = MediaAsset(
        filename=video_name,
        original_name=video.filename,
        file_path=video_path,
        file_size=file_size,
        mime_type=video.content_type,
        asset_type="video",
        content_type="video",
        content_id=video_obj.id,
        is_active=True
    )
    db.add(media_asset)
    db.commit()
    return video_obj

@router.get("/", response_model=List[VideoRead])
def get_videos(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all videos with optional filtering
    """
    query = db.query(Video).filter(Video.is_published == True)
    
    if category:
        query = query.filter(Video.category == category)
    
    videos = query.offset(skip).limit(limit).all()
    return videos

@router.get("/{video_id}", response_model=VideoRead)
def get_video(video_id: int, db: Session = Depends(get_db)):
    """
    Get a specific video by ID
    """
    video = db.query(Video).filter(Video.id == video_id, Video.is_published == True).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video

@router.put("/{video_id}", response_model=VideoRead)
def update_video(
    video_id: int,
    video_update: VideoUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update video information
    """
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Update fields
    update_data = video_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(video, field, value)
    
    video.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(video)
    return video

@router.delete("/{video_id}")
def delete_video(
    video_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a video (soft delete by setting is_published to False)
    """
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Soft delete
    video.is_published = False
    video.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Video deleted successfully"}

@router.post("/{video_id}/increment-views")
def increment_views(video_id: int, db: Session = Depends(get_db)):
    """
    Increment video view count
    """
    video = db.query(Video).filter(Video.id == video_id, Video.is_published == True).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    video.views += 1
    db.commit()
    
    return {"views": video.views}

@router.get("/serve/{filename}")
def serve_video(filename: str):
    """
    Serve video files
    """
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Video file not found")
    
    # Determine content type based on file extension
    ext = os.path.splitext(filename)[1].lower()
    content_types = {
        '.mp4': 'video/mp4',
        '.avi': 'video/x-msvideo',
        '.mov': 'video/quicktime',
        '.wmv': 'video/x-ms-wmv',
        '.flv': 'video/x-flv',
        '.webm': 'video/webm',
        '.mkv': 'video/x-matroska'
    }
    content_type = content_types.get(ext, 'video/mp4')
    
    with open(file_path, "rb") as f:
        content = f.read()
    
    return Response(content, media_type=content_type)

@router.get("/thumbnails/{filename}")
def serve_thumbnail(filename: str):
    """
    Serve video thumbnails
    """
    file_path = os.path.join(THUMBNAIL_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    
    with open(file_path, "rb") as f:
        content = f.read()
    
    return Response(content, media_type="image/jpeg") 