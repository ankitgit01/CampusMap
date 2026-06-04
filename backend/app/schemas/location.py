"""
Pydantic schemas for location operations
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class LocationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    category: str  # Library, Hostel, Department, Building, Gate, Cafe, Bus Stop
    description: Optional[str] = None
    latitude: float
    longitude: float
    is_accessible: bool = False
    has_elevator: bool = False
    has_ramp: bool = False
    has_wheelchair_access: bool = False
    image_url: Optional[str] = None

class LocationResponse(BaseModel):
    id: int
    name: str
    category: str
    description: Optional[str] = None
    latitude: float
    longitude: float
    is_accessible: bool
    has_elevator: bool
    has_ramp: bool
    has_wheelchair_access: bool
    accessibility_score: float
    image_url: Optional[str] = None

    class Config:
        from_attributes = True

class LocationUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_accessible: Optional[bool] = None
    has_elevator: Optional[bool] = None
    has_ramp: Optional[bool] = None
    has_wheelchair_access: Optional[bool] = None
    accessibility_score: Optional[float] = None
    image_url: Optional[str] = None
