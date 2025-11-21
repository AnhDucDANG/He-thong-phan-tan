# 📘 HƯỚNG DẪN KẾT NỐI VEHICLE SERVICE VỚI DATABASE CHUNG

**Dành cho: Đức**  
**Người hướng dẫn: Lâm**  
**Ngày: 21/11/2025**

---

## 🎯 MỤC TIÊU

Kết nối **Vehicle Service** của bạn (Node.js + Express + Mongoose) với **MongoDB Sharded Cluster** (database chung) trên máy của Lâm thông qua Tailscale.

---

## 📋 THÔNG TIN KẾT NỐI

### 🔗 Database Connection String
```
mongodb://100.69.63.99:27017/rental_db
```

### 🌐 Tailscale Network
- **IP máy Lâm**: `100.69.63.99`
- **Port MongoDB Router (mongos)**: `27017`
- **Database name**: `rental_db` (database chung cho tất cả services)
- **Collection**: `vehicles` (sẽ được lưu ở Shard 2)

### 📍 Service URLs
```bash
User Service:    http://100.69.63.99:8001 (Lâm)
Vehicle Service: http://100.73.22.88:8002 (Đức - bạn)
Booking Service: http://100.65.117.32:8003 (Ly)
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
   
   # Kết quả: 100.73.22.88 (hoặc IP khác)
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

**⚠️ LƯU Ý:** Nếu bạn chạy bằng `docker-compose up`, **KHÔNG CẦN sửa code**! Docker sẽ tự động inject biến môi trường.

**Chỉ sửa code nếu bạn chạy trực tiếp Node.js (không dùng Docker):**

### **File 1: `vehicle-service/.env`**

Tạo file `.env` ở thư mục gốc `vehicle-service/`:

```bash
# Kết nối đến MongoDB của Lâm qua Tailscale
MONGO_URI=mongodb://100.69.63.99:27017/rental_db

# Port service
PORT=8002

# Tailscale IP của máy Đức
MY_TAILSCALE_IP=100.73.22.88

# External Services
USER_SERVICE_URL=http://100.69.63.99:8001
VEHICLE_SERVICE_URL=http://100.73.22.88:8002
BOOKING_SERVICE_URL=http://100.65.117.32:8003
PAYMENT_SERVICE_URL=http://100.108.163.69:8004
```

### **File 2: `vehicle-service/src/config/database.js`**

**✅ Giữ nguyên** - Code hiện tại đã đúng! File này đã dùng `process.env.MONGO_URI`.

### **File 3: `vehicle-service/server.js`**

**✅ Giữ nguyên** - Code hiện tại đã đúng! File này đã load biến môi trường từ `.env`.

---

## 🚀 CHẠY SERVICE

### **⭐ PHƯƠNG ÁN KHUYẾN NGHỊ: Dùng Docker Compose**

```bash
# 1. Di chuyển đến thư mục vehicle-service
cd D:\baitap\He-thong-phan-tan\vehicle-service

# 2. Kiểm tra Tailscale
tailscale status

# 3. Chạy vehicle service
docker-compose up -d vehicle_service

# 4. Xem logs real-time
docker-compose logs -f vehicle_service

# 5. Kiểm tra container đang chạy
docker-compose ps

# 6. Test service
curl http://100.73.22.88:8002/health
# Hoặc mở browser: http://localhost:8002

# 7. Dừng service (khi không dùng)
docker-compose down
```

**✅ Ưu điểm:**
- Không cần sửa code
- Tự động inject environment variables
- Dễ quản lý và restart
- Logs tập trung

### **Cách 3: Chạy Docker thủ công (Nếu không dùng docker-compose)**

```bash
# 1. Build image
cd vehicle-service
docker build -t vehicle-service .

# 2. Run container với network mode host
docker run -d \
  --name vehicle-service \
  --network host \
  -e MONGO_URI=mongodb://100.69.63.99:27017/rental_db \
  -e PORT=8002 \
  vehicle-service

# 3. Xem logs
docker logs -f vehicle-service

# 4. Test
curl http://localhost:8002/health
```

---

## ✅ KIỂM TRA KẾT NỐI

### **Test 1: Health Check**
```bash
curl http://localhost:8002/health
# Hoặc mở browser: http://localhost:8002/health

# Kết quả mong đợi:
{
  "service": "Vehicle Service",
  "status": "Running",
  "database": "connected"
}
```

### **Test 2: Lấy danh sách vehicles**
```bash
# GET tất cả vehicles
curl http://localhost:8002/api/vehicles

# Hoặc test với Postman:
# GET http://localhost:8002/api/vehicles
```

### **Test 3: Tạo vehicle thử nghiệm**
```bash
curl -X POST http://100.73.22.88:8002/api/vehicles \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "Toyota",
    "model": "Camry",
    "year": 2024,
    "licensePlate": "29A-12345",
    "pricePerDay": 500000,
    "status": "available",
    "location": "Hanoi"
  }'
```

### **Test 4: Kiểm tra trong MongoDB**
```bash
# Kết nối vào MongoDB của Lâm (yêu cầu mongosh)
mongosh mongodb://100.69.63.99:27017/rental_db

# Xem dữ liệu vehicles
db.vehicles.find().pretty()

# Kiểm tra shard nào lưu trữ
db.vehicles.getShardDistribution()

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
- Liên hệ Lâm để kiểm tra MongoDB đang chạy

### **Lỗi 2: Port 8002 already in use**
```
Error: Port 8002 is already allocated
```
**Giải pháp:**
```bash
# Tìm process đang dùng port 8002
netstat -ano | findstr :8002

# Kill process (thay <PID> bằng số process ID)
taskkill /PID <PID> /F

# Hoặc đổi port trong docker-compose.yml:
# ports: - "8003:8002"
```

### **Lỗi 3: Database 'vehicle_db' not found**
```
Error: Database 'vehicle_db' not found
```
**Giải pháp:**
- Đảm bảo `MONGO_URI` dùng database `rental_db` (không phải `vehicle_db`)
- Sửa trong `.env`: `MONGO_URI=mongodb://100.69.63.99:27017/rental_db`

### **Lỗi 4: Docker build failed**
```
Error: Cannot find module 'express'
```
**Giải pháp:**
- Đảm bảo file `package.json` có đầy đủ dependencies
- Rebuild image: `docker-compose build --no-cache vehicle_service`

### **Lỗi 5: Health check failed**
```
MongoDB Connection Error: MongoServerError
```
**Giải pháp:**
- Kiểm tra MongoDB của Lâm đang chạy
- Kiểm tra connection string đúng format
- Xem logs chi tiết: `docker-compose logs vehicle_service`

---

## 📞 LIÊN HỆ HỖ TRỢ

**Nếu gặp vấn đề, liên hệ Lâm:**
- Tailscale IP: `100.69.63.99`
- Service: User Service @ `http://100.69.63.99:8001`
- MongoDB Router: `100.69.63.99:27017`

---

## 📚 TÀI LIỆU THAM KHẢO

- MongoDB Sharding: https://www.mongodb.com/docs/manual/sharding/
- Mongoose Documentation: https://mongoosejs.com/docs/
- Express.js Guide: https://expressjs.com/
- Tailscale: https://tailscale.com/kb/
- Docker Compose: https://docs.docker.com/compose/

---

## 📝 NOTES - QUAN TRỌNG

### **Về Database và Collection:**
- **Database chung**: `rental_db` (KHÔNG dùng `vehicle_db` riêng nữa)
- **Collection**: `vehicles` sẽ tự động được tạo khi insert dữ liệu đầu tiên
- **Sharding**: Collection `vehicles` sẽ được lưu ở **Shard 2** và phân tán theo `vehicle_id`

### **Về Schema:**
Mongoose schema của bạn sẽ tự động tạo collection. Đảm bảo model name là số ít:
```javascript
// vehicle-service/src/models/Vehicle.js
module.exports = mongoose.model('Vehicle', vehicleSchema);
// Mongoose sẽ tự động tạo collection tên "vehicles" (số nhiều)
```

### **Về API Endpoints:**
Service của bạn sẽ expose các endpoints:
```
GET    /api/vehicles          - Lấy tất cả vehicles
GET    /api/vehicles/:id      - Lấy 1 vehicle theo ID
POST   /api/vehicles          - Tạo vehicle mới
PUT    /api/vehicles/:id      - Cập nhật vehicle
DELETE /api/vehicles/:id      - Xóa vehicle
GET    /health                - Health check
```

---

## ✨ CHECKLIST HOÀN THÀNH

### **Setup môi trường:**
- [ ] Cài đặt Docker Desktop
- [ ] Cài đặt Tailscale và đăng nhập
- [ ] Test kết nối đến `100.69.63.99:27017`
- [ ] Kiểm tra IP Tailscale của bạn (nên là `100.73.22.88`)

### **Chạy service:**
- [ ] Pull code mới nhất từ repo (git pull)
- [ ] Di chuyển đến thư mục `vehicle-service`
- [ ] Chạy: `docker-compose up -d vehicle_service`
- [ ] Kiểm tra logs không có lỗi
- [ ] Test health check: `http://localhost:8002/health`

### **Kiểm tra kết nối:**
- [ ] Health check response có `"database": "connected"`
- [ ] Tạo vehicle thử nghiệm thành công
- [ ] Kiểm tra data xuất hiện trong MongoDB của Lâm
- [ ] API có thể được gọi từ máy khác qua Tailscale

### **Tích hợp:**
- [ ] Booking Service (Ly) có thể gọi API của bạn
- [ ] User Service (Lâm) có thể xác thực requests
- [ ] Test end-to-end flow: Login → Get Vehicles → Create Booking

### **Hoàn tất:**
- [ ] Báo Lâm đã kết nối thành công ✅
- [ ] Gửi IP Tailscale của bạn cho Lâm
- [ ] Test với Postman collection (file `postman_collection.json`)

---

**Chúc bạn thành công! 🎉**

---

## 🔥 BONUS: Script Test Nhanh

Tạo file `test_connection.ps1` trong thư mục `vehicle-service`:

```powershell
# Test kết nối nhanh cho Vehicle Service

Write-Host "`n=== VEHICLE SERVICE CONNECTION TEST ===" -ForegroundColor Cyan

# 1. Check Tailscale
Write-Host "`n[1/6] Checking Tailscale..." -ForegroundColor Yellow
$tailscaleStatus = tailscale status 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Tailscale is running" -ForegroundColor Green
    $myIP = tailscale ip -4
    Write-Host "   Your IP: $myIP" -ForegroundColor Gray
} else {
    Write-Host "❌ Tailscale not running!" -ForegroundColor Red
    exit 1
}

# 2. Ping MongoDB server
Write-Host "`n[2/6] Pinging MongoDB server..." -ForegroundColor Yellow
$pingResult = Test-Connection -ComputerName 100.69.63.99 -Count 2 -Quiet
if ($pingResult) {
    Write-Host "✅ Can reach Lâm's server" -ForegroundColor Green
} else {
    Write-Host "❌ Cannot reach server!" -ForegroundColor Red
    exit 1
}

# 3. Test MongoDB port
Write-Host "`n[3/6] Testing MongoDB port 27017..." -ForegroundColor Yellow
$portTest = Test-NetConnection -ComputerName 100.69.63.99 -Port 27017 -WarningAction SilentlyContinue
if ($portTest.TcpTestSucceeded) {
    Write-Host "✅ MongoDB port is open" -ForegroundColor Green
} else {
    Write-Host "❌ MongoDB port is closed!" -ForegroundColor Red
    exit 1
}

# 4. Check Docker
Write-Host "`n[4/6] Checking Docker..." -ForegroundColor Yellow
$dockerVersion = docker --version 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Docker is installed: $dockerVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Docker not found!" -ForegroundColor Red
    exit 1
}

# 5. Check Node.js
Write-Host "`n[5/6] Checking Node.js..." -ForegroundColor Yellow
$nodeVersion = node --version 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Node.js is installed: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "⚠️  Node.js not found (OK if using Docker)" -ForegroundColor Yellow
}

# 6. Test User Service
Write-Host "`n[6/6] Testing User Service..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://100.69.63.99:8001/health" -TimeoutSec 5 -UseBasicParsing
    Write-Host "✅ User Service is reachable" -ForegroundColor Green
} catch {
    Write-Host "⚠️  User Service not reachable (may not be running)" -ForegroundColor Yellow
}

Write-Host "`n=== TEST COMPLETED ===" -ForegroundColor Cyan
Write-Host "`nNext steps:" -ForegroundColor White
Write-Host "  1. Run: docker-compose up -d vehicle_service" -ForegroundColor Gray
Write-Host "  2. Check logs: docker-compose logs -f vehicle_service" -ForegroundColor Gray
Write-Host "  3. Test API: curl http://localhost:8002/health" -ForegroundColor Gray
Write-Host ""
```

Chạy test:
```bash
cd vehicle-service
.\test_connection.ps1
```
