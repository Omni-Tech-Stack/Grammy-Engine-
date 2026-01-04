"""
Grammy Prompt Engine™ - FastAPI Backend Entry Point
Main application configuration and route registration
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time
import os

from api import (
    prompt_engine,
    songgen,
    vocalgen,
    mixmaster,
    grammy_meter,
    upload,
    auth
)
from services.supabase_client import init_supabase
from utils.config import log_configuration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("🎵 Grammy Engine starting up...")
    
    # Log configuration
    log_configuration()
    
    # Initialize Supabase connection
    try:
        init_supabase()
        logger.info("✅ Supabase initialized")
    except Exception as e:
        logger.error(f"❌ Supabase initialization failed: {e}")
    
    yield
    
    logger.info("🎵 Grammy Engine shutting down...")


# Initialize FastAPI app
app = FastAPI(
    title="Grammy Prompt Engine™",
    description="AI-Powered Music Generation & Hit Prediction Platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app",
        "https://*.railway.app",
        "https://grammyengine.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc) if app.debug else "An unexpected error occurred"
        }
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Enhanced health check for Railway"""
    health_status = {
        "status": "healthy",
        "service": "Grammy Prompt Engine",
        "version": "1.0.0",
        "checks": {}
    }
    
    # Database check
    try:
        # Quick DB connection test
        from services.supabase_client import supabase
        if supabase:
            health_status["checks"]["database"] = "connected"
        else:
            health_status["checks"]["database"] = "not_initialized"
    except Exception as e:
        health_status["checks"]["database"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Redis check (if configured)
    try:
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            from redis import Redis
            redis_client = Redis.from_url(redis_url, socket_connect_timeout=2)
            redis_client.ping()
            health_status["checks"]["redis"] = "connected"
        else:
            health_status["checks"]["redis"] = "not_configured"
    except Exception as e:
        health_status["checks"]["redis"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status


@app.get("/")
async def root():
    return {
        "message": "🎵 Grammy Prompt Engine™ API",
        "version": "1.0.0",
        "docs": "/api/docs"
    }


# Register API routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(prompt_engine.router, prefix="/api/prompt", tags=["Prompt Engine"])
app.include_router(songgen.router, prefix="/api/songgen", tags=["Song Generation"])
app.include_router(vocalgen.router, prefix="/api/vocalgen", tags=["Vocal Generation"])
app.include_router(mixmaster.router, prefix="/api/mixmaster", tags=["Mix & Master"])
app.include_router(grammy_meter.router, prefix="/api/meter", tags=["Grammy Meter"])
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )
