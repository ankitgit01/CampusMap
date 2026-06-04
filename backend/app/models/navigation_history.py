"""
Navigation history model to track user journeys
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class NavigationHistory(Base):
    __tablename__ = "navigation_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    source_location = Column(String(255), nullable=False)
    destination_location = Column(String(255), nullable=False)
    routing_mode = Column(String(50), nullable=False)  # fastest, shortest, accessible, low_crowd
    distance = Column(Float, nullable=True)  # in meters
    estimated_time = Column(Float, nullable=True)  # in seconds
    actual_time = Column(Float, nullable=True)  # in seconds
    route_taken = Column(Text, nullable=True)  # JSON array of location IDs
    crowdedness_encountered = Column(Float, nullable=True)  # 0-1
    accessibility_used = Column(Boolean, default=False)
    weather_condition = Column(String(100), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    completed = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="navigation_history")

    def __repr__(self):
        return f"<NavigationHistory(id={self.id}, user_id={self.user_id})>"


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    location_name = Column(String(255), nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    alias = Column(String(255), nullable=True)  # User's custom name for location
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="favorites")

    def __repr__(self):
        return f"<Favorite(id={self.id}, user_id={self.user_id}, location={self.location_name})>"
