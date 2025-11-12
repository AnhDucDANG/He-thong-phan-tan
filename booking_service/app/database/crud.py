from sqlalchemy.orm import Session
from sqlalchemy import text
from booking_service.models import Booking
from booking_service.schemas import BookingCreate 
from datetime import datetime
import logging

logger = logging.getLogger(__name__) 

def create_booking_transaction(db: Session, booking_data: BookingCreate):
    BOOKING_TABLE = Booking.__tablename__

    try:
        # Chuyển đổi ngày tháng sang đối tượng datetime 
        start_dt = datetime.fromisoformat(booking_data.start_date.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(booking_data.end_date.replace('Z', '+00:00'))
        
        # UPDLOCK: Giữ khóa cập nhật (Update Lock) cho các hàng được chọn, ngăn các giao dịch khác sửa đổi
        # HOLDLOCK: Giữ khóa cho đến khi Transaction kết thúc
        
        sql_check = text("""
            SELECT TOP 1 id 
            FROM dbo.Booking WITH (UPDLOCK, HOLDLOCK)
            WHERE car_id = :car_id
            AND status IN ('PENDING_PAYMENT', 'CONFIRMED')
            AND start_date <= :end_date 
            AND end_date > :start_date;
        """)

        # Nếu tìm thấy bất kỳ bản ghi nào (count > 0), có nghĩa là đã có một đơn hàng trùng lặp
        result = db.execute(
            sql_check, 
            {
                "car_id": booking_data.car_id, 
                "start_date": start_dt, 
                "end_date": end_dt
            }
        ).fetchone()

        if result:
            # Nếu tìm thấy, ném ra lỗi để Transaction tự động Rollback
            raise Exception("Concurrency conflict: The car is already reserved for this period.")

        # TẠO BOOKING        
        db_booking = Booking(
            user_id=booking_data.user_id,
            car_id=booking_data.car_id,
            start_date=start_dt,
            end_date=end_dt,
            book_price=booking_data.estimated_price,
            status="PENDING_PAYMENT"
        )
        
        db.add(db_booking)
        
        # Commit Transaction (Lưu thay đổi vào CSDL)
        db.add(db_booking)
        db.flush()          # để lấy ID
        return db_booking 
        logger.info(f"Booking created and committed: {db_booking.id}")
        return db_booking

    except Exception as e:
        # Nếu có bất kỳ lỗi nào -> Transaction sẽ Rollback
        db.rollback() 
        logger.error(f"Transaction failed and rolled back: {e}")
        # raise lỗi để Router bắt và trả về HTTP 409
        raise e