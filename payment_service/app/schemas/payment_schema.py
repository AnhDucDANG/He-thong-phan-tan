from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BookingCreate(BaseModel):
    user_id: int
    room_id: int
    start_date: datetime
    end_date: datetime

class BookingResponse(BaseModel):
    id: int
    user_id: int
    room_id: int
    start_date: datetime
    end_date: datetime
    created_at: datetime

class BookingUpdate(BaseModel):
    room_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None