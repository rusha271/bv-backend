from sqlalchemy import Column, Float, Integer, LargeBinary, String, Text, ForeignKey, DateTime, Boolean
from datetime import datetime
from app.db.base import Base

class BlogPost(Base):
    __tablename__ = "blog_posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 


class VastuTip(Base):
    __tablename__ = "vastu_tips"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    details = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)
    image_url = Column(String(500), nullable=False)
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # author_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Add this

class Book(Base):
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    isbn = Column(String(20), nullable=True)
    image_url = Column(String(500), nullable=True)
    image_alt = Column(String(255), nullable=True)
    rating = Column(Float, default=0.0)
    pages = Column(Integer, nullable=True)
    publication_year = Column(Integer, nullable=True)
    publisher = Column(String(255), nullable=True)
    price = Column(Float, nullable=True)
    is_available = Column(Boolean, default=True)
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    url = Column(String(500), nullable=True)
    video_type = Column(String(50), default="blob")
    thumbnail_url = Column(String(500), nullable=True)
    duration = Column(String(20), nullable=True)
    views = Column(Integer, default=0)
    category = Column(String(100), nullable=True)
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_video_url(self, db_session=None):
        """Get the actual video URL, either from url field or MediaAsset"""
        if self.url:
            return self.url
        
        # If no URL is set, try to find the actual filename from MediaAsset
        if db_session:
            try:
                media_asset = db_session.query(MediaAsset).filter(
                    MediaAsset.content_id == self.id,
                    MediaAsset.asset_type == "video"
                ).first()
                
                if media_asset and media_asset.filename:
                    return f"/static/media/videos/{media_asset.filename}"
            except Exception:
                pass
        
        # Fallback
        return f"/static/media/videos/video_{self.id}.mp4"
    
class MediaAsset(Base):
    __tablename__ = "media_assets"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=True)  # Nullable for blobs
    original_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=True)  # Nullable for blobs
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    asset_type = Column(String(50), nullable=False)  # image, video, document
    content_type = Column(String(50), nullable=True)  # book, video, tip
    content_id = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    file_data = Column(LargeBinary, nullable=True)  # Added for blob storage
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)