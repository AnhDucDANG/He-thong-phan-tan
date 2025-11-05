from pymongo import MongoClient
import os
import logging

logger = logging.getLogger(__name__)

# Đọc từ environment variables
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB", "rental_user_db")

# Tạo MongoDB client
client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
db = client[DB_NAME]

def check_connection() -> bool:
    """Kiểm tra kết nối MongoDB"""
    try:
        client.admin.command("ping")
        logger.info(f"✅ Connected to MongoDB at {MONGO_URL}")
        return True
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        return False