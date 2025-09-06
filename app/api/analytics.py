from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.session import SessionLocal
from app.models.blog import Video, VideoViewSession
from app.schemas.blog import VideoViewTrackRequest, VideoViewTrackResponse
from typing import Dict, Any
import time
from collections import defaultdict

router = APIRouter()

# In-memory cache for view counts (for optimization)
view_count_cache = defaultdict(int)
last_flush_time = time.time()
FLUSH_INTERVAL = 300  # 5 minutes

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def should_count_view(watch_time: float, duration: float, percentage: float) -> bool:
    """
    Apply smart view counting rules:
    - If duration < 15s → count only if percentage >= 90%
    - If duration >= 15s → count if watchTime >= 30s OR percentage >= 50%
    """
    if duration < 15:
        return percentage >= 90.0
    else:
        return watch_time >= 30.0 or percentage >= 50.0

def flush_view_counts_to_db(db: Session):
    """Flush cached view counts to database"""
    global view_count_cache, last_flush_time
    
    if not view_count_cache:
        return
    
    try:
        # For now, just log the counts since view_count column doesn't exist
        for video_id, count_increment in view_count_cache.items():
            print(f"Video {video_id} would have view count incremented by {count_increment}")
        
        # Clear cache after logging
        view_count_cache.clear()
        last_flush_time = time.time()
        print(f"Logged view counts at {time.time()} (view_count column not available)")
    except Exception as e:
        print(f"Error logging view counts: {str(e)}")

@router.post("/video-view", response_model=VideoViewTrackResponse)
async def track_video_view(
    request: VideoViewTrackRequest,
    db: Session = Depends(get_db)
):
    """
    Track video view with smart counting rules and deduplication
    """
    try:
        # Validate video exists - use a simple query without view_count
        video = db.query(Video.id, Video.title).filter(Video.id == request.videoId).first()
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video not found"
            )
        
        # Check if view should be counted based on smart rules
        if not should_count_view(request.watchTime, request.duration, request.percentage):
            return VideoViewTrackResponse(
                success=True,
                message="View criteria not met",
                viewCount=0  # Default to 0 since view_count column doesn't exist yet
            )
        
        # Check for duplicate view (sessionId + videoId combination)
        existing_session = db.query(VideoViewSession).filter(
            VideoViewSession.session_id == request.sessionId,
            VideoViewSession.video_id == request.videoId
        ).first()
        
        if existing_session:
            return VideoViewTrackResponse(
                success=True,
                message="View already tracked for this session",
                viewCount=0  # Default to 0 since view_count column doesn't exist yet
            )
        
        # Create new view session record
        try:
            view_session = VideoViewSession(
                session_id=request.sessionId,
                video_id=request.videoId
            )
            db.add(view_session)
            db.commit()
        except IntegrityError:
            # Handle race condition where another request created the same session
            db.rollback()
            return VideoViewTrackResponse(
                success=True,
                message="View already tracked for this session",
                viewCount=0  # Default to 0 since view_count column doesn't exist yet
            )
        
        # Add to cache for batch processing
        view_count_cache[request.videoId] += 1
        
        # Check if we should flush cache to database
        current_time = time.time()
        if current_time - last_flush_time >= FLUSH_INTERVAL:
            flush_view_counts_to_db(db)
        
        return VideoViewTrackResponse(
            success=True,
            message="View tracked successfully",
            viewCount=view_count_cache[request.videoId]  # Return cached count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to track video view: {str(e)}"
        )

@router.get("/video-view/flush-cache")
async def flush_view_cache(db: Session = Depends(get_db)):
    """
    Manual endpoint to flush view count cache to database
    (useful for testing or manual cache management)
    """
    try:
        flush_view_counts_to_db(db)
        return {"success": True, "message": "View count cache logged successfully (view_count column not available)"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to flush cache: {str(e)}"
        )