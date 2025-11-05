from pymongo import MongoClient
import os
import logging

logger = logging.getLogger(__name__)

# Đọc từ environment variables
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB", "rental_user_db")

logger.info(f"📡 Connecting to MongoDB at: {MONGO_URL}")
logger.info(f"📊 Using database: {DB_NAME}")

try:
    # Tạo MongoDB client
    client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
    db = client[DB_NAME]
    logger.info("✅ MongoDB client created")
except Exception as e:
    logger.error(f"❌ MongoDB client creation failed: {e}")
    client = None
    db = None

def check_connection() -> bool:
    """Kiểm tra kết nối MongoDB"""
    try:
        if client is None:
            logger.error("❌ MongoDB client is None")
            return False
        client.admin.command("ping")
        logger.info("✅ MongoDB connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        return False

def get_users_collection():
    """Lấy collection users"""
    if db is None:
        logger.error("❌ Database is None")
        return None
    return db["users"]