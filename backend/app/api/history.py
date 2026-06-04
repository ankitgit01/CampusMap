"""
Navigation history and user preferences API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
from app.database import get_db
from app.models import NavigationHistory, Favorite, Location, User
from app.api.auth import get_current_user
from app.ml.recommendation import RecommendationEngine

router = APIRouter(prefix="/history", tags=["history"])

recommendation_engine = RecommendationEngine()

@router.post("/save")
def save_navigation(
    source_location: str,
    destination_location: str,
    routing_mode: str,
    distance: float,
    estimated_time: float,
    actual_time: Optional[float] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save a navigation to history"""
    history_entry = NavigationHistory(
        user_id=user.id,
        source_location=source_location,
        destination_location=destination_location,
        routing_mode=routing_mode,
        distance=distance,
        estimated_time=estimated_time,
        actual_time=actual_time,
        completed=True
    )
    
    db.add(history_entry)
    db.commit()
    
    return {"message": "Navigation saved", "id": history_entry.id}

@router.get("/user")
def get_navigation_history(
    days: int = Query(30, description="Number of days to look back"),
    limit: int = 50,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's navigation history"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    history = db.query(NavigationHistory).filter(
        NavigationHistory.user_id == user.id,
        NavigationHistory.timestamp >= cutoff_date
    ).order_by(NavigationHistory.timestamp.desc()).limit(limit).all()
    
    return {
        "user_id": user.id,
        "days": days,
        "total": len(history),
        "history": [
            {
                "id": h.id,
                "source": h.source_location,
                "destination": h.destination_location,
                "mode": h.routing_mode,
                "distance": h.distance,
                "estimated_time": h.estimated_time,
                "actual_time": h.actual_time,
                "timestamp": h.timestamp,
                "completed": h.completed
            }
            for h in history
        ]
    }

@router.post("/favorites/add")
def add_favorite(
    location_id: int,
    alias: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a location to favorites"""
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Check if already favorited
    existing = db.query(Favorite).filter(
        Favorite.user_id == user.id,
        Favorite.location_id == location_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Location already in favorites"
        )
    
    favorite = Favorite(
        user_id=user.id,
        location_name=location.name,
        location_id=location_id,
        alias=alias or location.name
    )
    
    db.add(favorite)
    db.commit()
    
    return {"message": "Added to favorites", "location_name": location.name}

@router.get("/favorites")
def get_favorites(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user's favorite locations"""
    favorites = db.query(Favorite).filter(Favorite.user_id == user.id).all()
    
    return {
        "total": len(favorites),
        "favorites": [
            {
                "id": f.id,
                "location_id": f.location_id,
                "location_name": f.location_name,
                "alias": f.alias,
                "created_at": f.created_at
            }
            for f in favorites
        ]
    }

@router.delete("/favorites/{favorite_id}")
def remove_favorite(
    favorite_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a location from favorites"""
    favorite = db.query(Favorite).filter(
        Favorite.id == favorite_id,
        Favorite.user_id == user.id
    ).first()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")
    
    db.delete(favorite)
    db.commit()
    
    return {"message": "Removed from favorites"}

@router.get("/recommendations")
def get_recommendations(
    destination: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized route recommendations"""
    # Get user's history
    history = db.query(NavigationHistory).filter(
        NavigationHistory.user_id == user.id
    ).all()
    
    # Convert to dict format for recommendation engine
    history_dicts = [
        {
            "source_location": h.source_location,
            "destination_location": h.destination_location,
            "routing_mode": h.routing_mode,
            "timestamp": h.timestamp,
            "completed": h.completed
        }
        for h in history
    ]
    
    recommendations = recommendation_engine.get_recommendations(
        user_id=user.id,
        history=history_dicts,
        current_location=destination or "Unknown",
        num_recommendations=5
    )
    
    return {
        "user_id": user.id,
        "recommendations": recommendations
    }

@router.get("/frequently-used-routes")
def get_frequently_used_routes(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's most frequently used routes"""
    history = db.query(NavigationHistory).filter(
        NavigationHistory.user_id == user.id,
        NavigationHistory.completed == True
    ).all()
    
    history_dicts = [
        {
            "source_location": h.source_location,
            "destination_location": h.destination_location,
            "routing_mode": h.routing_mode,
            "timestamp": h.timestamp,
            "completed": h.completed
        }
        for h in history
    ]
    
    frequently_used = recommendation_engine.get_frequently_used_routes(
        user_id=user.id,
        history=history_dicts,
        limit=10
    )
    
    return {
        "user_id": user.id,
        "frequently_used": frequently_used
    }

@router.get("/statistics")
def get_history_statistics(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's navigation statistics"""
    history = db.query(NavigationHistory).filter(
        NavigationHistory.user_id == user.id
    ).all()
    
    completed = [h for h in history if h.completed]
    total_distance = sum(h.distance or 0 for h in completed)
    total_time = sum(h.actual_time or h.estimated_time or 0 for h in completed)
    
    mode_counts = {}
    location_counts = {}
    for h in completed:
        mode = h.routing_mode
        mode_counts[mode] = mode_counts.get(mode, 0) + 1
        for location_name in (h.source_location, h.destination_location):
            location_counts[location_name] = location_counts.get(location_name, 0) + 1

    frequent_locations = [
        {"location": location_name, "visits": visits}
        for location_name, visits in sorted(location_counts.items(), key=lambda item: item[1], reverse=True)
    ]
    
    return {
        "user_id": user.id,
        "total_navigations": len(history),
        "completed_navigations": len(completed),
        "total_distance_meters": total_distance,
        "total_time_seconds": total_time,
        "mode_preferences": mode_counts,
        "frequent_locations": frequent_locations[:8],
        "most_visited": frequent_locations[0]["location"] if frequent_locations else None
    }
