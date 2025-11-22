from beanie import Document
from datetime import datetime
from typing import Optional
from pydantic import Field


class Payment(Document):
    booking_id: str
    user_id: str
    amount: int
    payment_method: str = "vnpay"  # only vnpay supported in requirements
    payment_status: str = "pending"  # pending | completed | failed
    gateway_transaction_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "payments"

    def update_timestamp(self):
        self.updated_at = datetime.utcnow()
