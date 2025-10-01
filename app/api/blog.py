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
from app.utils.file_handler import get_file_handler, validate_and_save_files, MultipleFileHandler

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
    # Support both single and multiple files for backward compatibility
    pdf: Optional[UploadFile] = FastAPIFile(None),
    pdfs: List[UploadFile] = FastAPIFile([]),  # Multiple PDFs
    images: List[UploadFile] = FastAPIFile([]),  # Multiple images
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
    """Create a new book with multiple file uploads (PDFs and images)"""
    
    # Convert string values to appropriate types
    rating_float = float(rating) if rating else 0.0
    pages_int = int(pages) if pages else None
    price_float = float(price) if price else None
    publication_year_int = int(publication_year) if publication_year else None
    
    # Handle file uploads
    pdf_urls = []
    image_urls = []
    
    try:
        # Handle single PDF (backward compatibility)
        if pdf and pdf.filename:
            handler = get_file_handler()
            single_pdf_url = await handler.save_single_file(pdf, "books", None, "pdf")
            pdf_urls.append(single_pdf_url)
        
        # Handle multiple PDFs
        if pdfs:
            pdf_urls.extend(validate_and_save_files(pdfs, "documents", "books"))
        
        # Handle multiple images
        if images:
            image_urls.extend(validate_and_save_files(images, "images", "books"))
        
        # Create Book record
        book = Book(
            title=title,
            author=author,
            summary=summary,
            isbn=isbn,
            # Backward compatibility - use first file if available
            image_url=image_urls[0] if image_urls else None,
            pdf_url=pdf_urls[0] if pdf_urls else None,
            # New fields for multiple files
            image_urls=image_urls if image_urls else None,
            pdf_urls=pdf_urls if pdf_urls else None,
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
        
        # Update file paths with content ID after book is created
        if book.id:
            handler = get_file_handler()
            # Move files to content-specific folders
            updated_image_urls = []
            updated_pdf_urls = []
            
            for i, url in enumerate(image_urls):
                try:
                    old_path = url.replace("/static/", "app/static/")
                    new_folder = handler.create_content_folder("books", book.id)
                    filename = os.path.basename(old_path)
                    new_path = os.path.join(new_folder, filename)
                    
                    if os.path.exists(old_path):
                        os.rename(old_path, new_path)
                        updated_image_urls.append(new_path.replace("app/static/", "/static/"))
                except Exception as e:
                    print(f"Warning: Could not move image file: {str(e)}")
                    updated_image_urls.append(url)
            
            for i, url in enumerate(pdf_urls):
                try:
                    old_path = url.replace("/static/", "app/static/")
                    new_folder = handler.create_content_folder("books", book.id)
                    filename = os.path.basename(old_path)
                    new_path = os.path.join(new_folder, filename)
                    
                    if os.path.exists(old_path):
                        os.rename(old_path, new_path)
                        updated_pdf_urls.append(new_path.replace("app/static/", "/static/"))
                except Exception as e:
                    print(f"Warning: Could not move PDF file: {str(e)}")
                    updated_pdf_urls.append(url)
            
            # Update book with final URLs
            book.image_urls = updated_image_urls if updated_image_urls else None
            book.pdf_urls = updated_pdf_urls if updated_pdf_urls else None
            book.image_url = updated_image_urls[0] if updated_image_urls else None
            book.pdf_url = updated_pdf_urls[0] if updated_pdf_urls else None
            db.commit()
        
        return book
        
    except Exception as e:
        # Cleanup files on error
        handler = get_file_handler()
        handler.cleanup_files(pdf_urls + image_urls)
        raise HTTPException(status_code=500, detail=f"Failed to create book: {str(e)}")

@router.post("/tips", response_model=Dict[str, Any], dependencies=[Depends(require_role("admin"))])
async def create_tip(
    title: str = Form(...),
    content: str = Form(...),
    category: str = Form("general"),
    # Support both single and multiple files for backward compatibility
    image: Optional[UploadFile] = FastAPIFile(None),
    images: List[UploadFile] = FastAPIFile([]),  # Multiple images
    descriptions: List[str] = Form([]),  # Multiple descriptions
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Create a new tip (VastuTip) with multiple images and descriptions"""
    
    # Handle file uploads
    image_urls = []
    
    try:
        # Handle single image (backward compatibility)
        if image and image.filename:
            handler = get_file_handler()
            single_image_url = await handler.save_single_file(image, "tips", None, "image")
            image_urls.append(single_image_url)
        
        # Handle multiple images
        if images:
            image_urls.extend(validate_and_save_files(images, "images", "tips"))
        
        # Create VastuTip record
        new_tip = VastuTip(
            title=title,
            description=content,
            details=content,
            category=category or "general",
            # Backward compatibility - use first image if available
            image_url=image_urls[0] if image_urls else None,
            # New fields for multiple files
            image_urls=image_urls if image_urls else None,
            descriptions=descriptions if descriptions else None,
            is_published=True,
        )
        db.add(new_tip)
        db.commit()
        db.refresh(new_tip)
        
        # Update file paths with content ID after tip is created
        if new_tip.id and image_urls:
            handler = get_file_handler()
            # Move files to content-specific folders
            updated_image_urls = []
            
            for i, url in enumerate(image_urls):
                try:
                    old_path = url.replace("/static/", "app/static/")
                    new_folder = handler.create_content_folder("tips", new_tip.id)
                    filename = os.path.basename(old_path)
                    new_path = os.path.join(new_folder, filename)
                    
                    if os.path.exists(old_path):
                        os.rename(old_path, new_path)
                        updated_image_urls.append(new_path.replace("app/static/", "/static/"))
                except Exception as e:
                    print(f"Warning: Could not move image file: {str(e)}")
                    updated_image_urls.append(url)
            
            # Update tip with final URLs
            new_tip.image_urls = updated_image_urls if updated_image_urls else None
            new_tip.image_url = updated_image_urls[0] if updated_image_urls else None
            db.commit()

        return {
            "id": new_tip.id,
            "title": new_tip.title,
            "content": new_tip.description,
            "category": new_tip.category,
            "image": new_tip.image_url,  # safe string path (backward compatibility)
            "images": new_tip.image_urls,  # multiple images
            "descriptions": new_tip.descriptions,  # multiple descriptions
        }
        
    except Exception as e:
        # Cleanup files on error
        handler = get_file_handler()
        handler.cleanup_files(image_urls)
        raise HTTPException(status_code=500, detail=f"Failed to create tip: {str(e)}")
    
@router.get("/videos",response_model=List[VideoRead])
def read_videos(
    category: Optional[str] = None,
    db: Session = Depends(get_db), 
    request: Request = None
):
    """Get blog videos (non-tour videos) with optional category filtering"""
    # Rate limiting and logging
    if request:
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent", "Unknown")
        check_rate_limit(client_ip)
        print(f"Blog video request from IP: {client_ip}, User-Agent: {user_agent[:50]}... at {datetime.utcnow()}")
    
    def fetch_blog_videos():
        try:
            # Query published videos excluding tour videos
            query = db.query(Video).filter(
                Video.is_published == True,
                Video.category != 'tour'  # Exclude tour videos
            )
            
            if category:
                query = query.filter(Video.category == category)
                cache_key = f"blog_videos_{category}"
            else:
                cache_key = "blog_videos"
            
            videos = query.all()
            
            # Ensure URLs are populated for all videos
            for video in videos:
                if not video.url:
                    video.url = video.get_video_url(db)
            
            print(f"Returning {len(videos)} blog videos" + (f" with category '{category}'" if category else ""))
            return videos
        except Exception as e:
            print(f"Error in read_blog_videos: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error retrieving blog videos: {str(e)}")
    
    cache_key = f"blog_videos_{category}" if category else "blog_videos"
    return get_cached_data(cache_key, fetch_blog_videos)

@router.get("/tour-videos", response_model=List[VideoRead])
def read_tour_videos(
    db: Session = Depends(get_db), 
    request: Request = None
):
    """Get tour videos only (admin side videos)"""
    # Rate limiting and logging
    if request:
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent", "Unknown")
        check_rate_limit(client_ip)
        print(f"Tour video request from IP: {client_ip}, User-Agent: {user_agent[:50]}... at {datetime.utcnow()}")
    
    def fetch_tour_videos():
        try:
            # Query only tour videos
            videos = db.query(Video).filter(
                Video.is_published == True,
                Video.category == 'tour'
            ).all()
            
            # Ensure URLs are populated for all videos
            for video in videos:
                if not video.url:
                    video.url = video.get_video_url(db)
            
            print(f"Returning {len(videos)} tour videos")
            return videos
        except Exception as e:
            print(f"Error in read_tour_videos: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error retrieving tour videos: {str(e)}")
    
    return get_cached_data("tour_videos", fetch_tour_videos)

@router.post("/videos", response_model=VideoRead)
async def create_video(
    title: str = Form(...),
    description: str = Form(...),
    # Support both single and multiple files for backward compatibility
    video: Optional[UploadFile] = FastAPIFile(None),
    videos: List[UploadFile] = FastAPIFile([]),  # Multiple videos
    thumbnail: Optional[UploadFile] = FastAPIFile(None),
    thumbnails: List[UploadFile] = FastAPIFile([]),  # Multiple thumbnails
    category: str = Form(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Create a new video with multiple video files and thumbnails"""
    
    # Handle file uploads
    video_urls = []
    thumbnail_urls = []
    
    try:
        # Handle single video (backward compatibility)
        if video and video.filename:
            # Validate single video
            if not video.content_type.startswith("video/"):
                raise HTTPException(status_code=400, detail="Invalid video file type")
            
            handler = get_file_handler()
            single_video_url = await handler.save_single_file(video, "videos", None, "video")
            video_urls.append(single_video_url)
        
        # Handle multiple videos
        if videos:
            video_urls.extend(validate_and_save_files(videos, "videos", "videos"))
        
        # Handle single thumbnail (backward compatibility)
        if thumbnail and thumbnail.filename:
            # Validate single thumbnail
            if not thumbnail.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail="Invalid thumbnail file type")
            
            handler = get_file_handler()
            single_thumbnail_url = await handler.save_single_file(thumbnail, "videos", None, "thumbnail")
            thumbnail_urls.append(single_thumbnail_url)
        
        # Handle multiple thumbnails
        if thumbnails:
            thumbnail_urls.extend(validate_and_save_files(thumbnails, "images", "videos"))
        
        # Get video duration from first video
        duration = None
        if video_urls:
            try:
                from app.utils.helpers import get_video_duration
                first_video_path = video_urls[0].replace("/static/", "app/static/")
                duration = get_video_duration(first_video_path)
            except Exception as e:
                print(f"Could not get video duration: {str(e)}")
                duration = "00:00"
        
        # Create Video entry
        new_video = Video(
            title=title,
            description=description,
            # Backward compatibility - use first file if available
            url=video_urls[0] if video_urls else None,
            thumbnail_url=thumbnail_urls[0] if thumbnail_urls else None,
            # New fields for multiple files
            video_urls=video_urls if video_urls else None,
            thumbnail_urls=thumbnail_urls if thumbnail_urls else None,
            category=category,
            video_type="blob",
            duration=duration,
            is_published=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(new_video)
        db.commit()
        db.refresh(new_video)
        
        # Update file paths with content ID after video is created
        if new_video.id:
            handler = get_file_handler()
            # Move files to content-specific folders
            updated_video_urls = []
            updated_thumbnail_urls = []
            
            for i, url in enumerate(video_urls):
                try:
                    old_path = url.replace("/static/", "app/static/")
                    new_folder = handler.create_content_folder("videos", new_video.id)
                    filename = os.path.basename(old_path)
                    new_path = os.path.join(new_folder, filename)
                    
                    if os.path.exists(old_path):
                        os.rename(old_path, new_path)
                        updated_video_urls.append(new_path.replace("app/static/", "/static/"))
                except Exception as e:
                    print(f"Warning: Could not move video file: {str(e)}")
                    updated_video_urls.append(url)
            
            for i, url in enumerate(thumbnail_urls):
                try:
                    old_path = url.replace("/static/", "app/static/")
                    new_folder = handler.create_content_folder("videos", new_video.id)
                    filename = os.path.basename(old_path)
                    new_path = os.path.join(new_folder, filename)
                    
                    if os.path.exists(old_path):
                        os.rename(old_path, new_path)
                        updated_thumbnail_urls.append(new_path.replace("app/static/", "/static/"))
                except Exception as e:
                    print(f"Warning: Could not move thumbnail file: {str(e)}")
                    updated_thumbnail_urls.append(url)
            
            # Update video with final URLs
            new_video.video_urls = updated_video_urls if updated_video_urls else None
            new_video.thumbnail_urls = updated_thumbnail_urls if updated_thumbnail_urls else None
            new_video.url = updated_video_urls[0] if updated_video_urls else None
            new_video.thumbnail_url = updated_thumbnail_urls[0] if updated_thumbnail_urls else None
            db.commit()
        
        # Save videos as MediaAssets
        for i, url in enumerate(video_urls):
            try:
                video_path = url.replace("/static/", "app/static/")
                filename = os.path.basename(video_path)
                
                # Read video data for MediaAsset
                with open(video_path, "rb") as f:
                    video_data = f.read()
                
                media_asset = MediaAsset(
                    filename=filename,
                    original_name=f"video_{i+1}.mp4",  # Default name
                    file_path=video_path,
                    file_size=len(video_data),
                    mime_type="video/mp4",  # Default MIME type
                    asset_type="video",
                    content_type="video",
                    content_id=new_video.id,
                    file_data=video_data,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(media_asset)
            except Exception as e:
                print(f"Warning: Could not save media asset for video {i+1}: {str(e)}")
        
        db.commit()
        
        # Invalidate cache when new video is created
        if new_video.category == 'tour':
            invalidate_cache("tour_videos")
        else:
            invalidate_cache("blog_videos")
        
        return new_video
        
    except Exception as e:
        # Cleanup files on error
        handler = get_file_handler()
        handler.cleanup_files(video_urls + thumbnail_urls)
        raise HTTPException(status_code=500, detail=f"Failed to create video: {str(e)}")
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
