# 🚀 QUICK START - BOOKING SERVICE (Ly)

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
# Di chuyển đến thư mục gốc
cd D:\baitap\He-thong-phan-tan

# Chạy booking service
docker-compose up -d booking_service
```

### 3️⃣ Kiểm tra
```bash
# Xem logs
docker-compose logs -f booking_service

# Test API
curl http://localhost:8003/health
```

## 📌 Quan trọng!

- **MongoDB của Lâm:** `100.69.63.99:27017`
- **Database:** `rental_db`
- **Port service:** `8003`
- **Không cần sửa code** - Docker tự động config!

## 🐛 Nếu có lỗi?

```bash
# Xem logs chi tiết
docker-compose logs booking_service

# Restart service
docker-compose restart booking_service

# Build lại nếu cần
docker-compose up -d --build booking_service
```

## 📖 Hướng dẫn chi tiết

Xem file: `HUONG_DAN_KET_NOI_DATABASE.md`
