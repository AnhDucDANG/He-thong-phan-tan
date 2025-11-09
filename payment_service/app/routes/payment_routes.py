from fastapi import APIRouter, HTTPException
from app.schemas.booking_schema import BookingCreate, BookingUpdate, BookingResponse
from app.models.booking_model import Booking

router = APIRouter()

@router.post("/bookings/", response_model=BookingResponse)
async def create_booking(booking: BookingCreate):
    # Logic to create a booking
    pass

@router.get("/bookings/{booking_id}", response_model=BookingResponse)
async def get_booking(booking_id: int):
    # Logic to retrieve a booking by ID
    pass

@router.put("/bookings/{booking_id}", response_model=BookingResponse)
async def update_booking(booking_id: int, booking: BookingUpdate):
    # Logic to update a booking
    pass

@router.delete("/bookings/{booking_id}")
async def delete_booking(booking_id: int):
    # Logic to delete a booking
    pass