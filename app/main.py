"""
FastAPI Main Application
Childcare Location Intelligence System
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from loguru import logger
import sys
import time

from app.config import get_settings

# Make agent import optional
try:
    from app.agents.location_agent import get_agent
    AGENT_AVAILABLE = True
except ImportError:
    logger.warning("Agent framework not available - running without agent support")
    AGENT_AVAILABLE = False
    get_agent = None

# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add(
    "logs/app.log",
    rotation="500 MB",
    retention="10 days",
    level="INFO"
)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler
    Manages startup and shutdown events
    """
    # Startup
    logger.info("Starting Brightspot Locator AI application...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"LLM Provider: {settings.get_llm_config()['provider']}")
    
    # Initialize agent (singleton) if available
    if AGENT_AVAILABLE and get_agent:
        try:
            agent = await get_agent()
            logger.info("Location analysis agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            logger.warning("Application starting without agent - some endpoints may be unavailable")
    else:
        logger.info("Agent framework not available - using direct data collectors")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered childcare center location intelligence and validation system",
    docs_url="/api/docs" if settings.debug else None,
    redoc_url="/api/redoc" if settings.debug else None,
    lifespan=lifespan
)


# ============================================
# Middleware Configuration
# ============================================

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add X-Process-Time header to responses"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    logger.info(f"Request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response


# ============================================
# Exception Handlers
# ============================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "An error occurred"
        }
    )


# ============================================
# Static Files & Templates
# ============================================

from pathlib import Path

# Mount static files (CSS, JS, images)
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Templates
templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


# ============================================
# Health Check Endpoints
# ============================================

@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "environment": settings.environment,
        "docs": "/api/docs" if settings.debug else None
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time()
    }


@app.get("/api/v1/info")
async def api_info():
    """API information and configuration"""
    llm_config = settings.get_llm_config()
    
    return {
        "api_version": "1.0",
        "features": {
            "validation": True,
            "comparison": settings.enable_comparison_mode,
            "discovery": settings.enable_discovery_mode,
            "batch_analysis": settings.enable_batch_analysis,
            "export_pdf": settings.enable_export_pdf,
            "export_json": settings.enable_export_json,
        },
        "limits": {
            "free_tier_analyses_per_week": settings.free_tier_analyses_per_week,
            "max_concurrent_analyses": settings.max_concurrent_analyses,
            "analysis_timeout_seconds": settings.analysis_timeout_seconds,
        },
        "llm": {
            "provider": llm_config["provider"],
            "model": llm_config.get("model", "N/A"),
        },
        "pricing": {
            "free": f"{settings.free_tier_analyses_per_week}/week",
            "paid": f"${settings.paid_tier_price}",
            "pro": f"${settings.pro_tier_price}/month",
            "premium": f"${settings.premium_tier_price}/month"
        }
    }


# ============================================
# API Routes
# ============================================

# Import and include API routers
from app.api.routes import validation, comparison, analysis, web
app.include_router(validation.router, prefix="/api/v1", tags=["validation"])
app.include_router(comparison.router, prefix="/api/v1", tags=["comparison"])
app.include_router(analysis.router, tags=["analysis"])
app.include_router(web.router, tags=["web"])


# ============================================
# Development/Debug Endpoints
# ============================================

if settings.debug:
    @app.get("/api/debug/config")
    async def debug_config():
        """Debug endpoint to view configuration (dev only)"""
        return {
            "environment": settings.environment,
            "database_url": settings.database_url.replace(settings.mysql_password, "***"),
            "redis_url": settings.redis_url.replace(settings.redis_password, "***") if settings.redis_password else settings.redis_url,
            "llm_config": {
                **settings.get_llm_config(),
                "api_key": "***"
            },
            "features": {
                "discovery": settings.enable_discovery_mode,
                "comparison": settings.enable_comparison_mode,
                "batch": settings.enable_batch_analysis,
            }
        }


# ============================================
# Main Entry Point
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
        workers=settings.workers if not settings.reload else 1
    )
