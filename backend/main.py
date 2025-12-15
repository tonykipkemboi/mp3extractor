"""
FastAPI Main Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from . import __version__
from .database import init_db
from .schemas import HealthResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager - runs on startup and shutdown
    """
    # Startup
    print("Initializing database...")
    init_db()
    print("Database initialized successfully")

    yield

    # Shutdown
    print("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="MP3 Extractor API",
    description="API for MP4 to MP3 conversion with real-time progress",
    version=__version__,
    lifespan=lifespan
)

# CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js default
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint

    Returns API status, version, and database connection status
    """
    return HealthResponse(
        status="healthy",
        version=__version__,
        database="connected"
    )


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API info
    """
    return {
        "name": "MP3 Extractor API",
        "version": __version__,
        "docs": "/docs",
        "health": "/api/health"
    }


# Import and include routers
from .api import files, conversion, jobs

app.include_router(files.router, prefix="/api/v1")
app.include_router(conversion.router, prefix="/api/v1")
app.include_router(jobs.router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
