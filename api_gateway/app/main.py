from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time
from .routes import proxy_routes
from .core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API Gateway",
    description="Gateway điều phối cho hệ thống cho thuê xe phân tán",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong production nên chỉ định cụ thể
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    start_time = time.time()
    
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        f"Completed {request.method} {request.url.path} "
        f"- Status: {response.status_code} - Time: {process_time:.2f}s"
    )
    
    return response

# Include routers
app.include_router(proxy_routes.router, prefix="/api", tags=["Proxy"])

@app.get("/", tags=["Root"])
def read_root():
    """Root endpoint"""
    return {
        "service": "API Gateway",
        "status": "running",
        "version": "1.0.0",
        "services": list(settings.SERVICE_MAP.keys())
    }

@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "gateway": "operational",
        "services": settings.SERVICE_MAP
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "path": request.url.path
        }
    )