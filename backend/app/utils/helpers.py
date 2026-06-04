"""
Helper functions for the application
"""
import math
from typing import Tuple

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    Returns distance in meters
    """
    # Convert decimal degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in meters
    r = 6371000
    
    return c * r

def calculate_walking_time(distance: float, accessibility: bool = False) -> float:
    """
    Calculate walking time in seconds based on distance and accessibility
    """
    from app.utils.constants import DEFAULT_WALKING_SPEED, ACCESSIBLE_WALKING_SPEED
    
    speed = ACCESSIBLE_WALKING_SPEED if accessibility else DEFAULT_WALKING_SPEED
    return distance / speed  # time in seconds

def calculate_accessibility_score(
    has_stairs: bool,
    has_slope: bool,
    slope_percentage: float,
    is_wheelchair_accessible: bool,
    has_ramp: bool,
    has_elevator: bool,
    width: float = None
) -> float:
    """
    Calculate accessibility score (0-1) based on various factors
    """
    from app.utils.constants import ACCESSIBILITY_WEIGHTS
    
    score = 0.5  # Base score
    
    # Negative factors
    if has_stairs:
        score += ACCESSIBILITY_WEIGHTS["has_stairs"]
    
    if has_slope:
        slope_factor = min(slope_percentage / 100, 1.0)  # Cap at 1.0
        score += ACCESSIBILITY_WEIGHTS["has_slope"] * slope_factor
    
    # Positive factors
    if is_wheelchair_accessible:
        score += ACCESSIBILITY_WEIGHTS["is_wheelchair_accessible"]
    
    if has_ramp:
        score += ACCESSIBILITY_WEIGHTS["has_ramp"]
    
    if has_elevator:
        score += ACCESSIBILITY_WEIGHTS["has_elevator"]
    
    if width and width >= 2.0:  # Wide enough for wheelchair
        score += ACCESSIBILITY_WEIGHTS["width"]
    
    # Clamp score between 0 and 1
    return max(0.0, min(1.0, score))

def encode_polyline(points: list) -> str:
    """
    Encode a list of lat/lon tuples into a Google polyline string
    """
    # Simplified version - full implementation would match Google's algorithm
    return ""

def decode_polyline(encoded: str) -> list:
    """
    Decode a Google polyline string into lat/lon tuples
    """
    # Simplified version
    return []

def format_time(seconds: float) -> str:
    """
    Format seconds into human readable time
    """
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours}h {minutes}m"

def format_distance(meters: float) -> str:
    """
    Format meters into human readable distance
    """
    if meters < 1000:
        return f"{int(meters)}m"
    else:
        km = meters / 1000
        return f"{km:.2f}km"
