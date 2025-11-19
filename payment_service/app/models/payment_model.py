from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.database.connection import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)  # ID người dùng từ user_service
    booking_id = Column(Integer, nullable=False)  # ID booking từ booking_service
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="VND")
    status = Column(String(20), default="pending")  # pending, completed, failed
    payment_method = Column(String(50), default="VNPay")  # chỉ tích hợp VNPay
    transaction_id = Column(String(100), nullable=True)  # ID giao dịch từ VNPay
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
