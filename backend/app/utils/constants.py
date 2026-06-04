"""
Constants used throughout the application
"""

# Location categories
LOCATION_CATEGORIES = {
    "LIBRARY": "Library",
    "HOSTEL": "Hostel",
    "DEPARTMENT": "Department",
    "BUILDING": "Building",
    "GATE": "Gate",
    "CAFE": "Cafe",
    "BUS_STOP": "Bus Stop",
    "SPORTS": "Sports Facility",
    "PARKING": "Parking",
    "HEALTH": "Health Center",
    "ADMIN": "Administration",
    "LABORATORY": "Laboratory"
}

# Route types
ROUTE_TYPES = {
    "ROAD": "Road",
    "FOOTPATH": "Footpath",
    "CORRIDOR": "Corridor",
    "BRIDGE": "Bridge",
    "RAMP": "Ramp"
}

# Routing modes
ROUTING_MODES = {
    "FASTEST": "fastest",
    "SHORTEST": "shortest",
    "ACCESSIBLE": "accessible",
    "LOW_CROWD": "low_crowd"
}

# Accessibility factors
ACCESSIBILITY_WEIGHTS = {
    "has_stairs": -0.5,
    "has_slope": -0.2,
    "is_wheelchair_accessible": 0.8,
    "has_ramp": 0.5,
    "has_elevator": 0.6,
    "width": 0.3
}

# Default speeds (m/s)
DEFAULT_WALKING_SPEED = 1.4  # Standard walking speed
ACCESSIBLE_WALKING_SPEED = 1.0  # Slower for accessibility

# Crowdedness levels
CROWDEDNESS_LEVELS = {
    "LOW": 0.2,
    "MEDIUM": 0.5,
    "HIGH": 0.8,
    "VERY_HIGH": 1.0
}

