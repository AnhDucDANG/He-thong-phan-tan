import httpx
from app.core.config import settings
from app.routes.http_client import get_request, post_request
from fastapi import HTTPException
from datetime import date, datetime
from typing import Dict, Any

CAR_SERVICE_URL = settings.VEHICLE_SERVICE_URL

async def check_car_availability(car_id: str, start_date: date, end_date: date) -> Dict[str, Any]:
    """
    Gọi Car Service để kiểm tra tính sẵn có và lấy thông tin chi tiết (giá).
    """
    endpoint = f"/api/vehicles/{car_id}" 
    
    # Chuyển đổi date thành string ISO 8601
    params = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }

    try:
        # Sử dụng GET Request
        response_data = await get_request(CAR_SERVICE_URL, endpoint, params=params)
        
        if not response_data.get("isDeleted", False):
            raise HTTPException(status_code=404, detail="Xe không có sẵn trong khoảng thời gian này.")
            
        return response_data # Bao gồm giá thuê, thông tin xe...
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Không tìm thấy thông tin xe.")
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Không thể kết nối Car Service: {e}")


async def mark_car_as_booked(car_id: str, booking_id: str):
    """
    Gọi Car Service để đánh dấu xe là đã được đặt sau khi tạo đơn hàng thành công.
    """
    endpoint = f"/api/cars/{car_id}/mark-booked"
    data = {"booking_id": booking_id, "status": "RESERVED"}

    try:
        # Sử dụng POST Request
        await post_request(CAR_SERVICE_URL, endpoint, data)
    except Exception as e:
        # Lưu ý: Nếu bước này thất bại, cần có logic Rollback/Saga (topic nâng cao)
        print(f"WARNING: Failed to mark car {car_id} as booked on Car Service: {e}")
        # Tạm thời chỉ log lỗi, không ném lỗi 500 để Transaction Booking không bị Rollback
        pass