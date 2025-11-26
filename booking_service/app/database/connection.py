from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings
from app.models.booking_model import Booking

client = None
db = None

async def init_db():
    global client, db
    client = AsyncIOMotorClient(settings.MONGO_URL) #client này quản lý pool kết nối, hỗ trợ sharding nếu cluster MongoDB đã config
    db = client.get_default_database()
    await init_beanie(
        database=db,
        document_models=[Booking]   #Beanie tự động tạo collection nếu chưa có, apply indexes, shard key
    )

async def close_db():
    if client:
        client.close()