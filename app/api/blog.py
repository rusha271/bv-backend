from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File as FastAPIFile, Form, status, Request
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.blog import BlogPost , VastuTip, Book, Video, MediaAsset
from app.schemas.blog import BlogPostCreate, BlogPostUpdate, BlogPostRead, BookRead , VideoRead , BookCreate , VideoCreate
from app.core.security import get_current_admin_user, get_current_user, require_role
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

# Simple rate limiting
request_times = defaultdict(list)
RATE_LIMIT_WINDOW = 60  # 60 seconds
RATE_LIMIT_MAX_REQUESTS = 10  # Max 10 requests per minute

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
def list_blog_posts(db: Session = Depends(get_db)):
    return db.query(Book).filter(Book.published == True).all()


@router.post("/books", response_model=BookCreate)
async def create_book(
    title: str = Form(...),
    author: str = Form(...),
    summary: str = Form(...),
    pdf: UploadFile = FastAPIFile(...),
    rating: float = Form(None),
    pages: int = Form(None),
    price: float = Form(None),
    publication_year: int = Form(None),
    publisher: str = Form(None),
    category: str = Form(None),
    isbn: str = Form(None),
    db: Session = Depends(get_db)
):
    """Create a new book with PDF upload"""
    # Save PDF file
    upload_dir = "app/static/books"
    os.makedirs(upload_dir, exist_ok=True)
    file_ext = os.path.splitext(pdf.filename)[1]
    file_name = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(upload_dir, file_name)
    with open(file_path, "wb") as f:
        f.write(await pdf.read())
    # Create Book record
    book = Book(
        title=title,
        author=author,
        summary=summary,
        isbn=isbn,
        image_url=f"/static/books/{file_name}",
        rating=rating or 0.0,
        pages=pages,
        publication_year=publication_year,
        publisher=publisher,
        price=price,
        is_available=True,
        is_published=True
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return book

@router.post("/tips", response_model=Dict[str, Any], dependencies=[Depends(require_role("admin"))])
def create_tip(
    tip: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Create a new tip (VastuTip)"""
    title = tip.get("title")
    content = tip.get("content")
    category = tip.get("category")
    image = tip.get("image")
    if not all([title, content, image]):
        raise HTTPException(status_code=400, detail="Missing required fields")
    new_tip = VastuTip(
        title=tip.title,
        description=tip.content,
        details=tip.content,
        category=tip.category or "general",
        image_url=str(tip.image),
        is_published=True,
        # author_id=int(current_user.sub)  # enable this if author tracking is required
    )
    db.add(new_tip)
    db.commit()
    db.refresh(new_tip)
    return {
        "id": new_tip.id,
        "title": new_tip.title,
        "content": new_tip.description,
        "category": new_tip.category,
        "image": new_tip.image_url,
    }

@router.get("/videos",response_model=List[VideoRead])
def read_videos(db: Session = Depends(get_db), request: Request = None):
    """Get all published videos with rate limiting"""
    # Rate limiting and logging
    if request:
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent", "Unknown")
        check_rate_limit(client_ip)
        print(f"Video request from IP: {client_ip}, User-Agent: {user_agent[:50]}... at {datetime.utcnow()}")
    
    videos = db.query(Video).filter(Video.is_published == True).all()
    print(f"Returning {len(videos)} videos")
    return videos

@router.post("/videos", response_model=VideoRead)
async def create_video(
    title: str = Form(...),
    description: str = Form(...),
    video: UploadFile = FastAPIFile(...),
    thumbnail: UploadFile = FastAPIFile(...),
    category: Optional[str] = Form(None),
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
    thumbnail_dir = "app/static/thumbnails"
    os.makedirs(thumbnail_dir, exist_ok=True)

    thumbnail_ext = os.path.splitext(thumbnail.filename)[1] or mimetypes.guess_extension(thumbnail.content_type) or ".png"
    thumbnail_name = f"{uuid.uuid4()}{thumbnail_ext}"
    thumbnail_path = os.path.join(thumbnail_dir, thumbnail_name)

    try:
        with open(thumbnail_path, "wb") as f:
            f.write(thumbnail_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save thumbnail: {str(e)}")

    # --------- Create Video entry ---------
    try:
        new_video = Video(
            title=title,
            description=description,
            category=category,
            thumbnail_url=f"/static/thumbnails/{thumbnail_name}",
            video_type="blob",
            is_published=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            # author_id=int(current_user.sub)
        )
        db.add(new_video)
        db.commit()
        db.refresh(new_video)
    except Exception as e:
        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)
        raise HTTPException(status_code=500, detail=f"Failed to save video: {str(e)}")

    # --------- Save video as MediaAsset ---------
    try:
        video_ext = os.path.splitext(video.filename)[1] or mimetypes.guess_extension(video.content_type) or ".mp4"
        video_name = f"{uuid.uuid4()}{video_ext}"

        media_asset = MediaAsset(
            filename=video_name,
            original_name=video.filename,
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
