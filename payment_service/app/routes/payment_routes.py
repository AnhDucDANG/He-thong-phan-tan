from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.payment_model import Payment
from pydantic import BaseModel
from typing import List, Optional
import urllib.parse
import hashlib
import hmac

import os

# Lấy thông tin VNPay từ biến môi trường
M49B55TZ = os.getenv("M49B55TZ", "TEST1234")        # mã merchant sandbox
VNPAY_HASH_SECRET = os.getenv("1CDCMQ2WCGLIBX9KLZUFDLIG68Z51G7Z", "SECRET_KEY") # secret sandbox
VNPAY_URL = os.getenv("VNPAY_URL", "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html")
VNPAY_RETURN_URL = os.getenv("VNPAY_RETURN_URL", "http://localhost:3000/payment-return")

router = APIRouter(
    prefix="/payments",
    tags=["payments"]
)

# -------------------- Schemas --------------------
class PaymentCreate(BaseModel):
    user_id: int
    booking_id: int
    amount: float

class PaymentResponse(BaseModel):
    id: int
    user_id: int
    booking_id: int
    amount: float
    status: str
    payment_method: str
    transaction_id: Optional[str]

    class Config:
        orm_mode = True

class VNPayLinkResponse(BaseModel):
    payment_id: int
    vnpay_url: str

class VNPayCallbackRequest(BaseModel):
    # Tất cả param VNPay gửi callback
    vnp_TxnRef: str
    vnp_TransactionNo: str
    vnp_ResponseCode: str
    vnp_Amount: int
    vnp_SecureHash: str

# -------------------- Routes --------------------

@router.post("/", response_model=PaymentResponse)
def create_payment(payment: PaymentCreate, db: Session = Depends(get_db)):
    db_payment = Payment(
        user_id=payment.user_id,
        booking_id=payment.booking_id,
        amount=payment.amount,
        status="pending"  # payment_method mặc định VNPay
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

@router.post("/{payment_id}/vnpay-link", response_model=VNPayLinkResponse)
def create_vnpay_link(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    # Tham số VNPay
    vnp_params = {
        "vnp_Version": "2.1.0",
        "vnp_Command": "pay",
        "vnp_TmnCode": VNPAY_TMN_CODE,
        "vnp_Amount": int(payment.amount * 100),  # VNPay nhân 100
        "vnp_CurrCode": "VND",
        "vnp_TxnRef": str(payment.id),
        "vnp_OrderInfo": f"Thanh toán booking {payment.booking_id}",
        "vnp_Locale": "vn",
        "vnp_ReturnUrl": VNPAY_RETURN_URL,
    }

    # Tạo query string sắp xếp theo key
    query_string = "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in sorted(vnp_params.items()))
    # Tạo secure hash
    vnp_secure_hash = hmac.new(VNPAY_HASH_SECRET.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    vnp_params["vnp_SecureHash"] = vnp_secure_hash

    vnpay_url = f"{VNPAY_URL}?{urllib.parse.urlencode(vnp_params)}"
    return VNPayLinkResponse(payment_id=payment.id, vnpay_url=vnpay_url)

@router.post("/vnpay-callback")
async def vnpay_callback(request: Request, db: Session = Depends(get_db)):
    """
    Nhận callback từ VNPay sau khi user thanh toán
    """
    params = dict(request.query_params)
    payment_id = int(params.get("vnp_TxnRef"))
    secure_hash = params.get("vnp_SecureHash")

    # Xác thực hash
    query_params = {k: v for k, v in params.items() if k != "vnp_SecureHash"}
    query_string = "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in sorted(query_params.items()))
    expected_hash = hmac.new(VNPAY_HASH_SECRET.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    if secure_hash != expected_hash:
        raise HTTPException(status_code=400, detail="Invalid secure hash")

    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    # Cập nhật trạng thái theo response code
    response_code = params.get("vnp_ResponseCode")
    transaction_no = params.get("vnp_TransactionNo")
    if response_code == "00":
        payment.status = "completed"
    else:
        payment.status = "failed"

    payment.transaction_id = transaction_no
    db.commit()
    db.refresh(payment)

    return {"message": "Payment status updated", "payment_id": payment.id, "status": payment.status}
