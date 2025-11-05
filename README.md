# 🚗 Hệ Thống Quản Lý Cho Thuê Xe - Kiến Trúc Phân Tán

## Mô tả

Hệ thống microservices cho thuê xe tự lái được xây dựng theo kiến trúc phân tán, kết nối các services trên nhiều máy khác nhau thông qua Tailscale VPN.

## Kiến trúc hệ thống

### Sơ đồ tổng quan

```
┌─────────────────────────────────────────────────────────────┐
│           Tailscale VPN Network (100.x.x.x)                 │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  MÁY LEADER (100.69.63.99)                           │  │
│  │                                                       │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │ API Gateway │→ │ User Service│→ │  MongoDB    │  │  │
│  │  │   Port 8000 │  │   Port 8001 │  │ Port 27017  │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │  │
│  │         │                                            │  │
│  └─────────┼────────────────────────────────────────────┘  │
│            │                                               │
│            ├──────────────┬──────────────┬─────────────────┤
│            ↓              ↓              ↓                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  MEMBER 1    │  │  MEMBER 2    │  │  MEMBER 3    │    │
│  │ 100.x.x.x    │  │ 100.x.x.x    │  │ 100.x.x.x    │    │
│  │              │  │              │  │              │    │
│  │ Vehicle      │  │ Booking      │  │ Payment      │    │
│  │ Service      │  │ Service      │  │ Service      │    │
│  │ :8002        │  │ :8003        │  │ :8004        │    │
│  │              │  │              │  │              │    │
│  │ PostgreSQL   │  │ PostgreSQL   │  │ MongoDB      │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Thành phần hệ thống

#### Máy Leader (Gateway Server)
- **Tailscale IP:** 100.69.63.99
- **Services:**
  - API Gateway (Port 8000) - Điều phối requests
  - User Service (Port 8001) - Quản lý người dùng & xác thực
  - MongoDB (Port 27017) - Cơ sở dữ liệu users

#### Team Members (Worker Nodes)
- **Member 1:** Vehicle Service + PostgreSQL (Port 8002)
- **Member 2:** Booking Service + PostgreSQL (Port 8003)
- **Member 3:** Payment Service + MongoDB (Port 8004)

## Hướng dẫn triển khai

### Yêu cầu hệ thống
### Bước 1: Cài đặt Tailscale

```powershell
# Download từ: https://tailscale.com/download
# Hoặc dùng winget
winget install Tailscale.Tailscale
```

### Bước 2: Đăng nhập Tailscale

1. Mở Tailscale
2. Click "Log in"
3. Chọn Google/GitHub/Microsoft
4. Hoàn tất đăng nhập

### Bước 3: Lấy Tailscale IP

```powershell
tailscale ip -4
# Output: 100.69.63.99 (IP của bạn)
```

### Bước 4: Clone và cấu hình project

```bash
# Clone project
git clone <repo-url>
cd He-thong-phan-tan

# Build và start
docker-compose --env-file .env up -d

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
.\test-system.ps1
```

---

## 🛠️ Development

### Rebuild sau khi sửa code

```bash
# Stop containers
docker-compose down

# Rebuild với no-cache
docker-compose build --no-cache

# Start lại
docker-compose --env-file .env up -d
```

### Xem logs

```bash
# Tất cả services
docker-compose logs -f

# Service cụ thể
docker-compose logs -f api_gateway
docker-compose logs -f user_service
docker-compose logs -f mongo
```

### Debug

```bash
# Exec vào container
docker exec -it rental-api-gateway bash
docker exec -it rental-user-service bash

# Kiểm tra MongoDB
docker exec -it rental-mongo mongosh
> show dbs
> use rental_user_db
> db.users.find()
```

---

## 🔐 Bảo mật

### JWT Authentication

- **Algorithm:** HS256
- **Expiration:** 60 minutes
- **Secret Key:** Được chia sẻ giữa tất cả services

### Password Hashing

- **Algorithm:** bcrypt
- **Salt rounds:** 12

### Protected Routes

Routes yêu cầu authentication:
- `/api/users/me`
- `/api/vehicles/*` 
- `/api/bookings/*`
- `/api/payments/*`

---

## 📊 Monitoring

### Health Check tất cả services

```powershell
curl http://100.69.63.99:8000/api/health/all
```

Response:
```json
{
  "users": {
    "status": "healthy",
    "response_time": 0.05
  },
  "vehicles": {
    "status": "healthy",
    "response_time": 0.12
  },
  "bookings": {
    "status": "healthy",
    "response_time": 0.15
  },
  "payments": {
    "status": "unreachable",
    "error": "Connection timeout"
  }
}
```

### Monitoring Script

## 🗄️ Databases

### MongoDB (User Service)

- **Host:** 100.69.63.99:27017
- **Database:** rental_user_db
- **Collection:** users

**Kết nối với MongoDB Compass:**
```
mongodb://100.69.63.99:27017
```

**Schema:**
```javascript
{
  _id: ObjectId,
  username: String,
  email: String,
  password: String (hashed),
  role: String (customer/admin),
  created_at: Date
}
```

### PostgreSQL (Vehicle & Booking Services)

- **Port:** 5432
- **Database:** rental_vehicle_db / rental_booking_db
- **User:** rental_user
- **Password:** [Xem trong .env của member]

---

## 🚨 Troubleshooting

### Problem: Cannot connect to service

```powershell
# 1. Kiểm tra Tailscale đang chạy
tailscale status

# 2. Kiểm tra Docker containers
docker-compose ps

# 3. Test ping
ping 100.69.63.99

# 4. Test port
Test-NetConnection -ComputerName 100.69.63.99 -Port 8000
```

### Problem: 401 Unauthorized

```bash
# Kiểm tra SECRET_KEY giống nhau
docker exec rental-api-gateway env | grep SECRET_KEY
```

### Problem: Service timeout

```python
# Tăng timeout trong config.py
REQUEST_TIMEOUT = 120  # 2 minutes
```

### Problem: Database connection failed

```bash
# Kiểm tra MongoDB
docker exec rental-mongo mongosh --eval "db.adminCommand('ping')"

# Restart MongoDB
docker-compose restart mongo
