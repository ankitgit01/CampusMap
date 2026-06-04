"""
Anonymous current-location check-ins used for live campus crowd signals.
"""
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.database import Base


class PresencePing(Base):
    __tablename__ = "presence_pings"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(128), unique=True, nullable=False, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self):
        return f"<PresencePing(session_id={self.session_id}, location_id={self.location_id})>"
