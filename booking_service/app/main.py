from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from contextlib import asynccontextmanager
import logging

from .core.config import settings
from .models.booking_model import Booking
from .routes import booking_routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB client
mongo_client: AsyncIOMotorClient = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    global mongo_client
    
    logger.info("🚀 Starting Booking Service...")
    logger.info(f"📊 MongoDB URL: {settings.MONGO_URL}")
    logger.info(f"📊 Database: {settings.MONGO_DB}")
    
    # Connect to MongoDB
    try:
        mongo_client = AsyncIOMotorClient(settings.MONGO_URL)
        database = mongo_client[settings.MONGO_DB]
        
        # Initialize Beanie
        await init_beanie(database=database, document_models=[Booking])
        
        logger.info("✅ Connected to MongoDB")
    except Exception as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down Booking Service...")
    if mongo_client:
        mongo_client.close()
        logger.info("✅ Closed MongoDB connection")

app = FastAPI(
    title="Booking Service",
    description="Car rental booking management microservice",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(booking_routes.router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Booking Service",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Ping MongoDB
        await mongo_client.admin.command('ping')
        
        return {
            "status": "healthy",
            "service": "booking_service",
            "database": "connected",
            "mongodb": {
                "connected": True,
                "database": settings.MONGO_DB
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "booking_service",
            "database": "disconnected",
            "error": str(e)
        }
