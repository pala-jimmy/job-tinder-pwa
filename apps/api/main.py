"""
Job Tinder PWA - FastAPI Backend
Main application entrypoint
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import get_settings
from database import create_db_and_tables
from routes.auth import router as auth_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events - startup and shutdown
    """
    # Startup: Create database tables
    print("🚀 Starting Job Tinder API...")
    create_db_and_tables()
    print("✅ Database tables created/verified")
    yield
    # Shutdown: cleanup if needed
    print("👋 Shutting down Job Tinder API...")


app = FastAPI(
    title="Job Tinder API",
    description="Backend API for Job Tinder PWA - Two-sided recruitment platform",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Job Tinder API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring
    Returns API status and basic system info
    """
    return {
        "status": "healthy",
        "service": "job-tinder-api",
        "version": "0.1.0",
        "database": settings.database_url.split("://")[0],  # Just show DB type
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
