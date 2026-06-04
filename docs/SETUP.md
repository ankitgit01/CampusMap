# Setup Instructions

## Prerequisites

Before starting, ensure you have:
- Python 3.8 or higher
- Node.js 16 or higher
- PostgreSQL 12 or higher
- Git
- Text editor or IDE (VS Code recommended)

## Backend Setup

### 1. Database Setup

#### Windows (with PostgreSQL installed)

1. Open pgAdmin or use psql:
```bash
psql -U postgres
```

2. Create database and user:
```sql
CREATE DATABASE campus_map;
CREATE USER campus_user WITH PASSWORD 'campus_password';
ALTER ROLE campus_user SET client_encoding TO 'utf8';
ALTER ROLE campus_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE campus_user SET default_transaction_deferrable TO on;
ALTER ROLE campus_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE campus_map TO campus_user;
\q
```

#### Linux/Mac

```bash
# Using Homebrew (Mac)
brew install postgresql

# Start PostgreSQL service
brew services start postgresql

# Create database
createdb campus_map

# Create user
psql postgres
CREATE USER campus_user WITH PASSWORD 'campus_password';
GRANT ALL PRIVILEGES ON DATABASE campus_map TO campus_user;
\q
```

#### Using Docker (Optional)

```bash
docker run --name postgres-campus \
  -e POSTGRES_USER=campus_user \
  -e POSTGRES_PASSWORD=campus_password \
  -e POSTGRES_DB=campus_map \
  -p 5432:5432 \
  -d postgres:15
```

### 2. Python Environment Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# Key settings:
# DATABASE_URL=postgresql://campus_user:campus_password@localhost:5432/campus_map
# SECRET_KEY=your-secret-key-here (change in production!)
```

### 4. Initialize Database

```bash
# Create database tables
python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"

# Or using Alembic (if migrations are set up):
# alembic upgrade head
```

### 5. Seed Sample Data (Optional)

Create `backend/seed_data.py`:

```python
from app.database import SessionLocal, Base, engine
from app.models import Location, Route

# Create tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Add sample locations
locations = [
    Location(
        name="Central Library",
        category="Library",
        latitude=28.5355,
        longitude=77.2,
        is_accessible=True,
        accessibility_score=0.9
    ),
    Location(
        name="Student Hostel 5",
        category="Hostel",
        latitude=28.5360,
        longitude=77.1995,
        is_accessible=True,
        accessibility_score=0.8
    ),
    # Add more locations...
]

for loc in locations:
    db.add(loc)

db.commit()
print("Sample data seeded!")
```

Run: `python seed_data.py`

### 6. Start Backend Server

```bash
# Run development server
python -m uvicorn app.main:app --reload

# Or with custom settings
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server will run on: `http://localhost:8000`

**Check API docs**: `http://localhost:8000/docs`

## Frontend Setup

### 1. Node.js Dependencies

```bash
cd frontend

# Install packages
npm install
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API URL
# VITE_API_URL=http://localhost:8000
```

### 3. Start Development Server

```bash
# Run development server
npm run dev

# Server will run on: http://localhost:5173
```

### 4. Build for Production

```bash
# Create production build
npm run build

# Preview production build
npm run preview
```

## Complete Project Setup (Quick Start)

### Setup Both Backend & Frontend at Once

```bash
# 1. Clone project
cd CampusMap

# 2. Setup Backend
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env with database URL
python -m uvicorn app.main:app --reload &

# 3. Setup Frontend (in new terminal)
cd ../frontend
npm install
cp .env.example .env
npm run dev
```

## Docker Setup (Optional)

### Using Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: campus_user
      POSTGRES_PASSWORD: campus_password
      POSTGRES_DB: campus_map
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    command: python -m uvicorn app.main:app --host 0.0.0.0
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://campus_user:campus_password@postgres:5432/campus_map
    depends_on:
      - postgres

  frontend:
    build: ./frontend
    command: npm run dev -- --host
    ports:
      - "3000:3000"
    environment:
      VITE_API_URL: http://localhost:8000

volumes:
  postgres_data:
```

Run:
```bash
docker-compose up
```

## Testing Setup

### Backend Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest backend/tests/

# With coverage
pytest --cov=app backend/tests/
```

### Frontend Tests

```bash
# Install test dependencies
npm install --save-dev vitest @testing-library/react @testing-library/jest-dom

# Run tests
npm test
```

## Troubleshooting

### Backend Issues

**Error: "Cannot connect to database"**
- Check PostgreSQL is running
- Verify DATABASE_URL in .env
- Ensure database exists: `psql -U postgres -l`

**Error: "Port 8000 already in use"**
```bash
# Kill process on port 8000
# Windows: netstat -ano | findstr :8000, then taskkill /PID <PID>
# Linux/Mac: lsof -i :8000, then kill -9 <PID>

# Or use different port
python -m uvicorn app.main:app --port 8001 --reload
```

**Error: "ModuleNotFoundError"**
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### Frontend Issues

**Error: "npm: command not found"**
- Node.js not installed. Download from nodejs.org

**Error: "Port 3000 already in use"**
- Vite will automatically try port 3001
- Or specify custom port: `npm run dev -- --port 3001`

**Error: "CORS error"**
- Backend CORS not configured for frontend URL
- Check ALLOWED_ORIGINS in backend config

### Database Issues

**Cannot create database**
```bash
# Check if PostgreSQL service is running
# Windows: services.msc, find PostgreSQL
# Mac: brew services list
# Linux: sudo systemctl status postgresql
```

**"Role doesn't exist"**
```bash
# Recreate user
psql -U postgres
DROP USER IF EXISTS campus_user;
CREATE USER campus_user WITH PASSWORD 'campus_password';
GRANT ALL PRIVILEGES ON DATABASE campus_map TO campus_user;
```

## Verification Checklist

- [ ] Python 3.8+ installed: `python --version`
- [ ] Node.js 16+ installed: `node --version`
- [ ] PostgreSQL running: `psql --version`
- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] Database created and configured
- [ ] Backend starts on http://localhost:8000
- [ ] Frontend starts on http://localhost:3000
- [ ] Can access API docs: http://localhost:8000/docs
- [ ] Can login to frontend

## Next Steps

1. **Add Sample Data**: Populate campus map with locations and routes
2. **Configure Admin User**: Create admin account for dashboard
3. **Train ML Models**: Prepare crowdedness and ETA prediction models
4. **Customize Settings**: Update campus-specific configuration
5. **Deploy**: Follow deployment guide for production setup

## Additional Resources

- [API Documentation](../docs/API.md)
- [Architecture Guide](../docs/ARCHITECTURE.md)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
