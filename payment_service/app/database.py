from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import asyncio

from app.models.payment import Payment, Transaction
from app.config import settings

class Database:
    client: AsyncIOMotorClient = None
    database = None

db = Database()

async def init_db():
    try:
        print(f"🔗 Connecting to MongoDB: {settings.MONGO_URL}")
        
        # Kết nối MongoDB
        db.client = AsyncIOMotorClient(
            settings.MONGO_URL,
            serverSelectionTimeoutMS=5000
        )
        
        # Test connection
        await db.client.admin.command('ping')
        print("✅ MongoDB connected successfully")
        
        # Init Beanie
        await init_beanie(
            database=db.client[settings.MONGO_DB],
            document_models=[Payment, Transaction]
        )
        print("✅ Beanie initialized successfully")
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        raise e

async def close_db():
    if db.client:
        db.client.close()