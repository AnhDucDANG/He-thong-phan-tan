# 🚀 QUICK START - VEHICLE SERVICE (Đức)

## Chạy service trong 3 bước:

### 1️⃣ Kiểm tra môi trường
```bash
# Kiểm tra Docker
docker --version

# Kiểm tra Tailscale
tailscale status
tailscale ip -4

# Test kết nối MongoDB của Lâm
Test-NetConnection -ComputerName 100.69.63.99 -Port 27017
```

### 2️⃣ Chạy service
```bash
# Di chuyển đến thư mục vehicle-service
cd D:\baitap\He-thong-phan-tan\vehicle-service

# Chạy vehicle service
docker-compose up -d vehicle_service
```

### 3️⃣ Kiểm tra
```bash
# Xem logs
docker-compose logs -f vehicle_service

# Test API
curl http://localhost:8002/health
curl http://localhost:8002/api/vehicles
```

## 📌 Quan trọng!

- **MongoDB của Lâm:** `100.69.63.99:27017`
- **Database:** `rental_db`
- **Collection:** `vehicles` (Shard 2)
- **Port service:** `8002`
- **Không cần sửa code** - Docker tự động config!

## 🐛 Nếu có lỗi?

```bash
# Xem logs chi tiết
docker-compose logs vehicle_service

# Restart service
docker-compose restart vehicle_service

# Build lại nếu cần
docker-compose up -d --build vehicle_service

# Stop service
docker-compose down
```

## 📖 API Endpoints

```
GET    /health                - Health check
GET    /api/vehicles          - Lấy tất cả vehicles
GET    /api/vehicles/:id      - Lấy 1 vehicle
POST   /api/vehicles          - Tạo vehicle mới
PUT    /api/vehicles/:id      - Cập nhật vehicle
DELETE /api/vehicles/:id      - Xóa vehicle
```

## 📞 Contact

- **Lâm**: 100.69.63.99:8001 (User Service)
- **Ly**: 100.65.117.32:8003 (Booking Service)
- **Hiếu**: 100.108.163.69:8004 (Payment Service)

## 📚 Hướng dẫn chi tiết

Xem file: `HUONG_DAN_KET_NOI_DATABASE.md`
