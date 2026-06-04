"""
Small offline seed dataset for local development and demos.
"""
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.models import Location, Route, User

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


LOCATIONS = [
    {
        "name": "IIT Roorkee Main Gate",
        "category": "Gate",
        "description": "Primary entrance on the Roorkee campus with security and campus access.",
        "latitude": 29.8665,
        "longitude": 77.8950,
        "is_accessible": True,
        "has_ramp": True,
        "has_wheelchair_access": True,
        "accessibility_score": 0.9,
    },
    {
        "name": "Mahatma Gandhi Central Library",
        "category": "Library",
        "description": "Central library with study halls and digital academic resources.",
        "latitude": 29.8649,
        "longitude": 77.8959,
        "is_accessible": True,
        "has_elevator": True,
        "has_ramp": True,
        "has_wheelchair_access": True,
        "accessibility_score": 0.95,
    },
    {
        "name": "Rajendra Bhawan",
        "category": "Hostel",
        "description": "Hostel node with finer routing around the bhawan entrance.",
        "latitude": 29.8680,
        "longitude": 77.9005,
        "is_accessible": True,
        "has_ramp": True,
        "has_wheelchair_access": True,
        "accessibility_score": 0.82,
    },
    {
        "name": "Rajendra Bhawan Mess",
        "category": "Hostel",
        "description": "Mess-side node for hostel-level routes that public maps usually miss.",
        "latitude": 29.8684,
        "longitude": 77.9010,
        "is_accessible": True,
        "has_ramp": True,
        "has_wheelchair_access": True,
        "accessibility_score": 0.86,
    },
    {
        "name": "Department of Computer Science and Engineering",
        "category": "Department",
        "description": "Labs, faculty rooms, seminar halls, and project spaces.",
        "latitude": 29.8652,
        "longitude": 77.8994,
        "is_accessible": True,
        "has_elevator": True,
        "has_ramp": True,
        "has_wheelchair_access": True,
        "accessibility_score": 0.88,
    },
    {
        "name": "Alaknanda Chowk",
        "category": "Cafe",
        "description": "Popular campus meeting and food point near hostel movement paths.",
        "latitude": 29.8668,
        "longitude": 77.8983,
        "is_accessible": True,
        "has_ramp": True,
        "has_wheelchair_access": True,
        "accessibility_score": 0.8,
    },
    {
        "name": "James Thomson Building",
        "category": "Building",
        "description": "Iconic administrative building and central orientation landmark.",
        "latitude": 29.8642,
        "longitude": 77.8968,
        "is_accessible": True,
        "has_ramp": True,
        "has_wheelchair_access": True,
        "accessibility_score": 0.84,
    },
    {
        "name": "Lecture Hall Complex",
        "category": "Building",
        "description": "High-traffic classroom zone where admin and live app crowd signals matter.",
        "latitude": 29.8634,
        "longitude": 77.8989,
        "is_accessible": True,
        "has_elevator": True,
        "has_ramp": True,
        "has_wheelchair_access": True,
        "accessibility_score": 0.9,
    },
    {
        "name": "Saharanpur Campus Bus Stop",
        "category": "Bus Stop",
        "description": "Campus shuttle and bus pickup point.",
        "latitude": 29.8628,
        "longitude": 77.8944,
        "is_accessible": True,
        "has_ramp": True,
        "has_wheelchair_access": True,
        "accessibility_score": 0.78,
    },
]


ROUTES = [
    ("IIT Roorkee Main Gate", "James Thomson Building", 220, 190, "Footpath", 0.18, True, False, False),
    ("James Thomson Building", "Mahatma Gandhi Central Library", 120, 105, "Footpath", 0.22, True, False, False),
    ("Mahatma Gandhi Central Library", "Department of Computer Science and Engineering", 310, 270, "Corridor", 0.35, True, False, False),
    ("Department of Computer Science and Engineering", "Lecture Hall Complex", 230, 205, "Footpath", 0.45, True, False, False),
    ("Lecture Hall Complex", "Alaknanda Chowk", 260, 230, "Footpath", 0.58, True, False, False),
    ("Alaknanda Chowk", "Rajendra Bhawan", 300, 275, "Road", 0.62, True, False, False),
    ("Rajendra Bhawan", "Rajendra Bhawan Mess", 75, 65, "Footpath", 0.42, True, False, False),
    ("Mahatma Gandhi Central Library", "Alaknanda Chowk", 280, 245, "Footpath", 0.38, True, False, False),
    ("IIT Roorkee Main Gate", "Saharanpur Campus Bus Stop", 300, 265, "Road", 0.25, True, False, False),
    ("Saharanpur Campus Bus Stop", "Lecture Hall Complex", 390, 350, "Road", 0.32, False, True, False),
]


def seed_initial_data(db: Session) -> None:
    """Populate an empty database with enough data for offline navigation."""
    old_demo = db.query(Location).filter(Location.name == "Main Gate").first()
    iit_demo = db.query(Location).filter(Location.name == "James Thomson Building").first()
    if old_demo is not None and iit_demo is None:
        db.query(Route).delete(synchronize_session=False)
        db.query(Location).delete(synchronize_session=False)
        db.commit()

    if db.query(Location).count() == 0:
        for location in LOCATIONS:
            db.add(Location(**location))
        db.commit()

    if db.query(Route).count() == 0:
        locations = {location.name: location for location in db.query(Location).all()}
        for source, destination, distance, walking_time, route_type, crowd, accessible, stairs, blocked in ROUTES:
            for route_source, route_destination in ((source, destination), (destination, source)):
                db.add(
                    Route(
                        source_id=locations[route_source].id,
                        destination_id=locations[route_destination].id,
                        distance=distance,
                        walking_time=walking_time,
                        route_type=route_type,
                        accessibility_score=0.85 if accessible else 0.45,
                        crowdedness_score=crowd,
                        is_wheelchair_accessible=accessible,
                        has_stairs=stairs,
                        has_slope=not accessible,
                        slope_percentage=8 if not accessible else 2,
                        is_blocked=blocked,
                        has_weather_cover=route_type == "Corridor",
                        has_lighting=True,
                    )
                )
        db.commit()

    legacy_admin = db.query(User).filter(User.email == "admin@campus.local").first()
    if legacy_admin is not None:
        legacy_admin.email = "admin@campusmap.dev"
        db.commit()

    if db.query(User).filter(User.email == "admin@campusmap.dev").first() is None:
        db.add(
            User(
                email="admin@campusmap.dev",
                username="admin",
                full_name="Campus Admin",
                hashed_password=pwd_context.hash("Admin@123"),
                is_admin=True,
            )
        )
        db.commit()
