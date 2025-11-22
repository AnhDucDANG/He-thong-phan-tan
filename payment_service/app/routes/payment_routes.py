from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import RedirectResponse, JSONResponse
from datetime import datetime
from app.schemas.payment_schema import PaymentCreate, PaymentUpdate
from app.models.payment_model import Payment
from app.core.config import settings
import hashlib
import hmac
import urllib.parse
from typing import Dict, Any

router = APIRouter(prefix="/payments", tags=["Payments"])


# Create new payment (called after booking created)
@router.post("", summary="Create a payment record")
async def create_payment(data: PaymentCreate):
    payment = Payment(**data.dict())
    await payment.insert()
    return JSONResponse(status_code=201, content={"message": "Payment created", "payment_id": str(payment.id)})


# Get payments by user
@router.get("/user/{user_id}", summary="Get payments for a user")
async def get_user_payments(user_id: str):
    payments = await Payment.find(Payment.user_id == user_id).to_list()
    return payments


# Get all payments
@router.get("", summary="Get all payments (admin)")
async def get_all_payments():
    return await Payment.find_all().to_list()


# Get payment detail
@router.get("/{payment_id}", summary="Get payment detail")
async def get_payment_detail(payment_id: str):
    payment = await Payment.get(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


# Update payment
@router.put("/{payment_id}", summary="Update a payment")
async def update_payment(payment_id: str, data: PaymentUpdate):
    payment = await Payment.get(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    update_data = data.dict(exclude_unset=True)
    for k, v in update_data.items():
        setattr(payment, k, v)
    payment.update_timestamp()
    await payment.save()
    return payment


# Delete payment (called when booking cancelled)
@router.delete("/{payment_id}", summary="Delete a payment")
async def delete_payment(payment_id: str):
    payment = await Payment.get(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    await payment.delete()
    return {"message": "Payment deleted", "payment_id": payment_id}


# VNPay helper: build secure hash & url
def build_vnpay_url(params: Dict[str, Any]) -> str:
    sorted_items = sorted(params.items())
    hash_data = "&".join(f"{k}={v}" for k, v in sorted_items)
    secure_hash = hmac.new(
        settings.VNPAY_HASH_SECRET.encode(),
        hash_data.encode(),
        hashlib.sha512
    ).hexdigest()
    query_string = urllib.parse.urlencode(sorted_items)
    return f"{settings.VNPAY_URL}?{query_string}&vnp_SecureHash={secure_hash}"


# Create VNPay payment (returns redirect URL)
@router.post("/vnpay/create", summary="Create VNPay payment and return payment URL")
async def create_vnpay_payment(data: PaymentCreate, request: Request):
    # amount must be multiplied by 100 for VNPay
    amount = data.amount * 100

    txn_ref = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")[:-3]  # unique ref
    vnp_params = {
        "vnp_Version": "2.1.0",
        "vnp_Command": "pay",
        "vnp_TmnCode": settings.VNPAY_TMN_CODE,
        "vnp_Amount": str(amount),
        "vnp_CurrCode": "VND",
        "vnp_TxnRef": txn_ref,
        "vnp_OrderInfo": f"Payment for booking {data.booking_id}",
        "vnp_OrderType": "billpayment",
        "vnp_Locale": "vn",
        "vnp_ReturnUrl": settings.VNPAY_RETURN_URL,
        "vnp_IpAddr": request.client.host if request.client else "127.0.0.1",
        "vnp_CreateDate": datetime.utcnow().strftime("%Y%m%d%H%M%S"),
    }

    payment_url = build_vnpay_url(vnp_params)
    # Optionally create a Payment record in DB with status 'pending'
    payment = Payment(
        booking_id=data.booking_id,
        user_id=data.user_id,
        amount=data.amount,
        payment_method="vnpay",
        payment_status="pending",
        gateway_transaction_id=None,
    )
    await payment.insert()

    return {"payment_url": payment_url, "payment_id": str(payment.id), "txn_ref": txn_ref}


# VNPay return URL endpoint (user redirect after payment)
@router.get("/vnpay/return", summary="VNPay return URL")
async def vnpay_return(**params):
    # VNPay returns many query params including vnp_ResponseCode and vnp_TxnRef etc.
    # Basic handling: check vnp_ResponseCode == "00"
    resp_code = params.get("vnp_ResponseCode")
    txn_ref = params.get("vnp_TxnRef")
    vnp_secure_hash = params.get("vnp_SecureHash")
    # NOTE: In production verify secure hash using secret and sorted params excluding vnp_SecureHash
    if resp_code == "00":
        # Mark payment as completed by txn_ref or other mapping (we saved txn_ref in create)
        # Simple response:
        return {"message": "Payment successful", "vnp_TxnRef": txn_ref}
    return {"message": "Payment failed or cancelled", "vnp_ResponseCode": resp_code}


# VNPay IPN endpoint (server-to-server asynchronous notification)
@router.get("/vnpay/ipn", summary="VNPay IPN (Instant Payment Notification)")
async def vnpay_ipn(**params):
    # For IPN: validate, update DB accordingly, and return a response the gateway expects
    resp_code = params.get("vnp_ResponseCode")
    txn_ref = params.get("vnp_TxnRef")
    # Implementation detail: find payment by txn_ref if stored and update.
    # Here we return a simple acknowledgement.
    return {"received": True, "vnp_TxnRef": txn_ref, "vnp_ResponseCode": resp_code}
