"""
FastAPI main application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.database import Base, SessionLocal, engine
from app.api import auth, navigation, admin, search, history
from app.seed import seed_initial_data

# Create tables
Base.metadata.create_all(bind=engine)
with SessionLocal() as db:
    seed_initial_data(db)

# Initialize FastAPI app
app = FastAPI(
    title="Campus Map Navigation API",
    description="Smart campus navigation with accessibility and crowd prediction",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(navigation.router)
app.include_router(admin.router)
app.include_router(search.router)
app.include_router(history.router)

@app.get("/")
def read_root():
    """API root endpoint"""
    return {
        "title": "Campus Map Navigation API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "auth": "/auth",
            "navigation": "/navigation",
            "admin": "/admin",
            "search": "/search",
            "history": "/history"
        },
        "docs": "/docs",
        "openapi_schema": "/openapi.json"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
