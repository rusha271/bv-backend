from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File as FastAPIFile, Form, status, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.blog import BlogPost , VastuTip, Book, Video, MediaAsset
from app.schemas.blog import BlogPostCreate, BlogPostUpdate, BlogPostRead, BookRead , VideoRead , BookCreate , VideoCreate
from app.core.security import get_current_admin_user, get_current_user, require_role, rate_limit_dependency, security_validation_dependency
from typing import List, Dict, Any, Optional
import os
import requests
from urllib.parse import urlparse
import uuid
import mimetypes
import time
from collections import defaultdict

from app.schemas.vastu import VastuTipCreate, VastuTipRead, VastuTipUpdate
from app.services.vastu_service import create_vastu_tip, delete_vastu_tip, get_all_vastu_tips, get_vastu_tip_by_id, update_vastu_tip

router = APIRouter()

# Simple rate limiting and caching
request_times = defaultdict(list)
RATE_LIMIT_WINDOW = 60  # 60 seconds
RATE_LIMIT_MAX_REQUESTS = 10  # Max 10 requests per minute

# Cache for frequently accessed data
_cache = {}
_cache_ttl = 300  # 5 minutes cache TTL

def check_rate_limit(client_ip: str):
    """Simple rate limiting function"""
    current_time = time.time()
    # Clean old requests
    request_times[client_ip] = [t for t in request_times[client_ip] if current_time - t < RATE_LIMIT_WINDOW]
    
    # Check if too many requests
    if len(request_times[client_ip]) >= RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(
            status_code=429, 
            detail="Too many requests. Please wait before making more requests."
        )
    
    # Add current request
    request_times[client_ip].append(current_time)

def get_cached_data(key: str, fetch_func, *args, **kwargs):
    """Simple cache implementation"""
    current_time = time.time()
    
    # Check if data exists in cache and is not expired
    if key in _cache:
        data, timestamp = _cache[key]
        if current_time - timestamp < _cache_ttl:
            return data
    
    # Fetch fresh data
    data = fetch_func(*args, **kwargs)
    _cache[key] = (data, current_time)
    return data

def invalidate_cache(*keys):
    """Invalidate specific cache keys"""
    for key in keys:
        _cache.pop(key, None)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# # Blog content endpoints
# @router.get("/blog", response_model=list[BlogPostRead])
# def list_blog_posts(db: Session = Depends(get_db)):
#     return db.query(BlogPost).filter(BlogPost.published == True).all()

# @router.post("/blog", response_model=BlogPostRead, dependencies=[Depends(require_role("admin"))])
# def create_blog_post(post: BlogPostCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
#     blog = BlogPost(**post.dict(), author_id=int(current_user.sub))
#     db.add(blog)
#     db.commit()
#     db.refresh(blog)
#     return blog

# @router.put("/blog/{id}", response_model=BlogPostRead, dependencies=[Depends(require_role("admin"))])
# def update_blog_post(id: int, post: BlogPostUpdate, db: Session = Depends(get_db)):
#     blog = db.query(BlogPost).filter(BlogPost.id == id).first()
#     if not blog:
#         raise HTTPException(status_code=404, detail="Blog post not found")
#     for field, value in post.dict(exclude_unset=True).items():
#         setattr(blog, field, value)
#     db.commit()
#     db.refresh(blog)
#     return blog

# @router.delete("/blog/{id}", dependencies=[Depends(require_role("admin"))])
# def delete_blog_post(id: int, db: Session = Depends(get_db)):
#     blog = db.query(BlogPost).filter(BlogPost.id == id).first()
#     if not blog:
#         raise HTTPException(status_code=404, detail="Blog post not found")
#     db.delete(blog)
#     db.commit()
#     return {"ok": True}

@router.get("/books",response_model=List[BookRead])
def list_books(
    db: Session = Depends(get_db),
    _: str = Depends(rate_limit_dependency("general")),
    __: bool = Depends(security_validation_dependency())
):
    """Get all published books with caching"""
    def fetch_books():
        return db.query(Book).filter(Book.is_published == True).all()
    
    return get_cached_data("books", fetch_books)


@router.post("/books", response_model=BookRead)
async def create_book(
    title: str = Form(...),
    author: str = Form(...),
    summary: str = Form(...),
    pdf: UploadFile = FastAPIFile(...),
    rating: str = Form(None),
    pages: str = Form(None),
    price: str = Form(None),
    publication_year: str = Form(None),
    publisher: str = Form(None),
    category: str = Form(None),
    isbn: str = Form(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_user)
):
    """Create a new book with PDF upload"""
    # Save PDF file
    upload_dir = "app/static/media/books"
    os.makedirs(upload_dir, exist_ok=True)
    file_ext = os.path.splitext(pdf.filename)[1]
    file_name = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(upload_dir, file_name)
    with open(file_path, "wb") as f:
        f.write(await pdf.read())
    
    # Convert string values to appropriate types
    rating_float = float(rating) if rating else 0.0
    pages_int = int(pages) if pages else None
    price_float = float(price) if price else None
    publication_year_int = int(publication_year) if publication_year else None
    
    # Create Book record
    book = Book(
        title=title,
        author=author,
        summary=summary,
        isbn=isbn,
        image_url=f"/static/media/books/{file_name}",
        rating=rating_float,
        pages=pages_int,
        publication_year=publication_year_int,
        publisher=publisher,
        price=price_float,
        is_available=True,
        is_published=True
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return book

@router.post("/tips", response_model=Dict[str, Any], dependencies=[Depends(require_role("admin"))])
async def create_tip(
    title: str = Form(...),
    content: str = Form(...),
    category: str = Form("general"),
    image: UploadFile = FastAPIFile(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Create a new tip (VastuTip)"""

    # Save uploaded image to disk
    upload_dir = "app/static/tips"
    os.makedirs(upload_dir, exist_ok=True)

    file_ext = os.path.splitext(image.filename)[1] or ".jpg"
    file_name = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(upload_dir, file_name)

    with open(file_path, "wb") as f:
        f.write(await image.read())

    # Only save the relative path in DB (not bytes, not base64)
    new_tip = VastuTip(
        title=title,
        description=content,
        details=content,
        category=category or "general",
        image_url=f"/static/tips/{file_name}",
        is_published=True,
    )
    db.add(new_tip)
    db.commit()
    db.refresh(new_tip)

    return {
        "id": new_tip.id,
        "title": new_tip.title,
        "content": new_tip.description,
        "category": new_tip.category,
        "image": new_tip.image_url,  # safe string path
    }
    
@router.get("/videos",response_model=List[VideoRead])
def read_videos(db: Session = Depends(get_db), request: Request = None):
    """Get all published videos with rate limiting - TOUR FUNCTIONALITY ONLY"""
    # Rate limiting and logging
    if request:
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent", "Unknown")
        check_rate_limit(client_ip)
        print(f"Video request from IP: {client_ip}, User-Agent: {user_agent[:50]}... at {datetime.utcnow()}")
    
    def fetch_tour_videos():
        try:
            # Query videos with explicit field selection to avoid any column issues
            videos = db.query(
                Video.id,
                Video.title,
                Video.description,
                Video.url,
                Video.video_type,
                Video.thumbnail_url,
                Video.duration,
                Video.views,
                Video.category,
                Video.is_published,
                Video.created_at,
                Video.updated_at
            ).filter(
                Video.is_published == True,
                Video.category == 'tour'
            ).all()
            
            # Convert to Video objects for consistency
            video_objects = []
            for video_data in videos:
                video_obj = Video()
                video_obj.id = video_data.id
                video_obj.title = video_data.title
                video_obj.description = video_data.description
                video_obj.url = video_data.url
                video_obj.video_type = video_data.video_type
                video_obj.thumbnail_url = video_data.thumbnail_url
                video_obj.duration = video_data.duration
                video_obj.views = video_data.views
                video_obj.category = video_data.category
                video_obj.is_published = video_data.is_published
                video_obj.created_at = video_data.created_at
                video_obj.updated_at = video_data.updated_at
                
                # Ensure URL is populated
                if not video_obj.url:
                    video_obj.url = video_obj.get_video_url(db)
                
                video_objects.append(video_obj)
            
            print(f"Returning {len(video_objects)} tour videos only")
            return video_objects
        except Exception as e:
            print(f"Error in read_videos: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error retrieving videos: {str(e)}")
    
    return get_cached_data("tour_videos", fetch_tour_videos)

@router.post("/videos", response_model=VideoRead)
async def create_video(
    title: str = Form(...),
    description: str = Form(...),
    video: UploadFile = FastAPIFile(...),
    thumbnail: UploadFile = FastAPIFile(...),
    category: str = Form(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    print("Received data:", title, description, video.filename, thumbnail.filename, category)

    # --------- Validation ---------
    if not video.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Invalid video file type")

    if not thumbnail.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid thumbnail file type")

    # Read files in memory
    video_data = await video.read()
    thumbnail_data = await thumbnail.read()

    # Check file sizes
    max_video_size = 100 * 1024 * 1024
    max_thumbnail_size = 5 * 1024 * 1024
    if len(video_data) > max_video_size:
        raise HTTPException(status_code=400, detail="Video file size exceeds 100MB")
    if len(thumbnail_data) > max_thumbnail_size:
        raise HTTPException(status_code=400, detail="Thumbnail file size exceeds 5MB")

    # --------- Save thumbnail ---------
    thumbnail_dir = "app/static/media/thumbnails"
    os.makedirs(thumbnail_dir, exist_ok=True)

    thumbnail_ext = os.path.splitext(thumbnail.filename)[1] or mimetypes.guess_extension(thumbnail.content_type) or ".png"
    thumbnail_name = f"{uuid.uuid4()}{thumbnail_ext}"
    thumbnail_path = os.path.join(thumbnail_dir, thumbnail_name)

    try:
        with open(thumbnail_path, "wb") as f:
            f.write(thumbnail_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save thumbnail: {str(e)}")

    # --------- Save video file to media directory ---------
    video_ext = os.path.splitext(video.filename)[1] or mimetypes.guess_extension(video.content_type) or ".mp4"
    video_name = f"{uuid.uuid4()}{video_ext}"
    
    video_dir = "app/static/media/videos"
    os.makedirs(video_dir, exist_ok=True)
    video_path = os.path.join(video_dir, video_name)
    with open(video_path, "wb") as f:
        f.write(video_data)

    # --------- Get video duration ---------
    duration = None
    try:
        from app.utils.helpers import get_video_duration
        duration = get_video_duration(video_path)
    except Exception as e:
        print(f"Could not get video duration: {str(e)}")
        duration = "00:00"

    # --------- Create Video entry ---------
    try:
        new_video = Video(
            title=title,
            description=description,
            url=f"/static/media/videos/{video_name}",
            category=category,
            thumbnail_url=f"/static/media/thumbnails/{thumbnail_name}",
            video_type="blob",
            duration=duration,
            is_published=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            # author_id=int(current_user.sub)
        )
        db.add(new_video)
        db.commit()
        db.refresh(new_video)
        
        # Invalidate cache when new video is created
        invalidate_cache("tour_videos")
    except Exception as e:
        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)
        if os.path.exists(video_path):
            os.remove(video_path)
        raise HTTPException(status_code=500, detail=f"Failed to save video: {str(e)}")

    # --------- Save video as MediaAsset ---------
    try:
        media_asset = MediaAsset(
            filename=video_name,
            original_name=video.filename,
            file_path=video_path,
            file_size=len(video_data),
            mime_type=video.content_type,
            asset_type="video",
            content_type="video",
            content_id=new_video.id,
            file_data=video_data,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(media_asset)
        db.commit()
    except Exception as e:
        db.delete(new_video)
        db.commit()
        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)
        if os.path.exists(video_path):
            os.remove(video_path)
        raise HTTPException(status_code=500, detail=f"Failed to save asset: {str(e)}")

    return new_video
# Vastu Tips endpoints
@router.post("/tips", response_model=VastuTipRead)
def create_vastu_tip_endpoint(
    tip: VastuTipCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """Create Vastu tip (admin only)"""
    return create_vastu_tip(db, tip,current_user)

@router.get("/tips", response_model=List[VastuTipRead])
def get_vastu_tips(
    category: Optional[str] = None,
    published_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get Vastu tips"""
    return get_all_vastu_tips(db, category, published_only)

@router.get("/tips/{tip_id}", response_model=VastuTipRead)
def get_vastu_tip(
    tip_id: int,
    db: Session = Depends(get_db)
):
    """Get specific Vastu tip"""
    tip = get_vastu_tip_by_id(db, tip_id)
    if not tip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vastu tip not found"
        )
    return tip

@router.put("/tips/{tip_id}", response_model=VastuTipRead)
def update_vastu_tip_endpoint(
    tip_id: int,
    tip_update: VastuTipUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """Update Vastu tip (admin only)"""
    tip = update_vastu_tip(db, tip_id, tip_update)
    if not tip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vastu tip not found"
        )
    return tip

@router.delete("/tips/{tip_id}")
def delete_vastu_tip_endpoint(
    tip_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """Delete Vastu tip (admin only)"""
    success = delete_vastu_tip(db, tip_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vastu tip not found"
        )
    return {"message": "Vastu tip deleted successfully"}

# Video serving endpoints
@router.get("/videos/serve/{filename}")
def serve_video(filename: str):
    """
    Serve video files from the media directory
    """
    video_dir = "app/static/media/videos"
    file_path = os.path.join(video_dir, filename)
    
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
    
    # Read and return the video file
    with open(file_path, "rb") as f:
        content = f.read()
    
    return Response(content, media_type=content_type)

@router.get("/videos/thumbnails/{filename}")
def serve_video_thumbnail(filename: str):
    """
    Serve video thumbnails from the media directory
    """
    thumbnail_dir = "app/static/media/thumbnails"
    file_path = os.path.join(thumbnail_dir, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    
    # Determine content type based on file extension
    ext = os.path.splitext(filename)[1].lower()
    content_types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }
    content_type = content_types.get(ext, 'image/jpeg')
    
    # Read and return the thumbnail file
    with open(file_path, "rb") as f:
        content = f.read()
    
    return Response(content, media_type=content_type)
