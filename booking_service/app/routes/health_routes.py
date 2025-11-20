from fastapi import APIRouter
import datetime
from app.core.config import settings
from typing import Dict, Any, Union
from motor.motor_asyncio import AsyncIOMotorClient 
import asyncio

router = APIRouter()

@router.get("/health", tags=["health"], response_model=Dict[str, Any])
async def health(check_db: bool = False) -> Dict[str, Union[str, bool, Dict]]:
    """
    Health check cơ bản.
    - check_db=True => thử kết nối tới database (nếu SQLALCHEMY_DATABASE_URL hợp lệ).
    """
    result = {
        "service": "booking",
        "status": "ok",
        "time": datetime.datetime.utcnow().isoformat() + "Z",
    }

    if check_db:
        client = None
        
        try:
            # Khởi tạo Async Motor Client từ MONGO_URL
            client = AsyncIOMotorClient(
                settings.MONGO_URL, 
                serverSelectionTimeoutMS=5000 # 5 giây timeout
            )
            
            # Thực hiện lệnh ping (kiểm tra server có phản hồi không)
            # await là bắt buộc khi dùng Motor
            await client.admin.command('ping')
            
            result["database"] = "ok"

        except Exception as e:
            result["database"] = "error"
            result["db_error"] = str(e)
            result["status"] = "degraded"
        
        finally:
            if client:
                 client.close()

    return result