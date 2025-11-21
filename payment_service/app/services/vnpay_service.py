import hashlib
import hmac
import urllib.parse
from datetime import datetime
from app.config import settings

class VNPayService:
    def __init__(self):
        self.tmn_code = settings.VNPAY_TMN_CODE
        self.hash_secret = settings.VNPAY_HASH_SECRET
        self.payment_url = settings.VNPAY_URL
        self.return_url = settings.VNPAY_RETURN_URL
        self.api_url = settings.VNPAY_API_URL
    
    def create_payment_url(self, payment_data: dict) -> str:
        vnp_params = {
            'vnp_Version': '2.1.0',
            'vnp_Command': 'pay',
            'vnp_TmnCode': self.tmn_code,
            'vnp_Amount': str(int(payment_data['amount'] * 100)),
            'vnp_CurrCode': 'VND',
            'vnp_TxnRef': payment_data['payment_id'],
            'vnp_OrderInfo': f"Thanh toan don hang {payment_data['booking_id']}",
            'vnp_OrderType': '250000',
            'vnp_Locale': 'vn',
            'vnp_ReturnUrl': self.return_url,
            'vnp_IpAddr': payment_data.get('ip_addr', '127.0.0.1'),
            'vnp_CreateDate': datetime.now().strftime('%Y%m%d%H%M%S')
        }
        
        vnp_params_sorted = sorted(vnp_params.items())
        query_string = '&'.join([f'{key}={urllib.parse.quote_plus(str(value))}' 
                               for key, value in vnp_params_sorted if value])
        
        secure_hash = hmac.new(
            self.hash_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()
        
        vnp_params['vnp_SecureHash'] = secure_hash
        return f"{self.payment_url}?{urllib.parse.urlencode(vnp_params)}"
    
    def verify_return_data(self, return_data: dict) -> dict:
        try:
            vnp_secure_hash = return_data.get('vnp_SecureHash', '')
            verify_data = {k: v for k, v in return_data.items() 
                         if k not in ['vnp_SecureHash', 'vnp_SecureHashType']}
            
            verify_data_sorted = sorted(verify_data.items())
            verify_query_string = '&'.join([f'{key}={urllib.parse.quote_plus(str(value))}' 
                                          for key, value in verify_data_sorted if value])
            
            calculated_hash = hmac.new(
                self.hash_secret.encode('utf-8'),
                verify_query_string.encode('utf-8'),
                hashlib.sha512
            ).hexdigest()
            
            if calculated_hash.upper() == vnp_secure_hash.upper():
                response_code = return_data.get('vnp_ResponseCode', '99')
                
                if response_code == '00':
                    return {
                        'success': True,
                        'message': 'Giao dịch thành công',
                        'transaction_id': return_data.get('vnp_TransactionNo'),
                        'bank_code': return_data.get('vnp_BankCode'),
                        'response_code': response_code
                    }
                else:
                    return {
                        'success': False,
                        'message': f'Giao dịch thất bại. Mã lỗi: {response_code}',
                        'response_code': response_code
                    }
            else:
                return {'success': False, 'message': 'Chữ ký bảo mật không hợp lệ'}
                
        except Exception as e:
            return {'success': False, 'message': f'Lỗi xác minh: {str(e)}'}
    
    def query_transaction_status(self, payment_id: str) -> dict:
        return {
            'success': True,
            'message': 'Query thành công (giả lập)',
            'payment_id': payment_id,
            'status': '00'
        }
    
    def simulate_vnpay_payment(self, payment_id: str, success: bool = True) -> dict:
        if success:
            return {
                'vnp_ResponseCode': '00',
                'vnp_TransactionNo': f'VNPAY{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'vnp_TxnRef': payment_id,
                'vnp_BankCode': 'NCB',
                'vnp_CardType': 'ATM',
                'vnp_SecureHash': 'simulated_hash'
            }
        else:
            return {
                'vnp_ResponseCode': '09',
                'vnp_TxnRef': payment_id,
                'vnp_Message': 'Giao dịch thất bại'
            }