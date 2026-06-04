# API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication

All protected endpoints require JWT token in Authorization header:
```
Authorization: Bearer <access_token>
```

## Response Format

Standard JSON response:
```json
{
  "data": {...},
  "message": "Success message",
  "status": 200
}
```

Error response:
```json
{
  "detail": "Error message",
  "status": 400
}
```

## Endpoints

### Auth Routes

#### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "password123",
  "full_name": "User Name"
}
```

Response:
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "full_name": "User Name",
  "is_active": true,
  "is_admin": false
}
```

#### Login User
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user_id": 1,
  "is_admin": false
}
```

#### Get Current User
```http
GET /auth/me
Authorization: Bearer <token>
```

### Navigation Routes

#### Find Route
```http
POST /navigation/find-route
Authorization: Bearer <token>

Query Parameters:
  source_location: string (required)
  destination_location: string (required)
  mode: string (fastest|shortest|accessible|low_crowd) - default: fastest
  algorithm: string (dijkstra|astar) - default: dijkstra
```

Response:
```json
{
  "source": "Library",
  "destination": "Cafeteria",
  "mode": "fastest",
  "algorithm": "dijkstra",
  "distance": 450.5,
  "walking_time": 325.7,
  "eta": 325.7,
  "eta_formatted": "5m 25s",
  "eta_confidence": 0.85,
  "path": [1, 5, 12, 8],
  "num_stops": 4,
  "crowdedness_level": "medium",
  "crowdedness_score": 0.45
}
```

#### Compare Routes
```http
POST /navigation/compare-routes

Query Parameters:
  source_location: string
  destination_location: string
```

Response:
```json
{
  "routes": {
    "fastest": {...},
    "shortest": {...},
    "accessible": {...},
    "low_crowd": {...}
  }
}
```

#### Get Route Details
```http
GET /navigation/route-details/{route_id}
```

#### Get Accessibility Metrics
```http
GET /navigation/accessibility-metrics
```

Response:
```json
{
  "total_locations": 45,
  "accessible_locations": 38,
  "accessibility_coverage": 0.84,
  "total_routes": 120,
  "campus_accessibility_index": 0.76
}
```

### Search Routes

#### Search Locations
```http
GET /search/locations

Query Parameters:
  query: string (required, min 1 char)
  category: string (optional)
  limit: integer (default: 10)
```

Response:
```json
{
  "query": "library",
  "results": [
    {
      "id": 1,
      "name": "Central Library",
      "category": "Library",
      "latitude": 28.5355,
      "longitude": 77.2,
      "match_score": 95,
      "description": "Main campus library"
    }
  ],
  "total": 1
}
```

#### Get Categories
```http
GET /search/categories
```

Response:
```json
{
  "categories": [
    {"name": "Library", "count": 3},
    {"name": "Hostel", "count": 8},
    {"name": "Department", "count": 15}
  ]
}
```

#### Search Nearby
```http
GET /search/nearby

Query Parameters:
  latitude: float (required)
  longitude: float (required)
  category: string (optional)
  radius: float (default: 500, in meters)
  limit: integer (default: 10)
```

#### Get Accessible Locations
```http
GET /search/accessible

Query Parameters:
  min_score: float (0-1, default: 0.6)
  category: string (optional)
  limit: integer (default: 10)
```

### History Routes

#### Save Navigation
```http
POST /history/save
Authorization: Bearer <token>

{
  "source_location": "Library",
  "destination_location": "Cafeteria",
  "routing_mode": "fastest",
  "distance": 450,
  "estimated_time": 325
}
```

#### Get Navigation History
```http
GET /history/user
Authorization: Bearer <token>

Query Parameters:
  days: integer (default: 30)
  limit: integer (default: 50)
```

#### Add Favorite
```http
POST /history/favorites/add
Authorization: Bearer <token>

{
  "location_id": 1,
  "alias": "My Library"
}
```

#### Get Favorites
```http
GET /history/favorites
Authorization: Bearer <token>
```

#### Get Recommendations
```http
GET /history/recommendations
Authorization: Bearer <token>

Query Parameters:
  destination: string (optional)
```

#### Get History Statistics
```http
GET /history/statistics
Authorization: Bearer <token>
```

Response:
```json
{
  "user_id": 1,
  "total_navigations": 42,
  "completed_navigations": 40,
  "total_distance_meters": 12500,
  "total_time_seconds": 9000,
  "mode_preferences": {
    "fastest": 25,
    "shortest": 10,
    "accessible": 5
  },
  "most_visited": "Cafeteria"
}
```

### Admin Routes

#### Create Location
```http
POST /admin/locations
Authorization: Bearer <token> (admin required)

{
  "name": "New Building",
  "category": "Building",
  "latitude": 28.5355,
  "longitude": 77.2,
  "is_accessible": true,
  "has_ramp": true
}
```

#### Get Locations
```http
GET /admin/locations

Query Parameters:
  category: string (optional)
  skip: integer (default: 0)
  limit: integer (default: 100)
```

#### Update Location
```http
PUT /admin/locations/{location_id}
Authorization: Bearer <token> (admin required)

{
  "description": "Updated description",
  "is_accessible": true
}
```

#### Create Route
```http
POST /admin/routes
Authorization: Bearer <token> (admin required)

{
  "source_id": 1,
  "destination_id": 2,
  "distance": 450,
  "walking_time": 325,
  "route_type": "Footpath",
  "has_stairs": false,
  "is_wheelchair_accessible": true
}
```

#### Block Route
```http
PATCH /admin/routes/{route_id}/block
Authorization: Bearer <token> (admin required)

{
  "reason": "Under construction"
}
```

#### Unblock Route
```http
PATCH /admin/routes/{route_id}/unblock
Authorization: Bearer <token> (admin required)
```

#### Get Admin Statistics
```http
GET /admin/statistics
Authorization: Bearer <token> (admin required)
```

Response:
```json
{
  "total_locations": 45,
  "total_routes": 120,
  "total_users": 1250,
  "active_routes": 118,
  "blocked_routes": 2,
  "admin_users": 3
}
```

#### Get Blocked Routes
```http
GET /admin/blocked-routes
Authorization: Bearer <token> (admin required)
```

## Error Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden (Admin only)
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

## Rate Limiting

Currently no rate limiting. To be implemented in production.

## Pagination

Use `skip` and `limit` parameters for pagination:
- `skip`: Number of items to skip (default: 0)
- `limit`: Number of items to return (default: 50, max: 100)

## Filtering

Supported query parameters for filtering:
- `category`: Location category
- `days`: Number of days to look back
- `min_score`: Minimum accessibility score

## Sorting

Currently sorted by relevance or date. Custom sorting to be implemented.
