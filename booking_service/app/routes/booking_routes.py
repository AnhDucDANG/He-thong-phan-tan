from fastapi import APIRouter, Depends, HTTPException
import datetime
from ..schemas.booking_schema import BookingCreate, BookingResponse
from app.core.config import settings

router = APIRouter()

#Api tạo đơn hàng
@router.post("/bookings", response_model=BookingResponse, status_code=201)
def create_booking(booking_data: BookingCreate):
    # b1: gọi User service
    # user_verified = user_service.verify_license(booking_data.user_id)
    # if not user_verified:
    #     raise HTTPException(status_code=403, detail="User license not valid")
    
    # b2: gọi Car Service
    # car_available = car_service.check_availability(booking_data.car_id, booking_data.start_date, booking_data.end_date)
    # if not car_available:
    #     raise HTTPException(status_code=404, detail="Car not available")

    # b3: tính bill
    # total_amount = calculate_price(booking_data.car_id, booking_data.start_date, booking_data.end_date)
    
    # b4: gọi Payment service
    # payment_status = payment_service.process_payment(total_amount)
    
    # b5: lưu vào DB
    # booking_id = database.save_booking(booking_data, payment_status)
    # car_service.mark_car_as_booked(booking_data.car_id, booking_id)
    
    return {"booking_id": "MOCK-BKG-001", "status": "CONFIRMED"}

#Api xem Booking
@router.get("/bookings/{id}", response_model=BookingResponse)
def get_booking_details(id: str):
    return {"booking_id": id, "status": "CONFIRMED"}

#Api hủy Booking
@router.post("/bookings/{id}/cancel")
def cancel_booking(id: str):
    # Gọi Car Service để giải phóng xe
    # car_service.release_car(id)
    return {"message": f"Booking {id} cancelled successfully"}

@router.get("/health", tags=["health"])
async def health(check_db: bool = False):
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
        try:
            from sqlalchemy import create_engine, text

            engine = create_engine(settings.SQLALCHEMY_DATABASE_URL, connect_args={"timeout": 5})
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            result["database"] = "ok"
        except Exception as e:
            result["database"] = "error"
            result["db_error"] = str(e)
            result["status"] = "degraded"

    return result