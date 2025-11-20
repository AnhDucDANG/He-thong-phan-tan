from beanie import PydanticObjectId
from app.models.booking_model import Booking  # Beanie Document
from app.schemas.booking_schema import BookingCreate  # Pydantic Schema
from datetime import datetime
from fastapi import HTTPException
import logging
from typing import Optional

logger = logging.getLogger(__name__)

async def create_booking_transaction(booking_data: BookingCreate, book_price: float) -> Optional[Booking]:
    """
    Tạo đơn đặt xe mới với kiểm tra trùng lặp lịch xe bất đồng bộ.
    """
    logger.info("=== DEBUG BOOKING REQUEST START ===")
    logger.info(f"user_id raw       → {booking_data.user_id} | type: {type(booking_data.user_id)}")
    logger.info(f"car_id raw        → {booking_data.car_id} | type: {type(booking_data.car_id)}")
    logger.info(f"start_date        → {booking_data.start_date}")
    logger.info(f"book_price passed → {book_price} | type: {type(book_price)}")
    logger.info("=== DEBUG BOOKING REQUEST END ====")

    try:
        # Chuyển đổi ngày tháng sang đối tượng datetime
        start_dt = datetime.fromisoformat(booking_data.start_date.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(booking_data.end_date.replace('Z', '+00:00'))

        # Xác thực user_id và car_id
        user_id = int(booking_data.user_id)
        if user_id <= 0:
            raise ValueError("user_id must be a positive integer")
        
        car_id = str(booking_data.car_id).strip()
        # Giới hạn độ dài tối đa
        if len(car_id) > 50:
            car_id = car_id[:50]
        if not car_id:
            raise ValueError("car_id cannot be empty after processing")

        # ATOMIC CHECK
        # Beanie Query Builder
        conflict = await Booking.find_one(
            Booking.car_id == car_id,
            Booking.status.in_(["PENDING_PAYMENT", "PENDING_CONFIRM", "CONFIRMED"]),
            Booking.start_date <= end_dt, 
            Booking.end_date > start_dt
        ).first_or_none()

        if conflict:
            logger.info(f"Found conflicting booking _id={conflict.id}, status={conflict.status}")
            raise HTTPException(
                status_code=409,
                detail="Concurrency conflict: The car is already reserved for this period."
            )

        # Tạo đối tượng Booking Document
        new_booking = Booking(
            user_id=user_id,
            car_id=car_id,
            start_date=start_dt,
            end_date=end_dt,
            book_price=book_price,
            status="PENDING_PAYMENT"
            # created_at sẽ tự động dùng giá trị mặc định (datetime.utcnow())
        )
        
        # Insert bất đồng bộ (atomic operation)
        result = await new_booking.insert()
        
        logger.info(f"Booking created and committed: {new_booking.id}")
        return new_booking

    except ValueError as ve:
        logger.error(f"Validation failed: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException:
        # Re-raise HTTPException (409 conflict)
        raise
    except Exception as e:
        logger.error(f"Transaction failed: {e}")
        # Trả về lỗi 500 nếu có lỗi không mong muốn khác
        raise HTTPException(status_code=500, detail="Internal Server Error during booking creation.")
