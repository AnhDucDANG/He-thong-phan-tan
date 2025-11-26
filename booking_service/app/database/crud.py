from beanie import PydanticObjectId
from app.models.booking_model import Booking  # Beanie Document
from app.schemas.booking_schema import BookingCreate  # Pydantic Schema
from datetime import datetime
from fastapi import HTTPException
import logging
from typing import Optional
from pymongo.errors import DuplicateKeyError

logger = logging.getLogger(__name__)

async def create_booking_transaction(
        booking_data: BookingCreate,
        daily_rate:float,
        total_days: int,
        book_price: float
    ) -> Booking:
    """
    Tạo đơn đặt xe mới với kiểm tra trùng lặp lịch đặt xe bằng unique index
    """
    logger.info("=== CREATE BOOKING TRANSACTION START ===")
    logger.info(f"Car: {booking_data.car_id} | Location: {booking_data.pickup_location}")
    logger.info(f"From: {booking_data.start_date} → To: {booking_data.end_date}")

    try:
        # Chuyển đổi ngày tháng sang đối tượng datetime
        start_dt = datetime.fromisoformat(booking_data.start_date.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(booking_data.end_date.replace('Z', '+00:00'))

        # Xác thực user_id và car_id
        user_id = str(booking_data.user_id)

        car_id = str(booking_data.car_id).strip()
        if not car_id:
            raise ValueError("car_id cannot be empty after processing")

        # Tạo đối tượng Booking Document
        new_booking = Booking(
            user_id=user_id,
            car_id=car_id,
            start_date=start_dt,
            end_date=end_dt,
            book_price=book_price,
            daily_rate=daily_rate,
            total_days=total_days,
            pickup_location=booking_data.pickup_location,  # (shard key)
            status="PENDING"
        )
        
        # Insert bất đồng bộ (atomic operation)
        await new_booking.insert()
        
        logger.info(f"Booking created and committed: {new_booking.id}")
        return new_booking

    except DuplicateKeyError as e:
        logger.warning(f"Conflict detected for car {booking_data.car_id} in period {start_dt} - {end_dt}")
        raise HTTPException(
            status_code=409,
            detail="Xe đã được đặt trong khoảng thời gian này. Vui lòng chọn thời gian khác."
        )
    
    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    
    except Exception as e:
        logger.error(f"Unexpected error during booking creation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Đã có lỗi xảy ra khi đặt xe.")
