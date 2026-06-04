"""
Navigation API endpoints - Core routing functionality
"""
from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from jose import JWTError, jwt
from app.database import get_db
from app.models import Location, Route, NavigationHistory, User, PresencePing
from app.graph.graph_builder import GraphBuilder
from app.graph.dijkstra import DijkstraRouter
from app.graph.astar import AStarRouter
from app.graph.accessibility import AccessibilityRouter
from app.ml.eta_predictor import ETAPredictor
from app.ml.crowd_predictor import CrowdPredictor
from app.services.signals import (
    annotate_graph_with_signals,
    build_route_signal_map,
    cleanup_stale_presence,
    get_weather_signal,
)
from app.api.auth import ALGORITHM, SECRET_KEY

router = APIRouter(prefix="/navigation", tags=["navigation"])

# Initialize predictors
eta_predictor = ETAPredictor()
crowd_predictor = CrowdPredictor()

@router.post("/find-route")
def find_route(
    source_location: str = Query(...),
    destination_location: str = Query(...),
    mode: str = Query("fastest", regex="^(fastest|shortest|accessible|low_crowd)$"),
    algorithm: str = Query("dijkstra", regex="^(dijkstra|astar)$"),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Find optimal route between two locations
    
    Modes:
    - fastest: Minimize travel time
    - shortest: Minimize distance
    - accessible: Prefer accessible routes
    - low_crowd: Avoid crowded paths
    
    Algorithms:
    - dijkstra: Classic shortest path
    - astar: A* with heuristics
    """
    
    cleanup_stale_presence(db)
    current_user = _optional_user_from_authorization(authorization, db)

    # Build graph and apply live crowd/weather signals
    graph = GraphBuilder.build_graph(db)
    source_location_obj = db.query(Location).filter(Location.name == source_location).first()
    weather_signal = get_weather_signal(
        source_location_obj.latitude if source_location_obj else None,
        source_location_obj.longitude if source_location_obj else None,
    )
    signal_map = build_route_signal_map(db, weather_signal=weather_signal)
    annotate_graph_with_signals(graph, signal_map)
    
    # Get location IDs
    source_id = graph.get_location_by_name(source_location)
    dest_id = graph.get_location_by_name(destination_location)
    
    if not source_id or not dest_id:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Find path based on algorithm
    if algorithm == "astar":
        router_algo = AStarRouter(graph)
    else:
        router_algo = DijkstraRouter(graph)
    
    # Find path based on mode
    if mode == "accessible":
        result = router_algo.find_accessible_path(source_id, dest_id)
    elif mode == "low_crowd":
        result = _find_best_personal_route(router_algo, graph, source_id, dest_id, current_user, db)
    elif mode == "shortest":
        result = router_algo.find_path(source_id, dest_id, weight_key="distance")
    else:  # fastest
        result = router_algo.find_path(source_id, dest_id, weight_key="effective_walking_time")
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    route_ids = result.get("route_ids") or _route_ids_for_path(graph, result["path"])
    route_signals = [signal_map[route_id] for route_id in route_ids if route_id in signal_map]
    avg_crowdedness = (
        sum(signal["effective_crowd_score"] for signal in route_signals) / len(route_signals)
        if route_signals
        else 0
    )
    eta_result = eta_predictor.predict_eta(
        distance=result['distance'],
        crowdedness=avg_crowdedness,
        weather=weather_signal["condition"],
        accessibility_mode=(mode == "accessible"),
        route_complexity=min(len(result['path']) - 2, 5)
    )
    
    if current_user:
        history = NavigationHistory(
            user_id=current_user.id,
            source_location=source_location,
            destination_location=destination_location,
            routing_mode=mode,
            distance=result['distance'],
            estimated_time=eta_result['estimated_time_seconds'],
            route_taken=",".join(str(node_id) for node_id in result["path"]),
            crowdedness_encountered=avg_crowdedness,
            accessibility_used=(mode == "accessible"),
            weather_condition=weather_signal["condition"],
            completed=True,
        )
        db.add(history)
        db.commit()
    
    return {
        "source": source_location,
        "destination": destination_location,
        "mode": mode,
        "algorithm": result.get('algorithm'),
        "distance": result['distance'],
        "walking_time": result['walking_time'],
        "eta": eta_result['estimated_time_seconds'],
        "eta_formatted": eta_result['estimated_time_formatted'],
        "eta_confidence": eta_result['confidence'],
        "path": result['path'],
        "segments": _segments_for_path(graph, result["path"], signal_map, route_ids),
        "num_stops": result['num_stops'],
        "crowdedness_level": crowd_predictor._get_crowdedness_level(avg_crowdedness),
        "crowdedness_score": avg_crowdedness,
        "route_ids": route_ids,
        "signals": {
            "weather": weather_signal,
            "presence_count": sum(signal["presence_count"] for signal in route_signals),
            "admin_crowd_score": max((signal["admin_crowd_score"] for signal in route_signals), default=0),
        },
        "personalized_via": result.get("personalized_via"),
        "personal_frequency": result.get("personal_frequency", 0),
}


@router.post("/presence")
def set_current_location(
    session_id: str = Query(..., min_length=8, max_length=128),
    location_id: Optional[int] = Query(None),
    location_name: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Record an anonymous current-location ping for live crowd inference."""
    cleanup_stale_presence(db)
    query = db.query(Location)
    if location_id is not None:
        location = query.filter(Location.id == location_id).first()
    elif location_name:
        location = query.filter(Location.name == location_name).first()
    else:
        raise HTTPException(status_code=400, detail="Choose a current location")

    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    ping = db.query(PresencePing).filter(PresencePing.session_id == session_id).first()
    if ping is None:
        ping = PresencePing(session_id=session_id, location_id=location.id)
        db.add(ping)
    else:
        ping.location_id = location.id
        ping.updated_at = datetime.utcnow()
    db.commit()

    counts = _presence_by_location(db)
    return {
        "message": "Current location updated",
        "location": {"id": location.id, "name": location.name},
        "active_here": counts.get(location.id, 0),
        "active_locations": counts,
    }


@router.get("/signals")
def get_live_signals(
    db: Session = Depends(get_db),
):
    """Return active campus signals used by ETA and crowd-aware routing."""
    cleanup_stale_presence(db)
    weather_signal = get_weather_signal()
    signal_map = build_route_signal_map(db, weather_signal=weather_signal)
    counts = _presence_by_location(db)
    return {
        "campus": "IIT Roorkee, Uttarakhand",
        "weather": weather_signal,
        "active_presence": sum(counts.values()),
        "presence_by_location": counts,
        "routes": signal_map,
    }


@router.get("/weather")
def get_current_weather(
    location_id: Optional[int] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    db: Session = Depends(get_db),
):
    """Fetch current weather for a selected/detected campus position."""
    if location_id is not None:
        location = db.query(Location).filter(Location.id == location_id).first()
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")
        latitude = location.latitude
        longitude = location.longitude
    if latitude is None or longitude is None:
        raise HTTPException(status_code=400, detail="Location coordinates required")
    return get_weather_signal(latitude, longitude)

@router.get("/route-details/{route_id}")
def get_route_details(route_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific route"""
    route = db.query(Route).filter(Route.id == route_id).first()
    
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    
    source = db.query(Location).filter(Location.id == route.source_id).first()
    destination = db.query(Location).filter(Location.id == route.destination_id).first()
    
    return {
        "id": route.id,
        "source": {
            "id": source.id,
            "name": source.name,
            "latitude": source.latitude,
            "longitude": source.longitude
        },
        "destination": {
            "id": destination.id,
            "name": destination.name,
            "latitude": destination.latitude,
            "longitude": destination.longitude
        },
        "distance": route.distance,
        "walking_time": route.walking_time,
        "route_type": route.route_type,
        "accessibility_score": route.accessibility_score,
        "crowdedness_score": route.crowdedness_score,
        "is_blocked": route.is_blocked,
        "blocked_reason": route.blocked_reason,
        "has_stairs": route.has_stairs,
        "has_slope": route.has_slope,
        "is_wheelchair_accessible": route.is_wheelchair_accessible,
        "has_weather_cover": route.has_weather_cover,
        "has_lighting": route.has_lighting
    }

@router.get("/accessibility-index/{location_id}")
def get_accessibility_index(location_id: int, db: Session = Depends(get_db)):
    """Get accessibility score for a location"""
    graph = GraphBuilder.build_graph(db)
    accessibility_router = AccessibilityRouter(graph)
    
    return accessibility_router.get_accessibility_index(location_id)

@router.get("/accessibility-metrics")
def get_accessibility_metrics(db: Session = Depends(get_db)):
    """Get overall campus accessibility metrics"""
    graph = GraphBuilder.build_graph(db)
    accessibility_router = AccessibilityRouter(graph)
    
    return accessibility_router.get_accessibility_metrics()

@router.get("/crowdedness/{location_id}")
def get_location_crowdedness(
    location_id: int,
    db: Session = Depends(get_db)
):
    """Get current/predicted crowdedness for a location"""
    location = db.query(Location).filter(Location.id == location_id).first()
    
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Get connected routes
    routes = db.query(Route).filter(
        (Route.source_id == location_id) | (Route.destination_id == location_id)
    ).all()
    
    signal_map = build_route_signal_map(db, [route.id for route in routes])
    avg_crowdedness = (
        sum(signal["effective_crowd_score"] for signal in signal_map.values()) / len(signal_map)
        if signal_map
        else 0
    )
    
    return {
        "location_id": location_id,
        "location_name": location.name,
        "average_crowdedness": avg_crowdedness,
        "crowdedness_level": crowd_predictor._get_crowdedness_level(avg_crowdedness),
        "last_updated": max((r.last_crowdedness_update for r in routes), default=None),
        "active_users_here": _presence_by_location(db).get(location_id, 0)
    }

@router.post("/compare-routes")
def compare_routes(
    source_location: str = Query(...),
    destination_location: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Compare different routing modes and algorithms
    Returns fastest, shortest, accessible, and low_crowd routes
    """
    graph = GraphBuilder.build_graph(db)
    signal_map = build_route_signal_map(db)
    annotate_graph_with_signals(graph, signal_map)
    
    source_id = graph.get_location_by_name(source_location)
    dest_id = graph.get_location_by_name(destination_location)
    
    if not source_id or not dest_id:
        raise HTTPException(status_code=404, detail="Location not found")
    
    dijkstra = DijkstraRouter(graph)
    astar = AStarRouter(graph)
    
    # Get different routes
    fastest_dijkstra = dijkstra.find_path(source_id, dest_id, weight_key="effective_walking_time")
    shortest_dijkstra = dijkstra.find_path(source_id, dest_id, weight_key="distance")
    accessible = dijkstra.find_accessible_path(source_id, dest_id)
    low_crowd = astar.find_low_crowd_path(source_id, dest_id)
    
    return {
        "routes": {
            "fastest": fastest_dijkstra,
            "shortest": shortest_dijkstra,
            "accessible": accessible,
            "low_crowd": low_crowd
        }
    }


def _route_ids_for_path(graph, path: List[int]) -> List[int]:
    route_ids = []
    for index in range(len(path) - 1):
        for neighbor_id, edge_data in graph.get_neighbors(path[index]):
            if neighbor_id == path[index + 1]:
                route_ids.append(edge_data.get("route_id"))
                break
    return [route_id for route_id in route_ids if route_id is not None]


def _segments_for_path(graph, path: List[int], signal_map: dict, route_ids: Optional[List[int]] = None) -> List[dict]:
    segments = []
    for index in range(len(path) - 1):
        source_id = path[index]
        destination_id = path[index + 1]
        source = graph.get_location(source_id)
        destination = graph.get_location(destination_id)
        if not source or not destination:
            continue

        preferred_route_id = route_ids[index] if route_ids and index < len(route_ids) else None
        matching_edges = []
        for neighbor_id, edge_data in graph.get_neighbors(source_id):
            if neighbor_id != destination_id:
                continue
            matching_edges.append(edge_data)

        if preferred_route_id is not None:
            matching_edges = sorted(
                matching_edges,
                key=lambda edge_data: edge_data.get("route_id") != preferred_route_id,
            )

        for edge_data in matching_edges:
            route_id = edge_data.get("route_id")
            signal = signal_map.get(route_id, {})
            crowd_score = signal.get("effective_crowd_score", edge_data.get("crowdedness_score", 0))
            segments.append({
                "route_id": route_id,
                "source_id": source_id,
                "destination_id": destination_id,
                "source": source.get("name"),
                "destination": destination.get("name"),
                "positions": [
                    [source.get("latitude"), source.get("longitude")],
                    [destination.get("latitude"), destination.get("longitude")],
                ],
                "distance": edge_data.get("distance", 0),
                "walking_time": edge_data.get("walking_time", 0),
                "effective_walking_time": edge_data.get("effective_walking_time", edge_data.get("walking_time", 0)),
                "crowdedness_score": crowd_score,
                "crowdedness_level": crowd_predictor._get_crowdedness_level(crowd_score),
            })
            break
    return segments


def _presence_by_location(db: Session) -> dict:
    from app.services.signals import active_presence_counts

    return active_presence_counts(db)


def _optional_user_from_authorization(authorization: Optional[str], db: Session) -> Optional[User]:
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            return None
        return db.query(User).filter(User.email == email).first()
    except JWTError:
        return None


def _find_best_personal_route(router_algo, graph, source_id: int, dest_id: int, user: Optional[User], db: Session) -> dict:
    direct = (
        router_algo.find_low_crowd_path(source_id, dest_id)
        if hasattr(router_algo, "find_low_crowd_path")
        else router_algo.find_path(source_id, dest_id, weight_key="effective_walking_time")
    )
    candidates = [direct]
    frequent = _frequent_location_ids(user, db)

    for location_id, count in frequent[:5]:
        if location_id in (source_id, dest_id):
            continue
        first = router_algo.find_path(source_id, location_id, weight_key="effective_walking_time")
        second = router_algo.find_path(location_id, dest_id, weight_key="effective_walking_time")
        if "error" in first or "error" in second:
            continue
        joined_path = first["path"] + second["path"][1:]
        candidates.append({
            "path": joined_path,
            "distance": first["distance"] + second["distance"],
            "walking_time": first["walking_time"] + second["walking_time"],
            "num_stops": len(joined_path),
            "start_location": graph.get_location(source_id),
            "end_location": graph.get_location(dest_id),
            "algorithm": first.get("algorithm", "dijkstra"),
            "mode": "best_route",
            "personalized_via": graph.get_location(location_id).get("name"),
            "personal_frequency": count,
        })

    def score(candidate):
        if "error" in candidate:
            return float("inf")
        route_ids = _route_ids_for_path(graph, candidate["path"])
        crowd = []
        effective_time = 0
        for route_id in route_ids:
            for edges in graph.edges.values():
                for _, edge_data in edges:
                    if edge_data.get("route_id") == route_id:
                        effective_time += edge_data.get("effective_walking_time", edge_data.get("walking_time", 0))
                        crowd.append(edge_data.get("crowdedness_score", 0))
                        break
        avg_crowd = sum(crowd) / len(crowd) if crowd else 0
        bonus = candidate.get("personal_frequency", 0) * 45
        return effective_time + avg_crowd * 600 - bonus

    return min(candidates, key=score)


def _frequent_location_ids(user: Optional[User], db: Session) -> List[tuple]:
    if not user:
        return []
    histories = db.query(NavigationHistory).filter(
        NavigationHistory.user_id == user.id,
        NavigationHistory.completed == True,
    ).all()
    counts = {}
    name_to_id = {location.name: location.id for location in db.query(Location).all()}
    for entry in histories:
        for name in (entry.source_location, entry.destination_location):
            location_id = name_to_id.get(name)
            if location_id:
                counts[location_id] = counts.get(location_id, 0) + 1
    return sorted(counts.items(), key=lambda item: item[1], reverse=True)
