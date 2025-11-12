CAR_MOCK_DATA = {
    "car_id": "CAR-00123",
    "model": "Toyota Vios",
    "rental_rate_per_day": 800000 
}

def get_car_details(car_id: str):
    """Giả lập lấy thông tin xe từ Car Service."""
    if car_id == "CAR-ERROR":
        # Giả lập lỗi xe không tồn tại
        return None
    return CAR_MOCK_DATA

def check_availability(car_id: str, pickup_date: str, return_date: str) -> bool:
    """Giả lập kiểm tra xe có sẵn. Luôn trả về True."""
    # Logic có thể kiểm tra car_id cụ thể để giả lập lỗi
    if car_id == "CAR-UNAVAILABLE":
        return False
    return True

def mark_car_as_booked(car_id: str, booking_id: str) -> bool:
    """Giả lập đánh dấu xe đã được đặt. Luôn trả về True."""
    print(f"MOCK: Car {car_id} marked as BOOKED by {booking_id}")
    return True

def release_car(car_id: str, booking_id: str) -> bool:
    """Giả lập giải phóng xe khi hủy đơn. Luôn trả về True."""
    print(f"MOCK: Car {car_id} released from booking {booking_id}")
    return True