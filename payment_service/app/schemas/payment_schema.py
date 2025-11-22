from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PaymentCreate(BaseModel):
    booking_id: str = Field(..., description="Booking ID liên quan")
    user_id: str = Field(..., description="User ID thực hiện payment")
    amount: int = Field(..., gt=0, description="Số tiền (VND)")
    payment_method: Optional[str] = Field("vnpay", description="Phương thức thanh toán - chỉ vnpay hiện tại")


class PaymentUpdate(BaseModel):
    payment_status: Optional[str] = Field(None, description="pending | completed | failed")
    gateway_transaction_id: Optional[str] = None


class PaymentOut(BaseModel):
    id: str
    booking_id: str
    user_id: str
    amount: int
    payment_method: str
    payment_status: str
    gateway_transaction_id: Optional[str]
    created_at: datetime
    updated_at: datetime
