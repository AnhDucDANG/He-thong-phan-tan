from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class PaymentBase(BaseModel):
    """Các trường cơ bản cho Payment"""
    booking_id: str
    user_id: str
    amount: float
    method: Literal["VNPAY", "MOMO", "PAYPAL", "CASH"] = "VNPAY"
    status: Literal["pending", "paid", "failed", "refunded"] = "pending"
    transaction_id: Optional[str] = None
    vn_pay_response_code: Optional[str] = None
    paid_at: Optional[datetime] = None

class PaymentCreate(PaymentBase):
    """Schema khi tạo Payment mới"""
    pass  # tất cả trường cơ bản đã đủ

class PaymentUpdate(BaseModel):
    """Schema khi cập nhật Payment"""
    status: Optional[Literal["pending", "paid", "failed", "refunded"]] = None
    transaction_id: Optional[str] = None
    vn_pay_response_code: Optional[str] = None
    paid_at: Optional[datetime] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PaymentOut(PaymentBase):
    """Schema khi trả dữ liệu Payment ra API"""
    id: Optional[str] = Field(default=None, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_deleted: bool = False

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "64fa2b1e5a6d3c001234abcd",
                "booking_id": "6789abcd1234ef567890abcd",
                "user_id": "1234abcd5678ef901234abcd",
                "amount": 1500000,
                "method": "VNPAY",
                "status": "pending",
                "transaction_id": None,
                "vn_pay_response_code": None,
                "paid_at": None,
                "created_at": "2025-11-19T19:00:00Z",
                "updated_at": "2025-11-19T19:00:00Z",
                "is_deleted": False
            }
        }