from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings
from app.models.booking_model import Booking

client = None
db = None

async def init_db():
    global client, db
    client = AsyncIOMotorClient(settings.MONGO_URL)
    db = client.get_default_database()
    await init_beanie(
        database=db,
        document_models=[Booking]
    )

async def close_db():
    if client:
        client.close()