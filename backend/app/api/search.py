"""
Search and discovery API endpoints
"""
from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
from app.database import get_db
from app.models import Location, Route
from fuzzywuzzy import fuzz

router = APIRouter(prefix="/search", tags=["search"])

@router.get("/locations")
def search_locations(
    query: str = Query(..., min_length=1),
    category: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Search for locations by name or category
    Supports fuzzy matching for typo tolerance
    """
    db_locations = db.query(Location).all()
    
    # Filter by category if provided
    if category:
        db_locations = [l for l in db_locations if l.category == category]
    
    # Fuzzy match results
    results = []
    for location in db_locations:
        score = fuzz.token_set_ratio(query.lower(), location.name.lower())
        if score > 60:  # Threshold for match
            results.append({
                "id": location.id,
                "name": location.name,
                "category": location.category,
                "latitude": location.latitude,
                "longitude": location.longitude,
                "match_score": score,
                "description": location.description
            })
    
    # Sort by match score
    results = sorted(results, key=lambda x: x['match_score'], reverse=True)[:limit]
    
    return {
        "query": query,
        "results": results,
        "total": len(results)
    }

@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    """Get all location categories with counts"""
    categories = db.query(
        Location.category,
        func.count(Location.id).label('count')
    ).group_by(Location.category).all()
    
    return {
        "categories": [
            {
                "name": cat[0],
                "count": cat[1]
            }
            for cat in categories
        ]
    }

@router.get("/nearby")
def search_nearby(
    latitude: float = Query(...),
    longitude: float = Query(...),
    category: Optional[str] = None,
    radius: float = Query(500, description="Search radius in meters"),
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Find locations near a geographic point
    Uses approximate distance calculation
    """
    locations = db.query(Location).all()
    
    # Filter by category if provided
    if category:
        locations = [l for l in locations if l.category == category]
    
    # Calculate distances (simple approximation)
    nearby = []
    for location in locations:
        # Approximate distance in meters
        lat_diff = (location.latitude - latitude) * 111320
        lon_diff = (location.longitude - longitude) * 111320 * __import__('math').cos(__import__('math').radians(latitude))
        distance = __import__('math').sqrt(lat_diff**2 + lon_diff**2)
        
        if distance <= radius:
            nearby.append({
                "id": location.id,
                "name": location.name,
                "category": location.category,
                "latitude": location.latitude,
                "longitude": location.longitude,
                "distance": distance,
                "description": location.description
            })
    
    # Sort by distance
    nearby = sorted(nearby, key=lambda x: x['distance'])[:limit]
    
    return {
        "center": {
            "latitude": latitude,
            "longitude": longitude
        },
        "radius": radius,
        "results": nearby,
        "total": len(nearby)
    }

@router.get("/trending")
def get_trending_locations(
    days: int = Query(7, description="Days to look back"),
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get trending destinations based on navigation history
    """
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Get most visited destinations
    trending = db.query(
        Location.id,
        Location.name,
        Location.category,
        func.count(Location.id).label('visit_count')
    ).select_from(Location).all()
    
    # Sort by visit count
    trending = sorted(trending, key=lambda x: x[3], reverse=True)[:limit]
    
    return {
        "period_days": days,
        "results": [
            {
                "id": item[0],
                "name": item[1],
                "category": item[2],
                "visit_count": item[3]
            }
            for item in trending
        ]
    }

@router.get("/accessible")
def search_accessible_locations(
    min_score: float = Query(0.6, ge=0, le=1),
    category: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Search for accessible locations
    """
    query = db.query(Location).filter(
        Location.accessibility_score >= min_score
    )
    
    if category:
        query = query.filter(Location.category == category)
    
    locations = query.order_by(
        Location.accessibility_score.desc()
    ).limit(limit).all()
    
    return {
        "min_accessibility_score": min_score,
        "results": [
            {
                "id": loc.id,
                "name": loc.name,
                "category": loc.category,
                "accessibility_score": loc.accessibility_score,
                "has_wheelchair_access": loc.has_wheelchair_access,
                "has_ramp": loc.has_ramp,
                "has_elevator": loc.has_elevator
            }
            for loc in locations
        ]
    }

@router.get("/by-category/{category}")
def get_locations_by_category(
    category: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get all locations in a specific category"""
    locations = db.query(Location).filter(
        Location.category == category
    ).offset(skip).limit(limit).all()
    
    total = db.query(Location).filter(Location.category == category).count()
    
    return {
        "category": category,
        "total": total,
        "items": locations
    }
