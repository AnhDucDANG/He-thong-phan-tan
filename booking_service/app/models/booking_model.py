from sqlalchemy import Column, Integer, String, DateTime, Float, func, UniqueConstraint
from booking_service.database import Base   #Base đã định nghĩa ở database.py

class Booking(Base):
    __tablename__ = "Booking"

    id = Column(Integer, primary_key=True, index=True)
    
    # Liên kết với Service 3 (User)
    user_id = Column(Integer, index=True, nullable=False) 
    
    # Liên kết với Service 1 (Car)
    car_id = Column(String(50), index=True, nullable=False)
    
    # Thời gian thuê
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    
    # Giá
    book_price = Column(Float, nullable=False)
    
    # Trạng thái (chờ thanh toán, đã đặt, đã huỷ)
    status = Column(String(50), default="pending", nullable=False) 
    
    # Thời gian tạo
    created_at = Column(DateTime, default=func.now()) 
    
    # Ví dụ về ràng buộc nếu muốn đảm bảo một xe chỉ có một đơn hàng ACTIVE:
    # __table_args__ = (
    #     UniqueConstraint('car_id', name='uq_car_active'),
    # )
    pass

# Hàm tạo các bảng trong CSDL (once)
def create_tables():
    from booking_service.database import engine
    Base.metadata.create_all(bind=engine)