from fastapi import APIRouter, HTTPException, status, Request, Query
from typing import List, Optional

from app.models.payment import Payment, PaymentStatus
from app.schemas.payment import PaymentCreate, PaymentResponse, VNPayReturn
from app.services.payment_service import PaymentService

router = APIRouter()
payment_service = PaymentService()

@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(payment_data: PaymentCreate, request: Request):
    """Tạo payment mới và nhận URL thanh toán VNPay"""
    try:
        client_ip = request.client.host if request.client else "127.0.0.1"
        payment = await payment_service.create_payment(payment_data, client_ip)
        return payment
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tạo payment thất bại: {str(e)}"
        )

@router.get("/vnpay-return")
async def vnpay_return(
    vnp_ResponseCode: str = Query(..., description="Mã phản hồi VNPay"),
    vnp_TxnRef: str = Query(..., description="Mã tham chiếu payment"),
    vnp_TransactionNo: Optional[str] = Query(None, description="Mã giao dịch VNPay"),
    vnp_BankCode: Optional[str] = Query(None, description="Mã ngân hàng"),
    vnp_CardType: Optional[str] = Query(None, description="Loại thẻ"),
    vnp_Amount: Optional[str] = Query(None, description="Số tiền"),
    vnp_SecureHash: Optional[str] = Query(None, description="Chữ ký bảo mật")
):
    """Endpoint nhận kết quả thanh toán từ VNPay"""
    try:
        return_data = {
            'vnp_ResponseCode': vnp_ResponseCode,
            'vnp_TxnRef': vnp_TxnRef,
            'vnp_TransactionNo': vnp_TransactionNo,
            'vnp_BankCode': vnp_BankCode,
            'vnp_CardType': vnp_CardType,
            'vnp_Amount': vnp_Amount,
            'vnp_SecureHash': vnp_SecureHash
        }
        
        result = await payment_service.process_vnpay_return(return_data)
        
        if result['success']:
            return {
                "success": True,
                "message": "🎉 Thanh toán thành công!",
                "payment_id": result['payment_id'],
                "amount": result['amount'],
                "booking_id": result['booking_id']
            }
        else:
            return {
                "success": False,
                "message": "❌ Thanh toán thất bại",
                "error": result['message']
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Xử lý kết quả thanh toán thất bại: {str(e)}"
        )

@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(payment_id: str):
    """Lấy thông tin payment bằng ID"""
    payment = await payment_service.get_payment_by_id(payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy payment"
        )
    return payment

@router.get("/booking/{booking_id}", response_model=List[PaymentResponse])
async def get_payments_by_booking(booking_id: str):
    """Lấy tất cả payments của một booking"""
    payments = await payment_service.get_payments_by_booking(booking_id)
    return payments

@router.get("/user/{user_id}", response_model=List[PaymentResponse])
async def get_payments_by_user(user_id: str):
    """Lấy tất cả payments của một user"""
    payments = await payment_service.get_payments_by_user(user_id)
    return payments

@router.post("/{payment_id}/simulate")
async def simulate_payment(
    payment_id: str, 
    success: bool = Query(True, description="Kết quả giả lập")
):
    """Giả lập thanh toán VNPay (testing)"""
    try:
        result = await payment_service.simulate_vnpay_payment(payment_id, success)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Giả lập thanh toán thất bại: {str(e)}"
        )

@router.get("/{payment_id}/query")
async def query_payment_status(payment_id: str):
    """Query trạng thái payment từ VNPay"""
    try:
        result = await payment_service.query_payment_status(payment_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Query payment status thất bại: {str(e)}"
        )