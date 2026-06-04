"""
Location/Node model for campus map
"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    category = Column(String(100), nullable=False)  # Library, Hostel, Department, Building, Gate, Cafe, Bus Stop
    description = Column(Text, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    is_accessible = Column(Boolean, default=False)
    has_elevator = Column(Boolean, default=False)
    has_ramp = Column(Boolean, default=False)
    has_wheelchair_access = Column(Boolean, default=False)
    accessibility_score = Column(Float, default=0.0)  # 0-1 score
    image_url = Column(String(500), nullable=True)
    operating_hours = Column(Text, nullable=True)  # JSON
    contact_info = Column(Text, nullable=True)  # JSON
    additional_info = Column(Text, nullable=True)  # JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    routes_from = relationship("Route", foreign_keys="Route.source_id", back_populates="source")
    routes_to = relationship("Route", foreign_keys="Route.destination_id", back_populates="destination")

    def __repr__(self):
        return f"<Location(id={self.id}, name={self.name}, category={self.category})>"
