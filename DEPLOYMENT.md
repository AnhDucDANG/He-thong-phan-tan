# 🌐 Distributed Deployment Guide with Tailscale

## Kiến trúc phân tán

Hệ thống Car Rental được thiết kế để deploy trên 3 servers riêng biệt, kết nối với nhau qua Tailscale VPN.

```
┌─────────────────────────────────────────────────────────────────┐
│ Server 1 (100.69.63.99) - API Gateway + User + MongoDB         │
├─────────────────────────────────────────────────────────────────┤
│ • API Gateway      :8000                                        │
│ • User Service     :8001                                        │
│ • MongoDB Cluster  :27017 (Sharded: Users, Vehicles, Bookings) │
└─────────────────────────────────────────────────────────────────┘
                             ▲
                             │ Tailscale VPN
            ┌────────────────┴────────────────┐
            │                                 │
┌───────────▼─────────────┐     ┌────────────▼────────────┐
│ Server 2 (100.73.22.88) │     │ Server 3 (100.65.117.32)│
├─────────────────────────┤     ├─────────────────────────┤
│ • Vehicle Service :8002 │     │ • Booking Service :8003 │
└─────────────────────────┘     └─────────────────────────┘
```

## 🚀 Quick Start

### Server 1: API Gateway + User Service + MongoDB

1. **Clone repository:**
   ```bash
   git clone https://github.com/AnhDucDANG/He-thong-phan-tan.git
   cd He-thong-phan-tan
   ```

2. **Cấu hình .env:**
   ```bash
   cp .env.example .env
   # Chỉnh sửa .env với Tailscale IPs của bạn
   ```

3. **Deploy:**
   ```bash
   docker-compose -f docker-compose.sharded-hybrid.yml up -d
   ```

4. **Verify:**
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8001/health
   ```

### Server 2: Vehicle Service

**Chi tiết:** Xem [vehicle-service/CHANGELOG.md](vehicle-service/CHANGELOG.md)

```bash
cd vehicle-service
# Cấu hình .env với API_GATEWAY_URL=http://100.69.63.99:8000
docker-compose -f docker-compose.server2.yml up -d
```

### Server 3: Booking Service

**Chi tiết:** Xem [booking_service/CHANGELOG.md](booking_service/CHANGELOG.md)

```bash
cd booking_service
# Cấu hình .env với API_GATEWAY_URL=http://100.69.63.99:8000
docker-compose -f docker-compose.server3.yml up -d
```

## 🔧 Environment Variables

### Server 1 (.env)

```env
# MongoDB - Local on Server 1
MONGO_URL=mongodb://mongo:27017

# JWT
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Gateway
GATEWAY_HOST=0.0.0.0
GATEWAY_PORT=8000
MY_TAILSCALE_IP=100.69.63.99

# Remote Services via Tailscale
VEHICLE_SERVICE_URL=http://100.73.22.88:8002
BOOKING_SERVICE_URL=http://100.65.117.32:8003
PAYMENT_SERVICE_URL=http://100.108.163.69:8004
```

### Server 2 (.env)

```env
# MongoDB - Kết nối đến Server 1 qua Tailscale
MONGO_URI=mongodb://100.69.63.99:27017/rental

# Service Config
PORT=8002

# API Gateway - Server 1
API_GATEWAY_URL=http://100.69.63.99:8000
```

### Server 3 (.env)

```env
# MongoDB - Kết nối đến Server 1 qua Tailscale
MONGO_URL=mongodb://100.69.63.99:27017
MONGO_DB=rental

# Service Config
SERVICE_HOST=0.0.0.0
SERVICE_PORT=8003

# API Gateway - Server 1
API_GATEWAY_URL=http://100.69.63.99:8000
```

## 🔒 Tailscale Setup

### 1. Cài đặt Tailscale trên tất cả servers

```bash
# Ubuntu/Debian
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# macOS
brew install tailscale
sudo tailscale up
```

### 2. Lấy Tailscale IP

```bash
tailscale ip -4
```

### 3. Verify connectivity

```bash
# Từ Server 2 hoặc 3, ping đến Server 1
tailscale ping 100.69.63.99

# Test API Gateway
curl http://100.69.63.99:8000/health
```

## 📊 Service Communication Flow

### Client → API Gateway → Services

```
Client Request
    ↓
API Gateway (100.69.63.99:8000)
    ↓
    ├─→ User Service (localhost:8001)        [Same server]
    ├─→ Vehicle Service (100.73.22.88:8002)  [Via Tailscale]
    └─→ Booking Service (100.65.117.32:8003) [Via Tailscale]
```

### Service-to-Service via Gateway

```
Booking Service (Server 3)
    ↓ API_GATEWAY_URL
Gateway (100.69.63.99:8000)
    ↓
    ├─→ /api/users/{id} → User Service
    └─→ /api/vehicles/{id} → Vehicle Service
```

## 🧪 Testing

### 1. Test Health Endpoints

```bash
# Server 1
curl http://100.69.63.99:8000/health  # API Gateway
curl http://100.69.63.99:8001/health  # User Service

# Server 2
curl http://100.73.22.88:8002/health  # Vehicle Service

# Server 3
curl http://100.65.117.32:8003/health # Booking Service
```

### 2. Test API Flow

```bash
# Register user via Gateway
curl -X POST http://100.69.63.99:8000/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "password123",
    "full_name": "Test User"
  }'

# Create vehicle (từ Server 2 nhưng qua Gateway)
curl -X POST http://100.69.63.99:8000/api/vehicles \
  -H "Content-Type: application/json" \
  -d '{
    "make": "Toyota",
    "model": "Camry",
    "year": 2024,
    "licensePlate": "ABC-123"
  }'

# Create booking (từ Server 3, calls User & Vehicle services via Gateway)
curl -X POST http://100.69.63.99:8000/api/bookings \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "...",
    "car_id": "...",
    "pickup_location": "HANOI",
    "start_date": "2025-12-01T09:00:00Z",
    "end_date": "2025-12-05T18:00:00Z"
  }'
```

## 🔍 Troubleshooting

### 1. Cannot connect to MongoDB from Server 2/3

**Giải pháp:**
```bash
# Kiểm tra MongoDB bind_ip
docker exec mongo-config-server mongosh --eval "db.adminCommand({getCmdLineOpts: 1})"

# Đảm bảo MongoDB lắng nghe trên tất cả interfaces
# hoặc bind cụ thể đến Tailscale IP
```

### 2. Service không thể gọi qua Gateway

**Kiểm tra:**
```bash
# Verify Tailscale connectivity
tailscale ping 100.69.63.99

# Check Gateway logs
docker logs rental-api-gateway

# Test direct connection
curl -v http://100.69.63.99:8000/health
```

### 3. High latency between services

**Tối ưu:**
- Sử dụng Tailscale direct connections (không qua relay)
- Đặt timeout cao hơn trong health checks
- Cân nhắc deploy services gần nhau về mặt địa lý

## 📈 Monitoring

### View logs từ xa qua Tailscale

```bash
# Logs từ Server 1
ssh user@100.69.63.99 "docker logs rental-api-gateway --tail 50"

# Logs từ Server 2
ssh user@100.73.22.88 "docker logs rental-vehicle-service --tail 50"

# Logs từ Server 3
ssh user@100.65.117.32 "docker logs rental-booking-service --tail 50"
```

## 🔐 Security Best Practices

1. **Tailscale ACLs**: Giới hạn access giữa các services
2. **Firewall**: Chỉ mở ports cần thiết trên localhost
3. **Environment Variables**: Không commit `.env` files
4. **JWT Secrets**: Dùng secrets mạnh, rotate định kỳ
5. **MongoDB Auth**: Enable authentication trong production

## 📚 References

- [Tailscale Documentation](https://tailscale.com/kb/)
- [Docker Compose Networking](https://docs.docker.com/compose/networking/)
- [MongoDB Sharding](https://docs.mongodb.com/manual/sharding/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 👥 Team

Xem chi tiết team trong [TEAM_INFO.md](TEAM_INFO.md)
