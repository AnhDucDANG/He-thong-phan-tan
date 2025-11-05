from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
from .routes import user_routes
from .database.connection import check_connection

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="User Service",
    description="Microservice for user management and authentication",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(user_routes.router, prefix="/users", tags=["Users"])

@app.on_event("startup")
async def startup_event():
    """Check database connection on startup"""
    logger.info("🚀 Starting User Service...")
    if check_connection():
        logger.info("✅ MongoDB connected successfully")
    else:
        logger.error("❌ MongoDB connection failed")

@app.get("/")
def root():
    return {
        "service": "User Service",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    try:
        db_status = "healthy" if check_connection() else "unhealthy"
        
        return {
            "status": "healthy" if db_status == "healthy" else "unhealthy",
            "service": "user_service",
            "database": db_status,
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "service": "user_service",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)