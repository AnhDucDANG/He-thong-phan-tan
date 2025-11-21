from beanie import Document
from pydantic import Field
from typing import Optional, Literal
from datetime import datetime
from enum import Enum

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"

class PaymentMethod(str, Enum):
    VNPAY = "vnpay"

class Payment(Document):
    booking_id: str = Field(..., description="ID của booking")
    user_id: str = Field(..., description="ID của user")
    amount: float = Field(..., gt=0, description="Số tiền thanh toán")
    currency: str = Field(default="VND", description="Loại tiền tệ")
    payment_method: PaymentMethod = Field(default=PaymentMethod.VNPAY, description="Phương thức thanh toán")
    status: PaymentStatus = Field(default=PaymentStatus.PENDING, description="Trạng thái thanh toán")
    
    # VNPay fields
    vnpay_transaction_id: Optional[str] = Field(None, description="Mã giao dịch VNPay")
    vnpay_response_code: Optional[str] = Field(None, description="Mã phản hồi VNPay")
    vnpay_bank_code: Optional[str] = Field(None, description="Mã ngân hàng")
    vnpay_card_type: Optional[str] = Field(None, description="Loại thẻ")
    vnpay_payment_url: Optional[str] = Field(None, description="URL thanh toán VNPay")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "payments"

class Transaction(Document):
    payment_id: str = Field(..., description="ID của payment")
    amount: float = Field(..., description="Số tiền giao dịch")
    transaction_type: Literal["payment", "refund"] = Field(..., description="Loại giao dịch")
    vnpay_transaction_id: Optional[str] = Field(None, description="Mã giao dịch VNPay")
    status: PaymentStatus = Field(..., description="Trạng thái giao dịch")
    metadata: Optional[dict] = Field(None, description="Thông tin bổ sung")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "transactions"