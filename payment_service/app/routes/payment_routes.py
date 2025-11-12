from typing import Optional, List
from uuid import uuid4
from enum import Enum
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, PositiveFloat

# File: payment_service/app/routes/payment_routes.py
# Mô tả: định nghĩa các route liên quan đến thanh toán, sử dụng FastAPI
# Ghi chú: toàn bộ chú thích bằng tiếng Việt



# Khởi tạo router để có thể gắn vào ứng dụng FastAPI chính
router = APIRouter(prefix="/payments")

# Cơ sở dữ liệu tạm thời trong bộ nhớ để ví dụ (thực tế nên dùng DB)
# payments_db lưu dạng: {payment_id: PaymentOut.dict()}
payments_db = {}

# Định nghĩa trạng thái thanh toán
class PaymentStatus(str, Enum):
    pending = "pending"
    succeeded = "succeeded"
    failed = "failed"

# Mô hình dữ liệu yêu cầu tạo thanh toán
class PaymentCreate(BaseModel):
    amount: PositiveFloat = Field(..., description="Số tiền (dương)")
    currency: str = Field(..., min_length=3, max_length=3, description="Mã tiền tệ ISO 3 chữ cái, ví dụ VND, USD")
    description: Optional[str] = Field(None, description="Mô tả thanh toán")
    metadata: Optional[dict] = Field(default_factory=dict, description="Dữ liệu tùy ý lưu kèm")

# Mô hình dữ liệu trả về cho client
class PaymentOut(BaseModel):
    id: str
    amount: float
    currency: str
    description: Optional[str]
    metadata: dict
    status: PaymentStatus
    created_at: datetime

# Mô hình cập nhật trạng thái từ webhook hoặc admin
class PaymentUpdate(BaseModel):
    status: PaymentStatus

# Route: kiểm tra tình trạng dịch vụ
@router.get("/health")
def health_check():
    """
    Kiểm tra tình trạng của service.
    Trả về "ok" nếu service hoạt động.
    """
    return {"status": "ok"}

# Route: tạo mới một thanh toán
@router.post("/", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
def create_payment(payload: PaymentCreate):
    """
    Tạo một payment mới.
    - Sinh id mới
    - Lưu vào bộ nhớ tạm
    - Trả về đối tượng payment
    """
    payment_id = str(uuid4())
    now = datetime.utcnow()
    payment = PaymentOut(
        id=payment_id,
        amount=payload.amount,
        currency=payload.currency.upper(),
        description=payload.description,
        metadata=payload.metadata or {},
        status=PaymentStatus.pending,
        created_at=now,
    )
    payments_db[payment_id] = payment.dict()
    return payment

# Route: lấy chi tiết một payment theo id
@router.get("/{payment_id}", response_model=PaymentOut)
def get_payment(payment_id: str):
    """
    Lấy chi tiết payment theo payment_id.
    Nếu không tìm thấy sẽ trả về 404.
    """
    record = payments_db.get(payment_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment không tồn tại")
    return record

# Route: danh sách payment (phân trang đơn giản)
@router.get("/", response_model=List[PaymentOut])
def list_payments(limit: int = 50, offset: int = 0):
    """
    Lấy danh sách các payment.
    - limit: số bản ghi tối đa trả về
    - offset: bỏ qua N bản ghi đầu
    Lưu ý: Ví dụ này lấy từ bộ nhớ, không phù hợp cho production.
    """
    all_payments = list(payments_db.values())
    # Sắp theo thời gian tạo giảm dần
    all_payments.sort(key=lambda p: p["created_at"], reverse=True)
    sliced = all_payments[offset : offset + limit]
    return sliced

# Route: cập nhật trạng thái (ví dụ webhook từ cổng thanh toán)
@router.post("/{payment_id}/status", response_model=PaymentOut)
def update_payment_status(payment_id: str, update: PaymentUpdate):
    """
    Cập nhật trạng thái của payment.
    Thường được gọi bởi webhook của bên thứ ba hoặc admin.
    """
    record = payments_db.get(payment_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment không tồn tại")
    # Cập nhật trạng thái và lưu lại
    record["status"] = update.status
    payments_db[payment_id] = record
    return record

# Route: xóa payment (chỉ ví dụ, thực tế cân nhắc soft-delete)
@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment(payment_id: str):
    """
    Xóa payment theo id.
    Trả về 204 khi xóa thành công, 404 nếu không tồn tại.
    """
    if payment_id not in payments_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment không tồn tại")
    del payments_db[payment_id]
    return None