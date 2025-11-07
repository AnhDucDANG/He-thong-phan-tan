from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import traceback
from .core.config import settings
from .routes import gateway_routes, proxy_routes

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="API Gateway",
    description="Central gateway for rental system microservices",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Request logging middleware with error handling
@app.middleware("http")
async def log_requests(request: Request, call_next):
    try:
        logger.info(f"🔵 Incoming: {request.method} {request.url.path}")
        response = await call_next(request)
        logger.info(f"🟢 Response: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"❌ Middleware error: {e}", exc_info=True)
        raise

# Include routes
app.include_router(gateway_routes.router, tags=["Gateway"])
app.include_router(proxy_routes.router, prefix="/api", tags=["Proxy"])

@app.on_event("startup")
async def startup_event():
    """Log service configuration on startup"""
    logger.info("🚀 Starting API Gateway...")
    logger.info(f"📍 Gateway running on {settings.GATEWAY_HOST}:{settings.GATEWAY_PORT}")
    logger.info("📡 Service URLs:")
    for service, url in settings.SERVICE_MAP.items():
        logger.info(f"   - {service}: {url}")
    logger.info("🔓 Public routes:")
    logger.info("   - /api/users/register")
    logger.info("   - /api/users/login")
    logger.info("   - /health")
    logger.info("   - /docs")

@app.get("/")
async def root():
    """Root endpoint - Public"""
    return {
        "service": "API Gateway",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "all_health": "/api/health/all",
            "services": "/api/services",
            "docs": "/docs",
            "register": "/api/users/register",
            "login": "/api/users/login"
        }
    }

@app.get("/health")
async def health_check():
    """Gateway health check - Public"""
    return {
        "status": "healthy",
        "service": "api_gateway",
        "version": "1.0.0"
    }

# ✅ Enhanced exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"⚠️ HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"❌ Unhandled exception: {exc}")
    logger.error(f"📍 Traceback: {traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc),
            "type": type(exc).__name__
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.GATEWAY_HOST, port=settings.GATEWAY_PORT)