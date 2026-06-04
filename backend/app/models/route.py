"""
Route/Edge model for campus map connections
"""
from sqlalchemy import Column, Integer, Float, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("locations.id"), nullable=False, index=True)
    destination_id = Column(Integer, ForeignKey("locations.id"), nullable=False, index=True)
    
    # Physical properties
    distance = Column(Float, nullable=False)  # in meters
    walking_time = Column(Float, nullable=False)  # in seconds
    route_type = Column(String(50), nullable=False)  # Road, Footpath, Corridor, Bridge, Ramp
    
    # Accessibility
    accessibility_score = Column(Float, default=0.0)  # 0-1 score
    has_stairs = Column(Boolean, default=False)
    has_slope = Column(Boolean, default=False)
    slope_percentage = Column(Float, default=0.0)
    is_wheelchair_accessible = Column(Boolean, default=False)
    width = Column(Float, nullable=True)  # in meters
    
    # Crowdedness
    crowdedness_score = Column(Float, default=0.0)  # 0-1, predicted/real-time
    last_crowdedness_update = Column(DateTime, nullable=True)
    
    # Route status
    is_blocked = Column(Boolean, default=False)
    blocked_reason = Column(String(255), nullable=True)
    is_closed = Column(Boolean, default=False)
    
    # Additional info
    has_weather_cover = Column(Boolean, default=False)
    has_lighting = Column(Boolean, default=False)
    description = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    source = relationship("Location", foreign_keys=[source_id], back_populates="routes_from")
    destination = relationship("Location", foreign_keys=[destination_id], back_populates="routes_to")

    def __repr__(self):
        return f"<Route(id={self.id}, source_id={self.source_id}, destination_id={self.destination_id})>"
