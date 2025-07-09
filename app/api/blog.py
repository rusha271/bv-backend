from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.blog import BlogPost
from app.models.vastu import VastuTip, Book, Video, MediaAsset
from app.schemas.blog import BlogPostCreate, BlogPostUpdate, BlogPostRead
from app.schemas.content import BookRead, VideoRead, BookCreate, VideoCreate, BookUpdate, VideoUpdate
from app.core.security import get_current_user, require_role
from typing import List, Dict, Any
import os
import requests
from urllib.parse import urlparse
import uuid

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Blog content endpoints
@router.get("/tips", response_model=List[Dict[str, Any]])
def get_tips(db: Session = Depends(get_db)):
    """Get all tips"""
    # Sample tips data - replace with database queries
    tips_data = [
        {
            "id": 1,
            "title": "Vastu for Main Entrance",
            "content": "The main entrance should face north, east, or northeast for positive energy flow.",
            "category": "entrance",
            "image": "/images/tips/entrance.jpg"
        },
        {
            "id": 2,
            "title": "Kitchen Placement",
            "content": "Kitchen should be placed in the southeast direction for optimal health and prosperity.",
            "category": "kitchen",
            "image": "/images/tips/kitchen.jpg"
        },
        {
            "id": 3,
            "title": "Bedroom Vastu",
            "content": "Master bedroom should be in the southwest direction for stability and peace.",
            "category": "bedroom",
            "image": "/images/tips/bedroom.jpg"
        }
    ]
    return tips_data

@router.get("/books", response_model=List[Dict[str, Any]])
def get_books(db: Session = Depends(get_db)):
    """Get all books"""
    # Sample books data - replace with database queries
    books_data = [
        {
            "id": 1,
            "title": "Vastu Shastra: The Ancient Science of Architecture",
            "author": "Dr. Khushdeep Bansal",
            "summary": "A comprehensive guide to understanding and applying Vastu principles in modern architecture.",
            "image": "/images/books/vastu-shastra.jpg",
            "rating": 4.5,
            "pages": 320
        },
        {
            "id": 2,
            "title": "The Power of Vastu Living",
            "author": "Kathleen Cox",
            "summary": "Learn how ancient Vastu principles can transform your living space and life.",
            "image": "/images/books/power-of-vastu.jpg",
            "rating": 4.2,
            "pages": 256
        },
        {
            "id": 3,
            "title": "Vastu for Wealth and Prosperity",
            "author": "Pundit Sanjay Jumaani",
            "summary": "Discover Vastu secrets for attracting wealth and abundance into your life.",
            "image": "/images/books/vastu-wealth.jpg",
            "rating": 4.3,
            "pages": 288
        }
    ]
    return books_data

@router.get("/videos", response_model=List[Dict[str, Any]])
def get_videos(db: Session = Depends(get_db)):
    """Get all videos"""
    # Sample videos data - replace with database queries
    videos_data = [
        {
            "id": 1,
            "title": "Vastu Tips for Home - Complete Guide",
            "description": "Learn essential Vastu principles for creating a harmonious home environment.",
            "url": "https://youtube.com/watch?v=example1",
            "thumbnail": "/images/videos/vastu-home-guide.jpg",
            "duration": "15:30",
            "views": 125000
        },
        {
            "id": 2,
            "title": "Kitchen Vastu - Do's and Don'ts",
            "description": "Important Vastu guidelines for kitchen placement and design.",
            "url": "https://youtube.com/watch?v=example2",
            "thumbnail": "/images/videos/kitchen-vastu.jpg",
            "duration": "12:45",
            "views": 89000
        },
        {
            "id": 3,
            "title": "Bedroom Vastu for Better Sleep",
            "description": "Transform your bedroom according to Vastu for peaceful sleep.",
            "url": "https://youtube.com/watch?v=example3",
            "thumbnail": "/images/videos/bedroom-vastu.jpg",
            "duration": "18:20",
            "views": 156000
        }
    ]
    return videos_data

@router.get("/blog", response_model=list[BlogPostRead])
def list_blog_posts(db: Session = Depends(get_db)):
    return db.query(BlogPost).filter(BlogPost.published == True).all()

@router.post("/blog", response_model=BlogPostRead, dependencies=[Depends(require_role("admin"))])
def create_blog_post(post: BlogPostCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    blog = BlogPost(**post.dict(), author_id=int(current_user.sub))
    db.add(blog)
    db.commit()
    db.refresh(blog)
    return blog

@router.put("/blog/{id}", response_model=BlogPostRead, dependencies=[Depends(require_role("admin"))])
def update_blog_post(id: int, post: BlogPostUpdate, db: Session = Depends(get_db)):
    blog = db.query(BlogPost).filter(BlogPost.id == id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog post not found")
    for field, value in post.dict(exclude_unset=True).items():
        setattr(blog, field, value)
    db.commit()
    db.refresh(blog)
    return blog

@router.delete("/blog/{id}", dependencies=[Depends(require_role("admin"))])
def delete_blog_post(id: int, db: Session = Depends(get_db)):
    blog = db.query(BlogPost).filter(BlogPost.id == id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog post not found")
    db.delete(blog)
    db.commit()
    return {"ok": True} 