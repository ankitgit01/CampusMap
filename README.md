# CampusMap

CampusMap is a smart campus navigation system that helps users find optimal routes across a campus using graph-based pathfinding algorithms. The application supports multiple routing modes, route comparison, accessibility-aware navigation, and crowd-aware route recommendations.

---

## Features

### Navigation

* Fastest route
* Shortest route
* Accessible route
* Low-crowd route

### Algorithms

* Dijkstra's Algorithm
* A* Search Algorithm

### Map Features

* Interactive campus map
* Route visualization
* Location details
* Search with autocomplete

### Smart Routing

* Crowd-aware navigation
* Weather signal integration
* Route comparison
* Personalized route recommendations

---

## Technology Stack

### Frontend

* React
* Vite
* Tailwind CSS
* Leaflet

### Backend

* FastAPI
* SQLAlchemy
* Python

### Database

* SQLite / PostgreSQL

### Machine Learning

* XGBoost
* Random Forest
* Gradient Boosting

---

## Project Structure

```text
CampusMap
├── backend
│   ├── app
│   │   ├── api
│   │   ├── graph
│   │   ├── ml
│   │   ├── models
│   │   └── services
│   └── requirements.txt
│
├── frontend
│   ├── src
│   │   ├── components
│   │   ├── pages
│   │   └── services
│   └── package.json
│
└── docs
```

---

## Methodology

### Graph Representation

The campus is represented as a weighted graph:

* Nodes represent buildings and campus locations.
* Edges represent walkable routes.
* Edge weights store distance, accessibility information, and crowd scores.

### Routing Engine

#### Dijkstra

Used to find the optimal path by exploring nodes in order of increasing cost.

#### A*

Uses heuristic-based search to reduce exploration and improve efficiency while maintaining optimality.

### Route Modes

#### Fastest

Minimizes estimated travel time.

#### Shortest

Minimizes total distance.

#### Accessible

Prioritizes wheelchair-friendly routes and avoids inaccessible paths.

#### Low Crowd

Avoids highly congested pathways using crowd prediction and route popularity signals.

### Smart Signals

The routing engine incorporates:

* Crowd information
* Route popularity
* Weather conditions
* Accessibility metadata

---

## Installation

### Clone Repository

```bash
git clone <repository-url>
cd CampusMap
```

---

## Backend Setup

```bash
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

# Linux / Mac
source venv/bin/activate

pip install -r requirements.txt
```

### Start Backend

```bash
python -m uvicorn app.main:app --reload
```

Backend runs at:

```text
http://localhost:8000
```

API Documentation:

```text
http://localhost:8000/docs
```

---

## Frontend Setup

Open a new terminal.

```bash
cd frontend

npm install
npm run dev
```

Frontend runs at:

```text
http://localhost:5173
```

---

## Usage

1. Start backend server.
2. Start frontend server.
3. Open the application.
4. Select source and destination.
5. Choose a routing mode.
6. Select Dijkstra or A*.
7. Click Find Route.
8. Use Compare to evaluate different route options.

---

## Future Improvements

* Real-time GPS tracking
* Indoor navigation
* Live crowd sensing
* Mobile application
* Voice navigation
* Event-aware route planning

---

## Learning Outcomes

This project demonstrates:

* Graph algorithms
* Pathfinding systems
* Full-stack development
* REST API design
* Machine learning integration
* Geospatial visualization
* Interactive UI design

---

## Authors

Developed as an academic project for smart campus navigation and route optimization.
