from beanie import PydanticObjectId
from ..models.booking_model import Booking
from ..schemas.booking_schema import BookingCreate
from datetime import datetime

async def create_booking_transaction(booking_data: BookingCreate, book_price: float, daily_rate: float, total_days: int) -> Booking:
    """
    Create a new booking in the database with transaction support
    """
    # user_id và car_id đã là string, không cần validate ObjectId
    
    # Create booking document
    booking = Booking(
        user_id=booking_data.user_id,
        car_id=booking_data.car_id,
        start_date=booking_data.start_date,
        end_date=booking_data.end_date,
        pickup_location=booking_data.pickup_location,
        book_price=book_price,
        daily_rate=daily_rate,
        total_days=total_days,
        status="CONFIRMED",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Save to database
    await booking.insert()
    
    return booking