"""
Live signal helpers for crowd, weather, and routing.
"""
from datetime import datetime, timedelta
from typing import Dict, Iterable, Optional

import requests
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import PresencePing, Route
from app.ml.crowd_predictor import CrowdPredictor


CROWD_PING_TTL_MINUTES = 20
IIT_ROORKEE_WEATHER = {
    "campus": "IIT Roorkee, Uttarakhand",
    "source": "offline campus heuristic",
    "condition": "clear",
    "temperature_c": 28,
    "impact": 1.0,
}


def get_weather_signal(
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
) -> Dict:
    """Fetch current weather from Open-Meteo with an offline fallback."""
    lat = latitude if latitude is not None else 29.8655
    lon = longitude if longitude is not None else 77.8976
    try:
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,precipitation,weather_code,wind_speed_10m",
                "timezone": "auto",
            },
            timeout=4,
        )
        response.raise_for_status()
        current = response.json().get("current", {})
        condition = _weather_code_to_condition(current.get("weather_code"), current.get("precipitation", 0))
        return {
            "campus": "IIT Roorkee, Uttarakhand",
            "source": "Open-Meteo live current weather",
            "condition": condition,
            "temperature_c": current.get("temperature_2m"),
            "precipitation_mm": current.get("precipitation", 0),
            "wind_speed_kmh": current.get("wind_speed_10m"),
            "observed_at": current.get("time"),
            "latitude": lat,
            "longitude": lon,
            "impact": _weather_impact(condition),
        }
    except requests.RequestException:
        return {
            **IIT_ROORKEE_WEATHER,
            "source": "offline fallback",
            "latitude": lat,
            "longitude": lon,
        }


def active_presence_counts(db: Session) -> Dict[int, int]:
    cutoff = datetime.utcnow() - timedelta(minutes=CROWD_PING_TTL_MINUTES)
    rows = (
        db.query(PresencePing.location_id, func.count(PresencePing.id))
        .filter(PresencePing.updated_at >= cutoff)
        .group_by(PresencePing.location_id)
        .all()
    )
    return {location_id: count for location_id, count in rows}


def build_route_signal_map(
    db: Session,
    route_ids: Optional[Iterable[int]] = None,
    weather_signal: Optional[Dict] = None,
) -> Dict[int, Dict]:
    """Compute effective crowd and ETA multipliers without overwriting admin values."""
    predictor = CrowdPredictor()
    counts = active_presence_counts(db)
    weather_signal = weather_signal or get_weather_signal()

    query = db.query(Route)
    if route_ids is not None:
        query = query.filter(Route.id.in_(list(route_ids)))

    signals = {}
    for route in query.all():
        admin_score = min(max(route.crowdedness_score or 0.0, 0.0), 1.0)
        source_count = counts.get(route.source_id, 0)
        destination_count = counts.get(route.destination_id, 0)
        presence_score = min(1.0, (source_count + destination_count) / 12)
        weather_bonus = 0.08 if weather_signal["condition"] == "rainy" and not route.has_weather_cover else 0.0
        effective = min(1.0, max(admin_score, presence_score) + weather_bonus)

        blocked_multiplier = 99 if route.is_blocked else 1
        eta_multiplier = blocked_multiplier * (1 + effective * 0.65) * weather_signal["impact"]

        signals[route.id] = {
            "admin_crowd_score": admin_score,
            "presence_count": source_count + destination_count,
            "presence_score": presence_score,
            "predicted_crowd_score": effective,
            "effective_crowd_score": effective,
            "crowdedness_level": predictor._get_crowdedness_level(effective),
            "weather": weather_signal,
            "eta_multiplier": eta_multiplier,
        }

    return signals


def annotate_graph_with_signals(graph, route_signals: Dict[int, Dict]) -> None:
    for edges in graph.edges.values():
        for _, edge_data in edges:
            signal = route_signals.get(edge_data.get("route_id"))
            if not signal:
                continue
            edge_data["admin_crowd_score"] = signal["admin_crowd_score"]
            edge_data["presence_count"] = signal["presence_count"]
            edge_data["crowdedness_score"] = signal["effective_crowd_score"]
            edge_data["crowdedness_level"] = signal["crowdedness_level"]
            edge_data["effective_walking_time"] = edge_data.get("walking_time", 0) * signal["eta_multiplier"]


def cleanup_stale_presence(db: Session) -> None:
    cutoff = datetime.utcnow() - timedelta(minutes=CROWD_PING_TTL_MINUTES)
    db.query(PresencePing).filter(PresencePing.updated_at < cutoff).delete(synchronize_session=False)


def _weather_impact(condition: str) -> float:
    return {
        "clear": 1.0,
        "cloudy": 1.03,
        "sunny": 1.06,
        "rainy": 1.22,
        "snow": 1.45,
    }.get(condition.lower(), 1.0)


def _weather_code_to_condition(code: Optional[int], precipitation: Optional[float]) -> str:
    if precipitation and precipitation > 0:
        return "rainy"
    if code is None:
        return "clear"
    if code in (0, 1):
        return "clear"
    if code in (2, 3, 45, 48):
        return "cloudy"
    if 51 <= code <= 82 or 95 <= code <= 99:
        return "rainy"
    if 71 <= code <= 77 or 85 <= code <= 86:
        return "snow"
    return "clear"
