from typing import List, Optional
from app.models.payment import Payment, Transaction, PaymentStatus
from app.schemas.payment import PaymentCreate
from app.services.vnpay_service import VNPayService
from app.services.external_services import ExternalServices

class PaymentService:
    def __init__(self):
        self.vnpay_service = VNPayService()
        self.external_services = ExternalServices()

    async def create_payment(self, payment_data: PaymentCreate, client_ip: str) -> Payment:
        # Kiểm tra booking tồn tại
        booking = await self.external_services.get_booking(payment_data.booking_id)
        if not booking:
            raise ValueError(f"Booking {payment_data.booking_id} không tồn tại")
        
        # Kiểm tra user tồn tại
        user = await self.external_services.get_user(payment_data.user_id)
        if not user:
            raise ValueError(f"User {payment_data.user_id} không tồn tại")
        
        # Tạo payment
        payment = Payment(**payment_data.dict())
        await payment.insert()
        
        # Tạo URL VNPay
        vnpay_data = {
            'payment_id': str(payment.id),
            'booking_id': payment.booking_id,
            'amount': payment.amount,
            'user_id': payment.user_id,
            'ip_addr': client_ip
        }
        
        payment_url = self.vnpay_service.create_payment_url(vnpay_data)
        payment.vnpay_payment_url = payment_url
        await payment.save()
        
        return payment

    async def process_vnpay_return(self, return_data: dict) -> dict:
        vnpay_result = self.vnpay_service.verify_return_data(return_data)
        
        if not vnpay_result['success']:
            return vnpay_result
        
        payment_ref = return_data.get('vnp_TxnRef')
        payment = await Payment.get(payment_ref)
        
        if not payment:
            return {'success': False, 'message': 'Không tìm thấy payment'}
        
        if vnpay_result['success']:
            payment.status = PaymentStatus.COMPLETED
            payment.vnpay_transaction_id = vnpay_result.get('transaction_id')
            payment.vnpay_bank_code = return_data.get('vnp_BankCode')
            payment.vnpay_card_type = return_data.get('vnp_CardType')
            payment.vnpay_response_code = vnpay_result.get('response_code', '00')
            await payment.save()
            
            # Tạo transaction
            transaction = Transaction(
                payment_id=str(payment.id),
                amount=payment.amount,
                transaction_type="payment",
                vnpay_transaction_id=vnpay_result.get('transaction_id'),
                status=PaymentStatus.COMPLETED
            )
            await transaction.insert()
            
            return {
                'success': True,
                'message': 'Thanh toán thành công',
                'payment_id': str(payment.id),
                'amount': payment.amount,
                'booking_id': payment.booking_id
            }
        else:
            payment.status = PaymentStatus.FAILED
            payment.vnpay_response_code = vnpay_result.get('response_code', '99')
            await payment.save()
            
            return {
                'success': False,
                'message': vnpay_result['message'],
                'payment_id': str(payment.id)
            }

    async def get_payment_by_id(self, payment_id: str) -> Optional[Payment]:
        return await Payment.get(payment_id)

    async def get_payments_by_booking(self, booking_id: str) -> List[Payment]:
        return await Payment.find({"booking_id": booking_id}).to_list()

    async def get_payments_by_user(self, user_id: str) -> List[Payment]:
        return await Payment.find({"user_id": user_id}).to_list()

    async def simulate_vnpay_payment(self, payment_id: str, success: bool = True) -> dict:
        payment = await self.get_payment_by_id(payment_id)
        if not payment:
            raise ValueError("Không tìm thấy payment")
        
        simulated_data = self.vnpay_service.simulate_vnpay_payment(payment_id, success)
        result = await self.process_vnpay_return(simulated_data)
        return result

    async def query_payment_status(self, payment_id: str) -> dict:
        return await self.vnpay_service.query_transaction_status(payment_id)