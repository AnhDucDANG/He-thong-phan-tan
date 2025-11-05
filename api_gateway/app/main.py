from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import logging
from .core.config import settings
from .routes import gateway_routes, proxy_routes

# Logging
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

# CORS - Cho phép tất cả origins để team có thể access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ✅ Cho phép tất cả
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
            "docs": "/docs"
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

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.GATEWAY_HOST, port=settings.GATEWAY_PORT)