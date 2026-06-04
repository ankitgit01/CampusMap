# Architecture Documentation

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                       │
│  - User Interface                                             │
│  - Map Visualization (Leaflet)                                │
│  - Search & Navigation                                        │
│  - Admin Dashboard                                            │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   API Gateway (FastAPI)                       │
│  - Authentication (JWT)                                       │
│  - Request Routing                                            │
│  - Input Validation                                           │
└──────┬──────────────────────────────────────┬────────────────┘
       │                                      │
       ▼                                      ▼
┌──────────────────────────────────┐ ┌─────────────────────────┐
│  Business Logic Layer            │ │   ML/AI Services        │
│  - Navigation Service            │ │  - Crowd Predictor      │
│  - Graph Engine                  │ │  - ETA Predictor        │
│  - User Management               │ │  - Recommendation Engine│
│  - Search Service                │ │                         │
└──────────────┬───────────────────┘ └──────────┬──────────────┘
               │                                │
               └────────────┬───────────────────┘
                            │
                            ▼
                   ┌────────────────────┐
                   │   PostgreSQL DB    │
                   │  - Users           │
                   │  - Locations       │
                   │  - Routes          │
                   │  - History         │
                   └────────────────────┘
```

## Backend Architecture

### Folder Structure
```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database configuration
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py
│   │   ├── location.py
│   │   ├── route.py
│   │   └── navigation_history.py
│   ├── schemas/             # Pydantic schemas
│   ├── api/                 # API routes
│   │   ├── auth.py
│   │   ├── navigation.py
│   │   ├── admin.py
│   │   ├── search.py
│   │   └── history.py
│   ├── graph/               # Graph algorithms
│   │   ├── graph_builder.py # Build graph from DB
│   │   ├── dijkstra.py      # Dijkstra algorithm
│   │   ├── astar.py         # A* algorithm
│   │   └── accessibility.py # Accessibility routing
│   ├── ml/                  # Machine learning
│   │   ├── crowd_predictor.py
│   │   ├── eta_predictor.py
│   │   └── recommendation.py
│   └── utils/               # Utilities
│       ├── constants.py
│       └── helpers.py
├── requirements.txt
├── config.py
└── .env.example
```

### Component Details

#### Authentication (JWT)
- Token expiry: 30 minutes
- Refresh token: Extended validity
- Password hashing: bcrypt

#### Graph Engine
1. **Graph Builder**
   - Loads locations from database as nodes
   - Creates edges from routes
   - Bidirectional edges for undirected paths
   - Filters blocked routes

2. **Dijkstra Router**
   - Time complexity: O((V+E) log V)
   - Supports multiple weight keys
   - Three modes: fastest, shortest, accessible

3. **A* Router**
   - Heuristic: Straight-line distance
   - Better performance than Dijkstra
   - Suitable for large graphs

4. **Accessibility Router**
   - Penalizes stairs and slopes
   - Prefers ramps and elevators
   - Calculates accessibility scores

#### ML Models

1. **Crowd Predictor** (XGBoost)
   - Features: Hour, day, peak hours, weather, events
   - Output: Crowdedness (0-1)
   - Fallback: Heuristic prediction

2. **ETA Predictor** (Gradient Boosting)
   - Inputs: Distance, crowdedness, weather, time, complexity
   - Output: Time in seconds
   - Confidence: 0.5-0.95

3. **Recommendation Engine**
   - User history analysis
   - Destination frequency
   - Routing mode preferences
   - Similar user detection

#### Search Service
- Fuzzy matching for typo tolerance
- Category filtering
- Geospatial queries (nearby)
- Full-text search ready

## Frontend Architecture

### Folder Structure
```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── MapComponent.jsx
│   │   ├── NavBar.jsx
│   │   ├── SearchBar.jsx
│   │   ├── RouteDetails.jsx
│   │   └── AdminPanel.jsx
│   ├── pages/               # Full pages
│   │   ├── Home.jsx
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   ├── Navigation.jsx
│   │   ├── History.jsx
│   │   └── Admin.jsx
│   ├── services/            # API services
│   │   ├── api.js          # Axios config
│   │   ├── auth.js
│   │   └── mapService.js
│   ├── styles/
│   │   └── index.css
│   ├── App.jsx              # Main app
│   └── index.jsx            # Entry point
├── public/                  # Static assets
├── index.html               # HTML template
├── vite.config.js
├── tailwind.config.js
└── package.json
```

### Component Hierarchy
```
App
├── NavBar
├── Home
├── Login
├── Register
├── Navigation
│   ├── SearchBar
│   ├── RouteDetails
│   └── MapComponent
├── History
├── Admin
│   └── AdminPanel
│       ├── StatCard
│       └── Tables
└── Protected Routes
```

### State Management
- Context API for authentication
- Local component state for forms
- Zustand for global state (to be implemented)
- URL params for navigation

## Database Design

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    username VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    full_name VARCHAR,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);
```

### Locations Table
```sql
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    category VARCHAR NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    accessibility_score FLOAT,
    is_accessible BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Routes Table
```sql
CREATE TABLE routes (
    id SERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES locations(id),
    destination_id INTEGER REFERENCES locations(id),
    distance FLOAT NOT NULL,
    walking_time FLOAT NOT NULL,
    accessibility_score FLOAT,
    crowdedness_score FLOAT,
    is_blocked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Navigation History Table
```sql
CREATE TABLE navigation_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    source_location VARCHAR NOT NULL,
    destination_location VARCHAR NOT NULL,
    routing_mode VARCHAR NOT NULL,
    distance FLOAT,
    estimated_time FLOAT,
    actual_time FLOAT,
    timestamp TIMESTAMP DEFAULT NOW(),
    completed BOOLEAN DEFAULT FALSE
);
```

## Data Flow

### Route Finding Flow
1. User enters source and destination
2. Frontend calls `/navigation/find-route`
3. Backend:
   - Finds location IDs
   - Builds graph from database
   - Runs selected algorithm (Dijkstra/A*)
   - Gets route based on mode
   - Predicts ETA and crowdedness
4. Frontend displays route on map

### Crowdedness Prediction Flow
1. Check if ML model is trained
2. Extract time features (hour, day, peak)
3. Get route data and weather
4. Run XGBoost model
5. Return crowdedness score (0-1)
6. Apply to affected routes

### User History Flow
1. After navigation completes
2. User saves navigation
3. Store in NavigationHistory table
4. Calculate statistics
5. Use for recommendations

## Security

### Authentication
- JWT tokens in Authorization header
- Token refresh mechanism
- Secure password hashing (bcrypt)

### Authorization
- Role-based access control (RBAC)
- Admin-only endpoints
- User-specific data isolation

### Data Validation
- Pydantic schemas
- Input sanitization
- SQL injection prevention (ORM)

### CORS
- Configurable origins
- Credentials allowed
- Methods: GET, POST, PUT, DELETE, PATCH

## Performance Optimizations

### Backend
- Database indexing on frequent columns
- Query optimization
- Caching (to be implemented)
- Async operations

### Frontend
- Code splitting with Vite
- Lazy loading components
- Memoization for expensive calculations
- Asset optimization

### Algorithms
- Bidirectional search (future)
- Route caching
- Heuristic-based early termination
- Efficient data structures

## Scalability Considerations

1. **Database**
   - Connection pooling
   - Read replicas for searches
   - Sharding by campus zone

2. **API**
   - Load balancing with Nginx
   - Horizontal scaling with Docker
   - Message queues for async tasks

3. **Frontend**
   - CDN for static assets
   - Service workers for offline
   - Progressive Web App (PWA)

## Deployment

### Development
```bash
# Backend
python -m uvicorn app.main:app --reload

# Frontend
npm run dev
```

### Production
```bash
# Backend
gunicorn -w 4 -b 0.0.0.0:8000 app.main:app

# Frontend
npm run build
# Serve with Nginx or similar
```

## Testing Strategy

### Backend Tests
- Unit tests for algorithms
- Integration tests for APIs
- Database migration tests
- ML model validation

### Frontend Tests
- Component unit tests
- Integration tests
- E2E tests with Cypress
- Performance testing

## Monitoring & Logging

- Application logs (DEBUG/INFO/ERROR)
- API request/response logging
- Database query logging
- Error tracking with Sentry
- Performance monitoring

## Future Enhancements

1. **Real-time Updates**
   - WebSocket for live crowdedness
   - Push notifications
   - Live location tracking

2. **Advanced Features**
   - Multi-destination routing
   - Transport modes (bus, auto)
   - Event calendar integration
   - Weather integration

3. **Mobile App**
   - React Native version
   - Offline support
   - GPS integration
   - Push notifications

4. **Analytics**
   - User behavior analysis
   - Popular routes
   - Peak time analysis
   - Campus redesign suggestions
