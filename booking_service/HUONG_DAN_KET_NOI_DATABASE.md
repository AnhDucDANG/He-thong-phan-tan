# 📘 HƯỚNG DẪN KẾT NỐI BOOKING SERVICE VỚI DATABASE CHUNG

**Dành cho: Ly**  
**Người hướng dẫn: Lâm**  
**Ngày: 20/11/2025**

---

## 🎯 MỤC TIÊU

Kết nối **Booking Service** của bạn với **MongoDB Sharded Cluster** (database chung) trên máy của Lâm thông qua Tailscale.

---

## 📋 THÔNG TIN KẾT NỐI

### 🔗 Database Connection String
```
mongodb://mongos:27017/rental_db
```

### 🌐 Tailscale Network
- **IP máy Lâm**: `100.69.63.99`
- **Port MongoDB Router (mongos)**: `27017`
- **Database name**: `rental_db` (database chung cho tất cả services)

### 📍 Service URLs
```bash
User Service:    http://100.69.63.99:8001
Vehicle Service: http://100.73.22.88:8002 (Đức)
Booking Service: http://100.65.117.32:8003 (Ly - bạn)
Payment Service: http://100.108.163.69:8004 (Hiếu)
```

---

## 🔧 CÁC BƯỚC THỰC HIỆN

### **Bước 1: Cài đặt Docker Desktop (Bắt buộc)**

1. Download Docker Desktop: https://www.docker.com/products/docker-desktop
2. Cài đặt và khởi động Docker Desktop
3. Kiểm tra Docker đã chạy:
   ```bash
   docker --version
   docker-compose --version
   ```

### **Bước 2: Cài đặt Tailscale (Bắt buộc)**

1. Download Tailscale: https://tailscale.com/download
2. Cài đặt và đăng nhập
3. Kiểm tra IP Tailscale của bạn:
   ```bash
   # Windows PowerShell
   tailscale ip -4
   
   # Kết quả: 100.65.117.32 (hoặc IP khác)
   ```

### **Bước 3: Test kết nối đến MongoDB của Lâm**

```bash
# Windows PowerShell
Test-NetConnection -ComputerName 100.69.63.99 -Port 27017

# Nếu thành công sẽ thấy:
# TcpTestSucceeded : True
```

**⚠️ QUAN TRỌNG:** Nếu test không thành công, liên hệ Lâm để mở firewall!

---

## 📝 SỬA CODE (Tùy chọn - Nếu không dùng Docker)

**⚠️ LƯU Ý:** Nếu bạn chạy bằng `docker-compose up`, KHÔNG CẦN sửa code! Docker sẽ tự động inject biến môi trường.

**Chỉ sửa code nếu bạn chạy trực tiếp Python (không dùng Docker):**

### **File 1: `booking_service/app/core/config.py`**

**❌ HIỆN TẠI (SAI):**
```python
MONGO_URL = f"mongodb://{MONGO_USER_QUOTED}:{MONGO_PASSWORD_QUOTED}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}"
```

**✅ SỬA THÀNH:**
```python
class Settings:
    # ... các config khác giữ nguyên ...

    # MongoDB Connection - Kết nối đến sharded cluster của Lâm
    MONGO_URL = os.getenv("MONGO_URL")
    if not MONGO_URL:
        # Default: Kết nối qua Tailscale
        MONGO_URL = "mongodb://100.69.63.99:27017/rental_db"
    
    MONGO_DB = os.getenv("MONGO_DB", "rental_db")  # Database chung
```

**📝 Giải thích:**
- Không cần username/password vì MongoDB của Lâm chưa bật authentication
- Kết nối trực tiếp qua Tailscale IP: `100.69.63.99:27017`
- Database chung: `rental_db` (thay vì `BookingCar`)

---

### **File 2: `booking_service/.env`**


**✅ THÊM cấu hình mới:**
```bash
# ==================== MongoDB Connection ====================
# Kết nối đến sharded cluster của Lâm qua Tailscale
MONGO_URL=mongodb://100.69.63.99:27017/rental_db
MONGO_DB=rental_db

# ==================== Service Info ====================
SERVICE_PORT=8003
SERVICE_HOST=0.0.0.0

# Tailscale IP của máy bạn (Ly)
MY_TAILSCALE_IP=100.65.117.32

# ==================== External Services ====================
USER_SERVICE_URL=http://100.69.63.99:8001
VEHICLE_SERVICE_URL=http://100.73.22.88:8002
BOOKING_SERVICE_URL=http://100.65.117.32:8003
PAYMENT_SERVICE_URL=http://100.108.163.69:8004

# ==================== Security ====================
SECRET_KEY=35a91c468c0a8a62d3669ba143ddf1db
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

---

### **File 3: `booking_service/app/database/connection.py`**

**✅ Giữ nguyên** - Code hiện tại đã đúng! Chỉ cần đảm bảo:
- `settings.MONGO_URL` được lấy từ `.env`
- Beanie Document models được init đúng


## 🚀 CHẠY SERVICE

### **⭐ PHƯƠNG ÁN KHUYẾN NGHỊ: Dùng Docker Compose**

```bash
# 1. Di chuyển đến thư mục gốc
cd D:\baitap\He-thong-phan-tan

# 2. Kiểm tra Tailscale
tailscale status

# 3. Chạy booking service
docker-compose up -d booking_service

# 4. Xem logs real-time
docker-compose logs -f booking_service

# 5. Kiểm tra container đang chạy
docker-compose ps

# 6. Test service
curl http://localhost:8003/health
# Hoặc mở browser: http://localhost:8003

# 7. Dừng service (khi không dùng)
docker-compose down
```

**✅ Ưu điểm:**
- Không cần sửa code
- Tự động inject environment variables
- Dễ quản lý và restart
- Logs tập trung

### **Cách 2: Chạy trực tiếp Python (Không khuyến nghị - chỉ để test)**

```bash
# 1. Cài dependencies
cd booking_service
pip install -r requirements.txt

# 2. Set biến môi trường (PowerShell)
$env:MONGO_URL="mongodb://100.69.63.99:27017/rental_db"
$env:MONGO_DB="rental_db"
$env:SERVICE_PORT="8003"

# 3. Chạy service
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload

# 4. Test
# Mở browser: http://localhost:8003
# Hoặc: curl http://localhost:8003/health
```

### **Cách 2: Chạy với Docker Compose (KHUYẾN NGHỊ)**

```bash
# 1. Đảm bảo đã sửa file docker-compose.yml trong thư mục gốc
cd D:\baitap\He-thong-phan-tan

# 2. Kiểm tra Tailscale đã chạy
tailscale status

# 3. Build và chạy service
docker-compose up -d booking_service

# 4. Xem logs
docker-compose logs -f booking_service

# 5. Test
curl http://localhost:8003/health

# 6. Dừng service
docker-compose down
```

**📝 Lưu ý về docker-compose.yml:**
- File `docker-compose.yml` ở thư mục gốc đã được cấu hình sẵn
- Không cần MongoDB container riêng
- Kết nối trực tiếp đến MongoDB của Lâm qua Tailscale
- Sử dụng `network_mode: host` để kết nối Tailscale dễ dàng

### **Cách 3: Chạy Docker thủ công (Nếu không dùng docker-compose)**

```bash
# 1. Build image
cd booking_service
docker build -t booking-service .

# 2. Run container với network mode host
docker run -d \
  --name booking-service \
  --network host \
  -e MONGO_URL=mongodb://100.69.63.99:27017/rental_db \
  -e MONGO_DB=rental_db \
  -e SERVICE_PORT=8003 \
  booking-service

# 3. Xem logs
docker logs -f booking-service

# 4. Test
curl http://localhost:8003/health
```

---

## ✅ KIỂM TRA KẾT NỐI

### **Test 1: Health Check**
```bash
curl http://localhost:8003/health
# Hoặc mở browser: http://localhost:8003/health

# Kết quả mong đợi:
{
  "status": "healthy",
  "database": "connected",
  "mongodb_process": "mongos"  # ← Quan trọng!
}
```

### **Test 2: Tạo booking thử nghiệm**
```bash
curl -X POST http://localhost:8003/api/v1/bookings \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "car_id": "test-car-001",
    "start_date": "2025-11-25T10:00:00",
    "end_date": "2025-11-27T10:00:00",
    "daily_rate": 500000,
    "total_days": 2,
    "book_price": 1000000
  }'
```

### **Test 3: Kiểm tra trong MongoDB**
```bash
# Kết nối vào MongoDB của Lâm
mongosh mongodb://100.69.63.99:27017/rental_db

# Xem dữ liệu
db.bookings.find().pretty()

# Xem sharding status
sh.status()
```

---

## 🐛 TROUBLESHOOTING

### **Lỗi 1: Connection timeout**
```
Error: connect ETIMEDOUT 100.69.63.99:27017
```
**Giải pháp:**
- Kiểm tra Tailscale đã đăng nhập chưa: `tailscale status`
- Ping thử: `ping 100.69.63.99`
- Kiểm tra firewall Windows của Lâm đã mở port 27017

### **Lỗi 2: Database không tồn tại**
```
Error: Database 'BookingCar' not found
```
**Giải pháp:**
- Đảm bảo đã sửa `MONGO_DB=rental_db` trong `.env`
- Không dùng database riêng `BookingCar`

### **Lỗi 3: Authentication failed**
```
Error: Authentication failed
```
**Giải pháp:**
- Xóa username/password trong MONGO_URL
- MongoDB của Lâm không dùng authentication

### **Lỗi 4: Collection không được shard**
**Giải pháp:**
- Liên hệ Lâm để thêm sharding cho collection `bookings`
- Hoặc chờ Lâm cấu hình trong `init-sharding/setup-indexes.js`

---

## 📞 LIÊN HỆ HỖ TRỢ

**Nếu gặp vấn đề, liên hệ Lâm:**
- Tailscale IP: `100.69.63.99`
- Service: User Service @ `http://100.69.63.99:8001`
- MongoDB Router: `100.69.63.99:27017`

---

## 📚 TÀI LIỆU THAM KHẢO

- MongoDB Sharding: https://www.mongodb.com/docs/manual/sharding/
- Beanie ODM: https://beanie-odm.dev/
- FastAPI: https://fastapi.tiangolo.com/
- Tailscale: https://tailscale.com/kb/

---

## ✨ CHECKLIST HOÀN THÀNH

### **Setup môi trường:**
- [ ] Cài đặt Docker Desktop
- [ ] Cài đặt Tailscale và đăng nhập
- [ ] Test kết nối đến `100.69.63.99:27017`
- [ ] Kiểm tra IP Tailscale của bạn (nên là `100.65.117.32`)

### **Chạy service:**
- [ ] Pull code mới nhất từ repo (git pull)
- [ ] Di chuyển đến thư mục gốc project
- [ ] Chạy: `docker-compose up -d booking_service`
- [ ] Kiểm tra logs không có lỗi
- [ ] Test health check: `http://localhost:8003/health`

### **Kiểm tra kết nối:**
- [ ] Health check response có `"mongodb_process": "mongos"`
- [ ] Tạo booking thử nghiệm thành công
- [ ] Kiểm tra data xuất hiện trong MongoDB của Lâm
- [ ] Service có thể gọi User Service của Lâm

### **Hoàn tất:**
- [ ] Báo Lâm đã kết nối thành công ✅
- [ ] Gửi IP Tailscale của bạn cho Lâm
- [ ] Test tích hợp với các service khác

---

**Chúc bạn thành công! 🎉**
