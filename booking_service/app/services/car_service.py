import httpx
from app.core.config import settings
from app.routes.http_client import get_request, post_request
from fastapi import HTTPException
from datetime import date, datetime
from typing import Dict, Any

CAR_SERVICE_URL = settings.VEHICLE_SERVICE_URL

async def check_car_availability(car_id: str, start_date: date, end_date: date) -> Dict[str, Any]:
    """
    Gọi Vehicle Service để kiểm tra xe có tồn tại và lấy thông tin (giá, trạng thái).
    """
    endpoint = f"/api/vehicles/{car_id}" 
    
    # Chuyển đổi date thành string ISO 8601
    params = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }

    try:
        # Sử dụng GET Request để lấy thông tin xe
        response_data = await get_request(CAR_SERVICE_URL, endpoint)
        
        # Kiểm tra trạng thái xe (available, on_rent, maintenance, out_of_service)
        if response_data.get("status") != "available":
            raise HTTPException(status_code=400, detail=f"Xe không có sẵn. Trạng thái hiện tại: {response_data.get('status')}")
        
        # Kiểm tra xe có bị xóa không
        if response_data.get("isDeleted"):
            raise HTTPException(status_code=404, detail="Xe đã bị xóa khỏi hệ thống.")
            
        return response_data # Bao gồm dailyRate, thông tin xe...
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Không tìm thấy thông tin xe.")
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Không thể kết nối Car Service: {e}")


async def mark_car_as_booked(car_id: str, booking_id: str):
    """
    Gọi Vehicle Service để cập nhật trạng thái xe thành on_rent và lưu booking record.
    """
    endpoint = f"/api/vehicles/{car_id}"
    data = {
        "status": "on_rent",
        "bookingRecords": [{"bookingId": booking_id}]
    }

    try:
        # Sử dụng PUT Request để cập nhật vehicle
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.put(f"{CAR_SERVICE_URL}{endpoint}", json=data)
            response.raise_for_status()
    except Exception as e:
        # Lưu ý: Nếu bước này thất bại, cần có logic Rollback/Saga (topic nâng cao)
        print(f"WARNING: Failed to mark car {car_id} as booked on Car Service: {e}")
        # Tạm thời chỉ log lỗi, không ném lỗi 500 để Transaction Booking không bị Rollback
        pass