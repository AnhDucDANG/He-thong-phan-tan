from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings
from app.models.payment_model import Payment
from typing import Optional

client: Optional[AsyncIOMotorClient] = None
db = None

async def init_db():
    global client, db
    mongo_url = settings.get_mongo_url()
    client = AsyncIOMotorClient(mongo_url)
    # If using a standalone Mongo (non-Atlas) you might want to use:
    # db = client[settings.MONGO_DB]
    db = client.get_default_database()
    await init_beanie(database=db, document_models=[Payment])
    print("✅ Connected to MongoDB")

async def close_db():
    global client
    if client:
        client.close()
        print("✅ MongoDB connection closed")
