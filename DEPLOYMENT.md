# 🚀 Distributed Deployment Guide with Tailscale

## Architecture Overview

```
Server 1 (100.69.63.99) - Main Server:
├─> API Gateway (:8000)
├─> User Service (:8001)
└─> MongoDB Cluster (Sharded)

Server 2 (100.73.22.88) - Vehicle Service:
└─> Vehicle Service (:8002)
    └─> Connects to: API Gateway @ 100.69.63.99:8000

Server 3 (100.65.117.32) - Booking Service:
└─> Booking Service (:8003)
    └─> Connects to: API Gateway @ 100.69.63.99:8000
```

## Prerequisites

1. **Tailscale installed** trên tất cả servers
2. **Docker và Docker Compose** installed
3. **Git** để clone repo

## Deployment Instructions

### Server 1 (API Gateway + User + MongoDB)

```bash
# 1. Clone repository
git clone https://github.com/AnhDucDANG/He-thong-phan-tan.git
cd He-thong-phan-tan

# 2. Setup environment
cp .env.server1.example .env
nano .env  # Cập nhật các Tailscale IPs

# 3. Deploy
docker compose -f docker-compose.sharded-hybrid.yml up -d

# 4. Verify
docker ps
curl http://localhost:8000/health
```

### Server 2 (Vehicle Service)

```bash
# 1. Clone repository
git clone https://github.com/AnhDucDANG/He-thong-phan-tan.git
cd He-thong-phan-tan/vehicle-service

# 2. Follow instructions in CHANGELOG.md
# 3. Use docker-compose.server2.yml for deployment
```

**📖 Xem chi tiết:** `vehicle-service/CHANGELOG.md`

### Server 3 (Booking Service)

```bash
# 1. Clone repository
git clone https://github.com/AnhDucDANG/He-thong-phan-tan.git
cd He-thong-phan-tan/booking_service

# 2. Follow instructions in CHANGELOG.md
# 3. Use docker-compose.server3.yml for deployment
```

**📖 Xem chi tiết:** `booking_service/CHANGELOG.md`

## Testing

### Test từ Server 1
```bash
# Test API Gateway
curl http://localhost:8000/health

# Test User Service
curl http://localhost:8001/health

# Test Vehicle Service (qua Tailscale)
curl http://100.73.22.88:8002/health

# Test Booking Service (qua Tailscale)
curl http://100.65.117.32:8003/health
```

### Test từ Server 2
```bash
# Test kết nối đến Gateway
curl http://100.69.63.99:8000/health

# Test service của mình
curl http://localhost:8002/health
```

### Test từ Server 3
```bash
# Test kết nối đến Gateway
curl http://100.69.63.99:8000/health

# Test service của mình
curl http://localhost:8003/health
```

## Troubleshooting

### 1. Không kết nối được qua Tailscale
```bash
# Kiểm tra Tailscale status
tailscale status

# Ping server khác
tailscale ping 100.69.63.99

# Kiểm tra firewall
sudo ufw status
```

### 2. Service không healthy
```bash
# Xem logs
docker logs rental-api-gateway
docker logs rental-user-service

# Restart service
docker compose restart api_gateway
```

### 3. MongoDB connection issues
```bash
# Kiểm tra MongoDB cluster
docker exec -it mongos-router mongosh

# Trong mongosh:
sh.status()
db.adminCommand({ listShards: 1 })
```

## Security Notes

⚠️ **QUAN TRỌNG:**

1. **Đổi SECRET_KEY** trong file `.env`
2. **Cấu hình Tailscale ACLs** để giới hạn truy cập
3. **Backup MongoDB** thường xuyên
4. **Monitor logs** để phát hiện vấn đề sớm

## Directory Structure

```
He-thong-phan-tan/
├── .env.server1.example          # Template cho Server 1
├── docker-compose.sharded-hybrid.yml  # Docker compose cho Server 1
├── DEPLOYMENT.md                 # File này
├── api_gateway/                  # API Gateway service
├── user_service/                 # User service
├── booking_service/              
│   ├── CHANGELOG.md             # Hướng dẫn deploy Server 3
│   └── docker-compose.server3.yml
└── vehicle-service/
    ├── CHANGELOG.md             # Hướng dẫn deploy Server 2
    └── docker-compose.server2.yml
```

## Support

Nếu gặp vấn đề, tham khảo:
- `booking_service/CHANGELOG.md` - Chi tiết cho Server 3
- `vehicle-service/CHANGELOG.md` - Chi tiết cho Server 2
- GitHub Issues: https://github.com/AnhDucDANG/He-thong-phan-tan/issues
