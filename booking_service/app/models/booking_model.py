from beanie import Document, Indexed, PydanticObjectId
from datetime import datetime
from typing import Optional, Literal, List, Tuple
from pydantic import Field

class Booking(Document):
    # ID: Beanie tự động thêm _id: PydanticObjectId,

    user_id: str
    car_id: str
    start_date: datetime
    end_date: datetime
    book_price: float
    daily_rate: float   #đơn giá thuê theo ngày
    total_days: int

    # Điểm nhận xe sử dụng Literal (Enum-like) để giới hạn giá trị
    pickup_location: Literal["HANOI", "HOCHIMINH", "DANANG"] = Field(...)

    # Trạng thái sử dụng Literal (Enum-like) để giới hạn giá trị
    status: Literal[
        "PENDING",
        "CONFIRMED", 
        "CANCELLED", 
        "COMPLETED",
        "REJECTED"
    ] = "PENDING" 
    
    # Thời gian tạo
    created_at: datetime = datetime.utcnow() 
    updated_at: Optional[datetime] = None

    # --- Cấu hình Beanie Document ---
    class Settings:
        # Tên bảng trong db
        name = "bookings"
        
        # Định nghĩa các index phức tạp (Compound Indexes) để tối ưu truy vấn
        # Định dạng: List[Tuple[Tuple[field_name, direction], ...], ...]
        indexes = [
            # Index 1: Hỗ trợ query nhanh các booking theo xe và trạng thái
            # e.g., Booking.find({'car_id': 'X', 'status': 'CONFIRMED'})
            [("pickup_location", 1), ("car_id", 1), ("status", 1)],
            
            # Index 2: Hỗ trợ query kiểm tra trùng lặp lịch (Booking Overlap Check)
            [
                ("pickup_location", 1),
                ("car_id", 1),
                ("start_date", 1),
                ("end_date", 1),
                # Nên bao gồm status để loại bỏ các booking đã CANCELLED khỏi việc kiểm tra
                ("status", 1),
            ],
            
            # Index 3: Index để tìm kiếm nhanh theo user_id
            [("pickup_location", 1), ("user_id", 1)] 
        ]
        
        use_shard_key = True
        #shard_keys = [{"pickup_location": 1}]
        shard_keys = [{"pickup_location": "hashed"}]

        # Tuỳ chọn: Tăng tốc độ parsing Pydantic
        keep_union_tag = True