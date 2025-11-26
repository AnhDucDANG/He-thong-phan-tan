import httpx
from app.core.config import settings
from app.routes.http_client import get_request
from fastapi import HTTPException
from typing import Dict, Any


async def verify_user_license(user_id: str) -> bool:
    """
    Gọi User Service để xác thực giấy phép lái xe của người dùng.
    """
    if not user_id or user_id.strip() == "":
        raise HTTPException(status_code=400, detail="User ID is required")
    
    user_service_url = settings.USER_SERVICE_URL
    endpoint = f"/users/{user_id}/verify"

    try:
        # Sử dụng GET Request
        response_data = await get_request(user_service_url, endpoint)

        role = response_data.get("role")
        is_valid = response_data.get("is_valid", False)
        
        if not is_valid or role != "customer": # Thêm điều kiện kiểm tra role
            raise HTTPException(status_code=403, detail=f"User ID: {user_id} không hợp lệ, không phải Customer.")
            
        return is_valid

    except httpx.HTTPStatusError as e:
        # Nếu User Service trả về 404 (User không tồn tại) hoặc 403
        if e.response.status_code in (404, 403):
             raise HTTPException(status_code=403, detail=f"User Service: {e.response.json().get('detail', 'Xác thực người dùng thất bại.')}")
        raise # Ném lỗi khác
    except Exception as e:
        # Lỗi kết nối (timeout, service down)
        raise HTTPException(status_code=503, detail=f"Không thể kết nối User Service: {e}")