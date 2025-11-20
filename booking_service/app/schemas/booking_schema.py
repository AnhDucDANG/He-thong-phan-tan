from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional, Literal
from datetime import datetime, date, timedelta

# Trạng thái đặt xe
BookingStatus = Literal[
    "pending",
    "confirmed",   
    "cancelled",   
    "completed",   
    "rejected"     
]


class BookingBase(BaseModel):
    """Base schema containing common fields for creating/updating a booking."""
    
    user_id: int = Field(..., description="ID of the customer making the booking (from User Service).")
    
    car_id: str = Field(..., description="ID of the car being booked (from Car/Inventory Service).")
    
    start_date: datetime
    end_date: datetime
    
    # Ghi chú tùy chọn
    notes: Optional[str] = Field(None, max_length=500)

    @validator('end_date')
    def end_must_be_after_start(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('End date/time must be strictly after start date/time.')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 101,
                "car_id": "CAR-ABC-123",
                "pickup_location": "Sân bay Tân Sơn Nhất",
                "return_location": "Quận 1, TP.HCM",
                "start_date": "2025-12-01T10:00:00",
                "end_date": "2025-12-05T10:00:00",
                "notes": "Yêu cầu xe có GPS"
            }
        }


# INPUT SCHEMAS (Client -> API)
class BookingCreate(BookingBase):
    """Schema for creating a new booking."""
    # status mặc định là 'pending'
    status: Literal["pending"] = "pending"   


class BookingUpdate(BaseModel):
    """Schema for updating details of an existing booking (used by customer/admin)."""
    
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=500)


class BookingStatusUpdate(BaseModel):
    """Schema for updating the status of a booking (used by Admin/System)."""
    status: BookingStatus = Field(..., description="New status for the booking.")


# OUTPUT SCHEMAS (API -> Client)
class BookingResponse(BookingBase):
    """Schema for the booking object returned by the API."""
    
    id: str = Field(..., description="MongoDB ObjectId as string")
    
    book_price: float = Field(..., description="Final calculated price of the booking.")
    
    # xếp hạng xe, số ngày thuê
    daily_rate: float = Field(..., description="Daily rental rate of the car at the time of booking.")
    total_days: int = Field(..., description="Total number of rental days.")
    
    # Trạng thái và thời gian tạo
    status: BookingStatus
    created_at: datetime
    updated_at: Optional[datetime] = None 
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "15",
                "user_id": 101,
                "car_id": "CAR-ABC-123",
                "pickup_location": "Sân bay Tân Sơn Nhất",
                "return_location": "Quận 1, TP.HCM",
                "start_date": "2025-12-01T10:00:00",
                "end_date": "2025-12-05T10:00:00",
                "daily_rate": 500.00,
                "total_days": 4,
                "book_price": 2000.00,
                "status": "confirmed",
                "created_at": "2025-11-20T15:30:00",
                "updated_at": "2025-11-20T16:00:00"
            }
        }
        populate_by_name = True