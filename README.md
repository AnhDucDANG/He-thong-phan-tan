# Hệ Thống Quản Lý Cho Thuê Xe - Kiến Trúc Phân Tán

## Mô tả
Hệ thống microservices cho thuê xe tự lái với kiến trúc phân tán.

## Kiến trúc
```
[Client] → [API Gateway:8000] → [User Service:8001] → [MongoDB:27017]
```

## Chạy hệ thống

### Yêu cầu
- Docker Desktop
- Docker Compose

### Khởi động
```bash
# Clone project
git clone <repo-url>
cd He-thong-phan-tan

# Build và start
docker-compose up -d

# Xem logs
docker-compose logs -f
```

## API Endpoints

### Qua API Gateway (Port 8000)
- `GET /health` - Health check
- `POST /api/users/register` - Đăng ký
- `POST /api/users/login` - Đăng nhập
- `GET /api/users/me` - Thông tin user (cần token)

### Direct User Service (Port 8001)
- `GET /health` - Health check
- `POST /users/register` - Đăng ký
- `POST /users/login` - Đăng nhập

## Test
```powershell
# Health check
Invoke-RestMethod http://localhost:8000/health

# Xem Swagger docs
# http://localhost:8000/docs
# http://localhost:8001/docs
```

## Development
```bash
# Rebuild sau khi sửa code
docker-compose up -d --build

# Xem logs service cụ thể
docker-compose logs -f user_service
```

## MongoDB
- Host: localhost:27017
- Database: rental_user_db
- Sử dụng MongoDB Compass để xem dữ liệu