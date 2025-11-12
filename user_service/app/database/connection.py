from motor.motor_asyncio import AsyncIOMotorClient
from ..core.config import settings
import logging
from pymongo.errors import ConnectionFailure

logger = logging.getLogger(__name__)

# Global MongoDB client
client: AsyncIOMotorClient = None
database = None

async def connect_db():
    """Connect to MongoDB"""
    global client, database
    
    try:
        logger.info(f"Connecting to MongoDB: {settings.MONGO_URL}")
        
        client = AsyncIOMotorClient(
            settings.MONGO_URL,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=5000
        )
        
        await client.admin.command('ping')
        
        database = client[settings.MONGO_DB]
        
        logger.info(f"✅ Connected to MongoDB database: {settings.MONGO_DB}")
        
        # Check if connected to mongos
        server_info = await client.admin.command('serverStatus')
        process_type = server_info.get('process', 'unknown')
        logger.info(f"📊 MongoDB process type: {process_type}")
        
        if process_type == 'mongos':
            logger.info("✅ Connected to MongoDB Sharded Cluster (mongos)")
            try:
                shards = await client.admin.command('listShards')
                logger.info(f"📦 Number of shards: {len(shards.get('shards', []))}")
            except Exception as e:
                logger.warning(f"Could not get shard info: {e}")
        else:
            logger.warning("⚠️  Not connected to mongos - sharding features may not work")
        
    except Exception as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")
        raise

async def close_db():
    """Close MongoDB connection"""
    global client
    if client:
        client.close()
        logger.info("✅ MongoDB connection closed")

def get_database():
    """Get database instance"""
    if database is None:
        raise Exception("Database not initialized. Call connect_db() first.")
    return database

def get_client():
    """Get MongoDB client instance"""
    if client is None:
        raise Exception("MongoDB client not initialized. Call connect_db() first.")
    return client

def check_connection() -> bool:
    """Check if MongoDB connection is alive"""
    try:
        db = get_database()
        db.command('ping')
        logger.info("✅ MongoDB connection successful")
        return True
    except ConnectionFailure as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        return False

def get_users_collection():
    """Get users collection (will be sharded)"""
    db = get_database()
    return db.users

def get_sharding_status():
    """Get sharding status for debugging"""
    try:
        db = get_database()
        admin_db = client.admin
        status = admin_db.command('serverStatus')
        
        # Check if this is a mongos
        is_mongos = status.get('process') == 'mongos'
        
        if is_mongos:
            shard_status = admin_db.command('listShards')
            return {
                "is_sharded": True,
                "process": "mongos",
                "shards": shard_status.get('shards', [])
            }
        else:
            return {
                "is_sharded": False,
                "process": status.get('process'),
                "message": "Connected to standalone MongoDB"
            }
    except Exception as e:
        logger.error(f"Error getting sharding status: {e}")
        return {
            "is_sharded": False,
            "error": str(e)
        }