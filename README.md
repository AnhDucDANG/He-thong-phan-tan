# Payment Service

## Tổng quan
Dự án này là một ứng dụng dịch vụ thanh toán cung cấp các chức năng quản lý thanh toán. Nó bao gồm các tính năng tạo, truy xuất, cập nhật và xóa thanh toán thông qua API RESTful.

## Cấu trúc dự án
```
payment_service/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── connection.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── payment_model.py
│   ├── routes/
│   │   ├── __init__.py
│   │   └── payment_routes.py
│   └── schemas/
│       ├── __init__.py
│       └── payment_schema.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env
├── .dockerignore
└── .gitignore
```

## Hướng dẫn cài đặt
1. **Clone repository:**
   ```bash
   git clone <repository-url>
   cd payment_service
   ```

2. **Cài đặt phụ thuộc:**
   Đảm bảo bạn đã cài Python và pip. Sau đó chạy:
   ```bash
   pip install -r requirements.txt
   ```

3. **Cấu hình biến môi trường:**
   Tạo file `.env` ở thư mục gốc và thêm các biến môi trường cần thiết, ví dụ thông tin kết nối database.

4. **Chạy ứng dụng:**
   Bạn có thể chạy ứng dụng bằng:
   ```bash
   python app/main.py
   ```

## Cấu hình Docker
Để chạy ứng dụng bằng Docker:

1. **Xây dựng image Docker:**
   ```bash
   docker build -t payment_service .
   ```

2. **Chạy ứng dụng bằng Docker Compose:**
   ```bash
   docker-compose up
   ```

## Sử dụng
Khi ứng dụng đang chạy, bạn có thể truy cập các endpoint API để quản lý thanh toán. Tham khảo tài liệu API để biết chi tiết các endpoint và cách sử dụng.

## Giấy phép
Dự án này được cấp phép theo MIT License. Xem file LICENSE để biết chi tiết.