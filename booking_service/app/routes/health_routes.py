from fastapi import APIRouter
import datetime
from app.core.config import settings
from typing import Dict, Any, Union

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

    # Logic kiểm tra kết nối DB (giữ nguyên từ code cũ)
    if check_db:
        try:
            # Lưu ý: Cần đảm bảo thư viện sqlalchemy đã được cài đặt (trong requirements.txt)
            from sqlalchemy import create_engine, text

            # Sử dụng config từ app.core.config
            engine = create_engine(settings.SQLALCHEMY_DATABASE_URL, connect_args={"timeout": 5})
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            result["database"] = "ok"
        except Exception as e:
            result["database"] = "error"
            result["db_error"] = str(e)
            result["status"] = "degraded"

    return result