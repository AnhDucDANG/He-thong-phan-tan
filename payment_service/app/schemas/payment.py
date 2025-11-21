from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from app.models.payment import PaymentStatus, PaymentMethod

class PaymentCreate(BaseModel):
    booking_id: str = Field(..., description="ID của booking")
    user_id: str = Field(..., description="ID của user")
    amount: float = Field(..., gt=0, description="Số tiền thanh toán")
    currency: str = Field(default="VND", description="Loại tiền tệ")
    payment_method: PaymentMethod = Field(default=PaymentMethod.VNPAY, description="Phương thức thanh toán")

class PaymentResponse(BaseModel):
    id: str
    booking_id: str
    user_id: str
    amount: float
    currency: str
    payment_method: PaymentMethod
    status: PaymentStatus
    vnpay_payment_url: Optional[str] = None
    vnpay_transaction_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PaymentUpdate(BaseModel):
    status: Optional[PaymentStatus] = None
    vnpay_transaction_id: Optional[str] = None
    vnpay_response_code: Optional[str] = None

class VNPayReturn(BaseModel):
    vnp_ResponseCode: str
    vnp_TxnRef: str
    vnp_TransactionNo: Optional[str] = None
    vnp_BankCode: Optional[str] = None
    vnp_CardType: Optional[str] = None
    vnp_Amount: Optional[str] = None
    vnp_SecureHash: Optional[str] = None