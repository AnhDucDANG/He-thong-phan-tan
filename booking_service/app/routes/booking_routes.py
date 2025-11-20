from fastapi import APIRouter, Depends, HTTPException
from ..schemas.booking_schema import BookingCreate, BookingResponse
from ..services.booking_service import save_booking

router = APIRouter(prefix="/bookings", tags=["bookings"])

# Api tạo đơn đặt xe
@router.post("/", response_model=BookingResponse, status_code=201)
async def create_booking(booking_data: BookingCreate):
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
    #try:
    #    booking_data.user_id = int(booking_data.user_id)
    #except (ValueError, TypeError):
    #    raise HTTPException(
    #        status_code=400,
    #        detail="user_id must be a valid integer"
    #   )

    total_amount = 2500000 
    payment_status = "CONFIRMED"

    # b5: lưu vào DB
    # booking_id = database.save_booking(booking_data, payment_status)
    # car_service.mark_car_as_booked(booking_data.car_id, booking_id)
    try:
        db_booking = await save_booking(booking_data, payment_status, total_amount)
        
    except ValueError as e:
        # Lỗi validation (user_id, car_id không hợp lệ)
        raise HTTPException(status_code=400, detail=f"Validation Error: {str(e)}")
    
    except Exception as e:
        # Lỗi xung đột dữ liệu (Concurrency conflict) hoặc lỗi CSDL
        error_msg = str(e).lower()
        if "already reserved" in error_msg or "concurrency" in error_msg:
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
    return BookingResponse(
        id=str(db_booking.id),
        user_id=db_booking.user_id,
        car_id=db_booking.car_id,
        start_date=db_booking.start_date,
        end_date=db_booking.end_date,
        book_price=db_booking.book_price,
        daily_rate=db_booking.daily_rate,         
        total_days=db_booking.total_days,         
        status=db_booking.status.lower(),
        created_at=db_booking.created_at,
        updated_at=db_booking.updated_at,
    )

# Api xem Booking
@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking_details(booking_id: str):
    # TODO: implement thật sau
    return {"id": booking_id, "status": "CONFIRMED"}

# Api hủy Booking
@router.post("/{booking_id}/cancel")
async def cancel_booking(booking_id: str):
    # TODO: implement thật sau
    return {"message": f"Booking {booking_id} cancelled successfully"}