import httpx
from app.core.config import settings
from app.routes.http_client import post_request
from fastapi import HTTPException
from typing import Dict, Any

PAYMENT_SERVICE_URL = settings.PAYMENT_SERVICE_URL

async def process_payment(booking_id: str, book_price: float) -> str:
    """
    Gọi Payment Service để xử lý giao dịch thanh toán.
    """
    endpoint = "/api/payments"
    data = {
        "booking_id": booking_id,
        "amount": book_price,
        "currency": "VND"
    }

    try:
        # Sử dụng POST Request
        response_data = await post_request(PAYMENT_SERVICE_URL, endpoint, data)

        # Giả định Payment Service trả về object {"status": "SUCCESS/FAILURE", ...}
        payment_status = response_data.get("status", "FAILURE")
        
        if payment_status != "SUCCESS":
            # Nếu thanh toán thất bại
            raise HTTPException(status_code=400, detail="Thanh toán thất bại.")
            
        return payment_status # "SUCCESS"

    except httpx.HTTPStatusError as e:
        # Nếu Payment Service trả về 400 (Invalid Card)
        raise HTTPException(status_code=400, detail=f"Lỗi thanh toán: {e.response.json().get('detail', 'Giao dịch không hợp lệ.')}")
    except Exception as e:
        # Lỗi kết nối
        raise HTTPException(status_code=503, detail=f"Không thể kết nối Payment Service: {e}")