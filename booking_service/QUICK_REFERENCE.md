# 🎯 QUICK REFERENCE - BOOKING SERVICE

## 📦 Thông tin kết nối nhanh

```bash
MongoDB:     mongodb://100.69.63.99:27017/rental_db
Database:    rental_db
Collection:  bookings
Port:        8003
```

## ⚡ Lệnh nhanh

### 1. Test kết nối
```powershell
# Chạy script test
cd D:\baitap\He-thong-phan-tan\booking_service
.\test_connection.ps1

# Hoặc test thủ công
Test-NetConnection -ComputerName 100.69.63.99 -Port 27017
```

### 2. Chạy bằng Docker Compose (KHUYẾN NGHỊ)
```bash
# Di chuyển về thư mục gốc
cd D:\baitap\He-thong-phan-tan

# Chạy service
docker-compose up -d booking_service

# Xem logs
docker-compose logs -f booking_service

# Dừng service
docker-compose down
```

### 3. Test API
```bash
# Health check
curl http://localhost:8003/health

# Tạo booking
curl -X POST http://localhost:8003/api/v1/bookings \
  -H "Content-Type: application/json" \
  -d '{"user_id":1,"car_id":"test-001","start_date":"2025-11-25T10:00:00","end_date":"2025-11-27T10:00:00","daily_rate":500000,"total_days":2,"book_price":1000000}'
```

## 🔧 Sửa code nhanh

### config.py
```python
# Thay dòng 25-40 thành:
MONGO_URL = os.getenv("MONGO_URL", "mongodb://100.69.63.99:27017/rental_db")
MONGO_DB = os.getenv("MONGO_DB", "rental_db")
```

### booking_model.py
```python
# Dòng 42:
name = "bookings"  # Đổi từ "booking" thành "bookings"
```

## 🐛 Fix lỗi thường gặp

| Lỗi | Giải pháp |
|------|-----------|
| Connection timeout | Kiểm tra Tailscale đã login chưa |
| Auth failed | Xóa username/password trong MONGO_URL |
| Database not found | Dùng `rental_db` thay vì `BookingCar` |
| Port 8003 in use | Đổi port hoặc kill process cũ |

## 📞 Contact
- **Lâm**: 100.69.63.99:8001 (User Service)
- **Đức**: 100.73.22.88:8002 (Vehicle Service)
- **Hiếu**: 100.108.163.69:8004 (Payment Service)

## 📚 Files quan trọng
- `HUONG_DAN_KET_NOI_DATABASE.md` - Hướng dẫn chi tiết
- `.env.example` - Config mẫu
- `test_connection.ps1` - Script test tự động
