from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.core.database import init_db
from app.api import agents, calls, transcripts, costs, tools, webhooks

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    print("Starting up...")
    
    # Check if database is configured
    if settings.SUPABASE_DB_HOST or (settings.DATABASE_URL and "localhost" not in settings.DATABASE_URL):
        try:
            await init_db()
            print("Database initialized")
        except Exception as e:
            print(f"Warning: Could not connect to database: {e}")
            print("Server will start but database features may not work")
    else:
        print("Database not configured - running in demo mode")
    
    yield
    # Shutdown
    print("Shutting down...")


app = FastAPI(
    title="Voice AI Platform API",
    description="API for managing AI voice agents with Twilio and LiveKit",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agents.router, prefix="/api")
app.include_router(calls.router, prefix="/api")
app.include_router(transcripts.router, prefix="/api")
app.include_router(costs.router, prefix="/api")
app.include_router(tools.router, prefix="/api")
app.include_router(webhooks.router)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Voice AI Platform API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok"}


# API Documentation
@app.get("/api/docs")
async def docs():
    """Redirect to API documentation"""
    return {"message": "Visit /docs for Swagger UI documentation"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
