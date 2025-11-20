from app.schemas.booking_schema import BookingCreate
from fastapi import HTTPException
from datetime import datetime, timedelta
from app.models.booking_model import Booking

async def save_booking(booking_data: BookingCreate, payment_status: str, total_amount: float):
    # Tính số ngày thuê (làm tròn lên nếu có giờ lẻ)
    delta: timedelta = booking_data.end_date - booking_data.start_date
    if delta <= timedelta(0):
        raise HTTPException(status_code=400, detail="end_date must be after start_date")

    # Tổng số ngày = làm tròn lên (ví dụ: 3 ngày 1 tiếng → tính 4 ngày)
    total_days = delta.days + 1  # phổ biến nhất trong ngành cho thuê xe

    # daily_rate sau này có thể lấy từ Vehicle Service
    if total_days <= 0:
        daily_rate = float(total_amount)
    else:
        daily_rate = round(total_amount / total_days, 2)

    booking = Booking(
        user_id=booking_data.user_id,
        car_id=booking_data.car_id,
        start_date=booking_data.start_date,
        end_date=booking_data.end_date,
        book_price=total_amount,          
        daily_rate=daily_rate,             
        total_days=total_days,             
        status=payment_status.upper(),      
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    await booking.insert()
    return booking