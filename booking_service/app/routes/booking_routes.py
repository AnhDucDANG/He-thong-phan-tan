from fastapi import APIRouter, Depends, HTTPException, status
from ..schemas.booking_schema import BookingCreate, BookingResponse
from app.database.crud import create_booking_transaction
from beanie import PydanticObjectId
from app.models.booking_model import Booking
from ..services import user_service, car_service, payment_service
#dependency nếu cần

router = APIRouter(prefix="/bookings", tags=["bookings"])

# Api tạo đơn đặt xe
@router.post("/", response_model=BookingResponse, status_code=201)
async def create_booking(booking_data: BookingCreate):

    # b1: gọi User service verify blx của khách
    await user_service.verify_user_license(int(booking_data.user_id))
    
    # b2: gọi Car Service check xe available và lấy đơn giá
    car_info = await car_service.check_car_availability(
        booking_data.car_id,
        booking_data.start_date.date(),
        booking_data.end_date.date()
    )
    daily_rate = float(car_info.get("daily_rate", 0))

    # b3: tính bill
    delta = booking_data.end_date - booking_data.start_date
    total_days = delta.days + 1
    total_amount = daily_rate * total_days
    
    # b4: gọi Payment service
    # payment_status = await payment_service.process_payment("booking_id thật", total_amount)
    payment_status = "CONFIRMED"

    # b5: lưu vào DB
    try:
        db_booking = await create_booking_transaction(booking_data, total_amount)

    except ValueError as e:
        # Lỗi validation (user_id, car_id không hợp lệ)
        raise HTTPException(status_code=400, detail=f"Validation Error: {str(e)}")
    
    except Exception as e:
        # Lỗi xung đột dữ liệu (Concurrency conflict) hoặc lỗi CSDL
        error_msg = str(e).lower()
        if "already reserved" in error_msg or "concurrency" in error_msg:
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")

    # b6: đánh dấu xe đã đặt (fire-and-forget)
    import asyncio
    asyncio.create_task(car_service.mark_car_as_booked(booking_data.car_id, str(db_booking.id)))
    
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
@router.get("/{booking_id}", response_model=BookingResponse, status_code=200)
async def get_booking_details(booking_id: str):
    """
    Lấy chi tiết một booking theo ID
    """
    try:
        # Chuyển string → ObjectId rồi tìm trong DB
        booking = await Booking.get(PydanticObjectId(booking_id))
        
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Booking with id {booking_id} not found"
            )
        
        return booking
    
    except Exception as e:
        # Nếu booking_id không phải ObjectId hợp lệ
        if "invalid" in str(e).lower() or "objectid" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid booking ID format"
            )

# Api hủy Booking
@router.post("/{booking_id}/cancel")
async def cancel_booking(booking_id: str):
    # TODO: implement thật sau
    return {"message": f"Booking {booking_id} cancelled successfully"}