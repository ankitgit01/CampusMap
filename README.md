# CampusMap - Smart Campus Navigation System

A comprehensive, AI-powered campus navigation platform that helps users efficiently navigate campuses while considering accessibility, crowdedness, and optimal routing.

## 🎯 Features

### Core Features
- **Smart Routing**: Multiple routing modes (Fastest, Shortest, Accessible, Low-Crowd)
- **Dijkstra & A\* Algorithms**: Compare execution time and route quality
- **Accessibility-Aware Navigation**: Routes for mobility constraints and wheelchair accessibility
- **Crowdedness Prediction**: ML-powered crowd prediction using XGBoost/Random Forest
- **Dynamic ETA Prediction**: Travel time estimates considering weather and crowdedness
- **Campus Map Visualization**: Interactive map with route highlighting
- **Search & Discovery**: Fast location search with fuzzy matching

### User Features
- **User Authentication**: Secure registration and login
- **Favorites**: Save frequently visited locations
- **Navigation History**: Track all navigation journeys
- **Personalized Recommendations**: Route suggestions based on history
- **Accessibility Profiles**: Customize accessibility requirements

### Admin Features
- **Location Management**: Add, edit, delete campus locations
- **Route Management**: Add, edit, and delete routes
- **Block/Unblock Routes**: Mark roads as blocked due to construction
- **Dashboard**: Real-time statistics and analytics
- **User Management**: Admin controls for users

### AI/ML Features
1. **Crowd Prediction**: Predict congestion levels based on time, day, events
2. **ETA Prediction**: Estimate arrival time considering multiple factors
3. **Route Recommendation Engine**: Suggest routes based on user preferences
4. **Accessibility Scoring**: Assign accessibility scores to paths

## 🏗️ Architecture

### Backend
- **Framework**: FastAPI (Python)
- **Database**: SQLite by default for local/offline development; PostgreSQL supported through `DATABASE_URL`
- **APIs**: RESTful with JWT authentication
- **Graph Engine**: Dijkstra + A* algorithms
- **ML Models**: XGBoost, Random Forest

### Frontend
- **Framework**: React 18 with Vite
- **UI Library**: Tailwind CSS
- **Mapping**: Leaflet for interactive maps
- **State Management**: Zustand
- **Routing**: React Router v6

### Database
- **Users**: Authentication and profiles
- **Locations**: Campus nodes/buildings
- **Routes**: Connections with metadata
- **Navigation History**: User journey logs

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+ only if you want to run the production-style database instead of local SQLite

### Backend Setup

1. **Clone and navigate**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure database**:
```bash
cp .env.example .env
# Default local database: sqlite:///./campus_map.db
# Optional PostgreSQL: set DATABASE_URL=postgresql://user:password@host:5432/dbname
```

4. **Start server**:
```bash
python -m uvicorn app.main:app --reload
```

Server runs on `http://localhost:8000`, creates tables automatically, and seeds local demo data.

Default local admin:
- Email: `admin@campusmap.dev`
- Password: `Admin@123`

### Frontend Setup

1. **Navigate and install**:
```bash
cd frontend
npm install
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with API URL
```

3. **Start development server**:
```bash
npm run dev
```

Application runs on `http://localhost:3000`

## 📡 API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user
- `POST /auth/refresh-token` - Refresh token

### Navigation
- `POST /navigation/find-route` - Find route with mode/algorithm
- `POST /navigation/compare-routes` - Compare all routing modes
- `GET /navigation/route-details/{id}` - Get route details
- `GET /navigation/accessibility-metrics` - Campus accessibility stats

### Search
- `GET /search/locations` - Search locations
- `GET /search/nearby` - Find nearby locations
- `GET /search/accessible` - Find accessible locations
- `GET /search/trending` - Get trending destinations

### History
- `POST /history/save` - Save navigation
- `GET /history/user` - Get user history
- `POST /history/favorites/add` - Add favorite
- `GET /history/recommendations` - Get recommendations

### Admin
- `POST /admin/locations` - Create location
- `PUT /admin/locations/{id}` - Update location
- `DELETE /admin/locations/{id}` - Delete location
- `POST /admin/routes` - Create route
- `PATCH /admin/routes/{id}/block` - Block route
- `GET /admin/statistics` - Admin dashboard stats

## 🧮 Algorithms

### Dijkstra's Algorithm
- **Time Complexity**: O((V + E) log V) with binary heap
- **Best for**: Shortest path finding
- **Modes**: Fastest time, Shortest distance, Accessible routing

### A\* Algorithm
- **Time Complexity**: O((V + E) log V) with heuristic
- **Best for**: Optimal pathfinding with heuristics
- **Heuristic**: Straight-line distance (Euclidean)
- **Modes**: All modes with better performance

### Crowd Prediction
- **Model**: XGBoost Regressor
- **Features**: Hour, day, peak hours, weather, events
- **Output**: Crowdedness score (0-1)

### ETA Prediction
- **Model**: Gradient Boosting
- **Factors**: Distance, crowdedness, weather, time, complexity
- **Confidence**: 0.5-0.95 based on inputs

## 📊 Database Schema

### Users Table
- id, email, username, password, full_name
- accessibility_requirements, created_at, last_login

### Locations Table
- id, name, category, latitude, longitude
- accessibility_score, has_elevator, has_ramp
- description, image_url

### Routes Table
- id, source_id, destination_id
- distance, walking_time, route_type
- accessibility_score, crowdedness_score
- is_blocked, has_stairs, has_slope

### NavigationHistory Table
- id, user_id, source_location, destination_location
- routing_mode, distance, estimated_time, actual_time
- timestamp, completed

## 🔐 Security

- JWT-based authentication
- Password hashing with bcrypt
- CORS enabled for frontend
- Protected admin endpoints
- Input validation with Pydantic

## 🧪 Testing

Run tests:
```bash
# Backend tests
pytest backend/tests/

# Frontend tests
npm test
```

## 🚢 Deployment

### Docker Deployment
```bash
docker-compose up
```

### Production Checklist
- [ ] Change SECRET_KEY in .env
- [ ] Set DEBUG=False
- [ ] Configure database connection
- [ ] Set up SSL/HTTPS
- [ ] Configure allowed hosts
- [ ] Set up logging

## 📈 Performance

- **Route Finding**: <100ms average (Dijkstra)
- **Search**: <50ms with fuzzy matching
- **ETA Prediction**: <10ms inference
- **Map Load**: <2s initial load

## 🎓 Learning Outcomes

This project covers:
- Graph algorithms and data structures
- Full-stack web development
- Machine learning integration
- Database design and optimization
- API design patterns
- Authentication and security
- Geospatial data handling
- Real-world problem solving

## 📚 Documentation

- [API Documentation](docs/API.md)
- [Architecture Guide](docs/ARCHITECTURE.md)
- [Setup Instructions](docs/SETUP.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

MIT License - see LICENSE file for details

## 👥 Authors

- Campus Navigation Team

## 🆘 Support

For issues and questions:
1. Check existing documentation
2. Search GitHub issues
3. Create a new issue with details

## 🎉 Acknowledgments

- Built for solving real campus navigation challenges
- Inspired by Google Maps and campus-specific needs
- Thanks to the open-source community
