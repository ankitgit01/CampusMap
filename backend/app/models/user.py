"""
User model for authentication and profile management
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    phone_number = Column(String(20), nullable=True)
    profile_picture = Column(String(500), nullable=True)
    accessibility_requirements = Column(Text, nullable=True)  # JSON stored as text
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    navigation_history = relationship("NavigationHistory", back_populates="user")
    favorites = relationship("Favorite", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"
