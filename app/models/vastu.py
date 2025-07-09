from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, JSON
from datetime import datetime
from app.db.base import Base

class PlanetaryData(Base):
    __tablename__ = "planetary_data"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    radius = Column(Float, nullable=False)
    distance = Column(Float, nullable=False)
    orbital_period = Column(Float, nullable=False)
    color = Column(Integer, nullable=False)  # Color as integer
    description = Column(Text, nullable=False)
    facts = Column(Text, nullable=False)
    mean_longitude = Column(Float, nullable=False)
    daily_motion = Column(Float, nullable=False)
    eccentricity = Column(Float, nullable=False)
    inclination = Column(Float, nullable=False)
    remedy = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class VastuTip(Base):
    __tablename__ = "vastu_tips"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    details = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    image_url = Column(String, nullable=False)
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class VastuCalculation(Base):
    __tablename__ = "vastu_calculations"
    
    id = Column(Integer, primary_key=True, index=True)
    location_data = Column(JSON, nullable=False)  # {"lat": float, "lng": float}
    calculation_date = Column(DateTime, nullable=False)
    planetary_positions = Column(JSON, nullable=False)
    vastu_recommendations = Column(JSON, nullable=False)
    chakra_alignment = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Book(Base):
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    isbn = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    image_alt = Column(String, nullable=True)
    rating = Column(Float, default=0.0)
    pages = Column(Integer, nullable=True)
    publication_year = Column(Integer, nullable=True)
    publisher = Column(String, nullable=True)
    price = Column(Float, nullable=True)
    is_available = Column(Boolean, default=True)
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Video(Base):
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    url = Column(String, nullable=False)
    video_type = Column(String, default="youtube")  # youtube, vimeo, direct
    youtube_id = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    duration = Column(String, nullable=True)
    views = Column(Integer, default=0)
    category = Column(String, nullable=True)
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MediaAsset(Base):
    __tablename__ = "media_assets"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String, nullable=False)
    asset_type = Column(String, nullable=False)  # image, video, document
    content_type = Column(String, nullable=True)  # book, video, tip
    content_id = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
