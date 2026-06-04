"""
Admin API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Location, Route, User
from app.schemas.location import LocationCreate, LocationResponse, LocationUpdate
from app.schemas.route import RouteCreate, RouteResponse, RouteUpdate
from app.api.auth import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])

def verify_admin(user: User = Depends(get_current_user)) -> User:
    """Verify user is admin"""
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user

# Location Management

@router.post("/locations", response_model=LocationResponse)
def create_location(
    location: LocationCreate,
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Add a new location (admin only)"""
    # Check if location already exists
    existing = db.query(Location).filter(Location.name == location.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Location already exists"
        )
    
    new_location = Location(**location.dict())
    db.add(new_location)
    db.commit()
    db.refresh(new_location)
    
    return new_location

@router.get("/locations")
def list_locations(
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all locations"""
    query = db.query(Location)
    
    if category:
        query = query.filter(Location.category == category)
    
    locations = query.offset(skip).limit(limit).all()
    total = db.query(Location).count()
    
    return {
        "total": total,
        "items": locations
    }

@router.get("/locations/{location_id}", response_model=LocationResponse)
def get_location(location_id: int, db: Session = Depends(get_db)):
    """Get specific location"""
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location

@router.put("/locations/{location_id}", response_model=LocationResponse)
def update_location(
    location_id: int,
    location_update: LocationUpdate,
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Update location (admin only)"""
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    update_data = location_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(location, key, value)
    
    db.commit()
    db.refresh(location)
    
    return location

@router.delete("/locations/{location_id}")
def delete_location(
    location_id: int,
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Delete location (admin only)"""
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    db.query(Route).filter(
        (Route.source_id == location_id) | (Route.destination_id == location_id)
    ).delete(synchronize_session=False)
    db.delete(location)
    db.commit()
    
    return {"message": "Location deleted"}

# Route Management

@router.post("/routes", response_model=RouteResponse)
def create_route(
    route: RouteCreate,
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Add a new route (admin only)"""
    # Verify locations exist
    source = db.query(Location).filter(Location.id == route.source_id).first()
    destination = db.query(Location).filter(Location.id == route.destination_id).first()
    
    if not source or not destination:
        raise HTTPException(status_code=404, detail="Location not found")
    
    new_route = Route(**route.dict())
    db.add(new_route)
    db.commit()
    db.refresh(new_route)
    
    return new_route

@router.get("/routes")
def list_routes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all routes"""
    routes = db.query(Route).offset(skip).limit(limit).all()
    total = db.query(Route).count()
    
    return {
        "total": total,
        "items": routes
    }

@router.get("/routes/{route_id}", response_model=RouteResponse)
def get_route(route_id: int, db: Session = Depends(get_db)):
    """Get specific route"""
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return route

@router.put("/routes/{route_id}", response_model=RouteResponse)
def update_route(
    route_id: int,
    route_update: RouteUpdate,
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Update route status (admin only)"""
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    
    update_data = route_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(route, key, value)
    
    db.commit()
    db.refresh(route)
    
    return route

@router.patch("/routes/{route_id}/block")
def block_route(
    route_id: int,
    reason: str,
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Block a route (admin only)"""
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    
    route.is_blocked = True
    route.blocked_reason = reason
    db.commit()
    
    return {"message": "Route blocked", "reason": reason}

@router.patch("/routes/{route_id}/unblock")
def unblock_route(
    route_id: int,
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Unblock a route (admin only)"""
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    
    route.is_blocked = False
    route.blocked_reason = None
    db.commit()
    
    return {"message": "Route unblocked"}

@router.delete("/routes/{route_id}")
def delete_route(
    route_id: int,
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Delete route (admin only)"""
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    
    db.delete(route)
    db.commit()
    
    return {"message": "Route deleted"}

# Statistics

@router.get("/statistics")
def get_statistics(
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Get admin dashboard statistics"""
    total_locations = db.query(Location).count()
    total_routes = db.query(Route).count()
    total_users = db.query(User).count()
    blocked_routes = db.query(Route).filter(Route.is_blocked == True).count()
    
    return {
        "total_locations": total_locations,
        "total_routes": total_routes,
        "total_users": total_users,
        "active_routes": total_routes - blocked_routes,
        "blocked_routes": blocked_routes,
        "admin_users": db.query(User).filter(User.is_admin == True).count()
    }

@router.get("/blocked-routes")
def get_blocked_routes(
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Get all blocked routes"""
    blocked_routes = db.query(Route).filter(Route.is_blocked == True).all()
    
    return {
        "total": len(blocked_routes),
        "routes": [
            {
                "id": route.id,
                "source_id": route.source_id,
                "destination_id": route.destination_id,
                "blocked_reason": route.blocked_reason,
                "updated_at": route.updated_at
            }
            for route in blocked_routes
        ]
    }
