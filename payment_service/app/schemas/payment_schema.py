from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from typing import Optional

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PaymentMethod(str, Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    E_WALLET = "e_wallet"


class PaymentCreate(BaseModel):
    order_id: str = Field(..., min_length=1)
    amount: float = Field(..., gt=0)
    payment_method: PaymentMethod
    description: Optional[str] = None


class PaymentUpdate(BaseModel):
    status: PaymentStatus
    notes: Optional[str] = None


class PaymentResponse(BaseModel):
    id: str
    order_id: str
    amount: float
    payment_method: PaymentMethod
    status: PaymentStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True