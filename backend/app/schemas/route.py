"""
Pydantic schemas for route operations
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class RouteCreate(BaseModel):
    source_id: int
    destination_id: int
    distance: float = Field(..., gt=0)
    walking_time: float = Field(..., gt=0)
    route_type: str  # Road, Footpath, Corridor, Bridge, Ramp
    crowdedness_score: float = 0.0
    accessibility_score: float = 0.8
    is_blocked: bool = False
    blocked_reason: Optional[str] = None
    has_stairs: bool = False
    has_slope: bool = False
    is_wheelchair_accessible: bool = False
    has_weather_cover: bool = False
    has_lighting: bool = False

class RouteResponse(BaseModel):
    id: int
    source_id: int
    destination_id: int
    distance: float
    walking_time: float
    route_type: str
    accessibility_score: float
    crowdedness_score: float
    is_blocked: bool
    has_stairs: bool
    has_slope: bool
    is_wheelchair_accessible: bool

    class Config:
        from_attributes = True

class RouteUpdate(BaseModel):
    distance: Optional[float] = None
    walking_time: Optional[float] = None
    is_blocked: Optional[bool] = None
    blocked_reason: Optional[str] = None
    crowdedness_score: Optional[float] = None
    accessibility_score: Optional[float] = None
