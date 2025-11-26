import httpx
from app.schemas.booking_schema import BookingCreate
from fastapi import HTTPException
from datetime import datetime, timedelta
from app.models.booking_model import Booking
from app.core.config import settings

VEHICLE_SERVICE_URL = settings.VEHICLE_SERVICE_URL
async def get_vehicle_daily_rate(car_id: str) -> float:
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{VEHICLE_SERVICE_URL}/api/vehicles/{car_id}")
            resp.raise_for_status()
            data = resp.json()
            return float(data["dailyRate"])
        except Exception as e:
            raise HTTPException(status_code=424, detail=f"Cannot get price from Vehicle Service: {str(e)}")

async def save_booking(booking_data: BookingCreate, payment_status: str, book_price: float):
    # Tính số ngày thuê (làm tròn lên nếu có giờ lẻ)
    delta: timedelta = booking_data.end_date - booking_data.start_date
    if delta <= timedelta(0):
        raise HTTPException(status_code=400, detail="end_date must be after start_date")

    # Tổng số ngày = làm tròn lên (ví dụ: 3 ngày 1 tiếng → tính 4 ngày)
    total_days = delta.days + (1 if delta.seconds > 0 else 0)

    # daily_rate tính tạm, sau này lấy từ Vehicle Service
    #if total_days <= 0:
    #    daily_rate = float(book_price)
    #else:
    #    daily_rate = round(book_price / total_days, 2)

    daily_rate = await get_vehicle_daily_rate(booking_data.car_id)
    delta = booking_data.end_date - booking_data.start_date
    book_price = daily_rate * total_days

    booking = Booking(
        user_id=booking_data.user_id,
        car_id=booking_data.car_id,
        start_date=booking_data.start_date,
        end_date=booking_data.end_date,
        book_price=book_price,          
        daily_rate=daily_rate,             
        total_days=total_days,             
        status=payment_status.upper(),      
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    await booking.insert()
    return booking