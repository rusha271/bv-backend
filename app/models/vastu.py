from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, JSON
from datetime import datetime
from app.db.base import Base

class PlanetaryData(Base):
    __tablename__ = "planetary_data"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
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


class ChakraPoint(Base):
    __tablename__ = "chakra_points"
    
    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    direction = Column(String(20), nullable=False)
    description = Column(Text, nullable=False)
    remedies = Column(Text, nullable=False)
    is_auspicious = Column(Boolean, default=True)
    should_avoid = Column(Boolean, default=False)
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