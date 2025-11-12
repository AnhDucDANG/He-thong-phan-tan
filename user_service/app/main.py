from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from datetime import datetime

from .core.config import settings
from .database.connection import connect_db, close_db, get_database, get_client
from .routes import user_routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    logger.info("🚀 Starting User Service...")
    await connect_db()
    logger.info("✅ Connected to MongoDB")
    yield
    logger.info("👋 Shutting down User Service...")
    await close_db()
    logger.info("✅ Closed MongoDB connection")

app = FastAPI(
    title="User Service",
    description="User management microservice for Car Rental System",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user_routes.router, tags=["users"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "User Service",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint with sharding info"""
    try:
        db = get_database()
        client = get_client()
        admin_db = client.admin

        await db.command('ping')
        
        server_info = await admin_db.command('serverStatus')
        process_type = server_info.get('process', 'unknown')
        
        is_mongos = process_type == 'mongos'
        
        health_info = {
            "status": "healthy",
            "service": "user_service",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat(),
            "mongodb": {
                "connected": True,
                "process": process_type,
                "is_sharded": is_mongos,
                "database": db.name,
                "host": str(client.address) if hasattr(client, 'address') else "unknown"
            }
        }
        
        if is_mongos:
            try:
                shards_result = await admin_db.command('listShards')
                health_info["sharding"] = {
                    "enabled": True,
                    "shard_count": len(shards_result.get('shards', [])),
                    "shards": [
                        {
                            "name": shard.get('_id'),
                            "host": shard.get('host')
                        }
                        for shard in shards_result.get('shards', [])
                    ]
                }
            except Exception as e:
                logger.warning(f"Could not get sharding info: {e}")
                health_info["sharding"] = {
                    "enabled": True,
                    "error": "Could not retrieve shard list"
                }
        else:
            health_info["sharding"] = {
                "enabled": False,
                "message": "Not connected to mongos router"
            }
        
        return health_info
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "service": "user_service",
                "database": "disconnected",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )