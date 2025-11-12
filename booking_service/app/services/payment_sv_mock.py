def process_payment(amount: int) -> str:
    """Giả lập xử lý thanh toán. Luôn trả về trạng thái 'SUCCESS'."""
    if amount > 5000000:
        # Giả lập thanh toán lỗi với giao dịch lớn
        return "FAILED"
    return "SUCCESS"