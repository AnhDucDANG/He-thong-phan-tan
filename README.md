# 🚗 Hệ Thống Quản Lý Cho Thuê Xe - Kiến Trúc Phân Tán

## 📖 Mô tả

Hệ thống quản lý cho thuê xe được xây dựng theo kiến trúc **Microservices phân tán** với **MongoDB Hybrid Sharding**, kết hợp:
- 🏛️ **Vertical Sharding** (Functional): Tách biệt domain theo chức năng
- 🌍 **Horizontal Sharding** (Geographic): Phân tán dữ liệu theo địa lý cho Booking Service
- 🔗 **Tailscale VPN**: Kết nối an toàn giữa các services trên nhiều máy

### 🎯 Đặc điểm nổi bật

- **7 MongoDB Shards**: 4 vertical (Users, Vehicles, Payments, Config) + 3 horizontal (Bookings North/South/Central)
- **3 Geographic Zones**: Miền Bắc (Hanoi), Miền Nam (HCM), Miền Trung (Danang)
- **Transparent Sharding**: Services kết nối qua Mongos Router, không cần biết về sharding
- **Ready to Scale**: Kiến trúc sẵn sàng scale từ 1 server lên nhiều servers theo địa lý

## 🏗️ Kiến trúc hệ thống

### 🌐 Hybrid Sharding Architecture

Hệ thống sử dụng **MongoDB Hybrid Sharding** kết hợp 2 chiến lược:

#### 1️⃣ Vertical Sharding (Functional)
Tách biệt collections theo domain/chức năng:
- **Shard 1** (port 27021): `users` collection
- **Shard 2** (port 27022): `vehicles` collection  
- **Shard 4** (port 27024): `payments` collection

#### 2️⃣ Horizontal Sharding (Geographic)
Phân tán `bookings` collection theo 3 vùng địa lý:
- **Shard 3A** (port 27025): Bookings **Miền Bắc** (Hanoi, Hai Phong, Quang Ninh)
- **Shard 3B** (port 27026): Bookings **Miền Nam** (HCM, Vung Tau, Can Tho)
- **Shard 3C** (port 27027): Bookings **Miền Trung** (Da Nang, Hue, Nha Trang)

**Shard Key**: `{ pickup_location: 1, _id: 1 }` - MongoDB tự động route dựa trên địa điểm pickup

### 📊 Sơ đồ kiến trúc phân tán

```
┌────────────────────────────────────────────────────────────────────┐
│              Tailscale VPN Network (100.x.x.x)                     │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  SERVER 1 (100.69.63.99) - Gateway & Database Cluster        │ │
│  ├──────────────────────────────────────────────────────────────┤ │
│  │                                                               │ │
│  │  🚀 MICROSERVICES LAYER                                      │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │ │
│  │  │ API Gateway │→ │ User Service│→ │   Booking   │         │ │
│  │  │   :8000     │  │   :8001     │  │   Service   │         │ │
│  │  └─────────────┘  └─────────────┘  └──────┬──────┘         │ │
│  │                                            │                 │ │
│  │  ─────────────────────────────────────────┼──────────────── │ │
│  │                                            │                 │ │
│  │  💾 DATABASE LAYER - HYBRID SHARDING      │                 │ │
│  │                                            ▼                 │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │         Mongos Router (:27017)                       │  │ │
│  │  │   ↓ Query Routing & Load Balancing ↓                │  │ │
│  │  └──┬─────────────────────┬─────────────────────────┬──┘  │ │
│  │     │                     │                         │      │ │
│  │     ▼                     ▼                         ▼      │ │
│  │  ┌────────────┐    ┌──────────────┐    ┌────────────┐    │ │
│  │  │ VERTICAL   │    │  HORIZONTAL  │    │ VERTICAL   │    │ │
│  │  │ SHARDING   │    │  SHARDING    │    │ SHARDING   │    │ │
│  │  ├────────────┤    ├──────────────┤    ├────────────┤    │ │
│  │  │ Shard 1    │    │ Shard 3A 🌏  │    │ Shard 4    │    │ │
│  │  │ Users      │    │ Bookings     │    │ Payments   │    │ │
│  │  │ :27021     │    │ NORTH        │    │ :27024     │    │ │
│  │  └────────────┘    │ :27025       │    └────────────┘    │ │
│  │                    ├──────────────┤                       │ │
│  │  ┌────────────┐    │ Shard 3B 🌏  │                       │ │
│  │  │ Shard 2    │    │ Bookings     │                       │ │
│  │  │ Vehicles   │    │ SOUTH        │                       │ │
│  │  │ :27022     │    │ :27026       │                       │ │
│  │  └────────────┘    ├──────────────┤                       │ │
│  │                    │ Shard 3C 🌏  │                       │ │
│  │  ┌────────────┐    │ Bookings     │                       │ │
│  │  │ Config Svr │    │ CENTRAL      │                       │ │
│  │  │ :27019     │    │ :27027       │                       │ │
│  │  └────────────┘    └──────────────┘                       │ │
│  │                                                            │ │
│  │  📈 Total: 7 Shards (1 config + 6 data shards)           │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  MEMBER 1    │  │  MEMBER 2    │  │  MEMBER 3    │       │
│  │ 100.x.x.x    │  │ 100.x.x.x    │  │ 100.x.x.x    │       │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤       │
│  │ Vehicle      │  │ Booking      │  │ Payment      │       │
│  │ Service      │  │ Service      │  │ Service      │       │
│  │ :8002        │  │ :8003        │  │ :8004        │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└────────────────────────────────────────────────────────────────┘
```

### 🔍 Query Routing Example

```javascript
// ✅ Targeted Query (Fast) - Route đến 1 shard duy nhất
db.bookings.find({ 
  pickup_location: "HANOI",        // ← Có shard key
  start_date: { $gte: "2024-01-01" }
})
// → Mongos route đến Shard 3A (NORTH) only

// ⚠️ Scatter-Gather Query (Slower) - Query tất cả shards
db.bookings.find({
  user_id: "abc123",               // ← Không có shard key
  status: "confirmed"
})
// → Mongos query Shard 3A + 3B + 3C, merge results
```

### 📦 Thành phần hệ thống

#### Server chính (100.69.63.99)
**Microservices:**
- 🚀 API Gateway (Port 8000) - Request routing & load balancing
- 👤 User Service (Port 8001) - Authentication & user management
- 📅 Booking Service (Port 8003) - Booking management (connects to sharded cluster)

**MongoDB Sharded Cluster:**
- 🔀 Mongos Router (Port 27017) - Query router cho tất cả services
- 📋 Config Server (Port 27019) - Metadata & cluster configuration
- 📦 Shard 1 (Port 27021) - Users collection (Vertical)
- 📦 Shard 2 (Port 27022) - Vehicles collection (Vertical)
- 🌏 Shard 3A (Port 27025) - Bookings North zone (Horizontal)
- 🌏 Shard 3B (Port 27026) - Bookings South zone (Horizontal)
- 🌏 Shard 3C (Port 27027) - Bookings Central zone (Horizontal)
- 📦 Shard 4 (Port 27024) - Payments collection (Vertical)

#### Team Members (Worker Nodes)
- **Member 1:** Vehicle Service (Port 8002)
- **Member 2:** Booking Service replica (Port 8003)  
- **Member 3:** Payment Service (Port 8004)

## 🚀 Hướng dẫn triển khai

### 📋 Yêu cầu hệ thống

**Hardware:**
- CPU: 4+ cores (8 cores recommended)
- RAM: 8GB minimum (16GB recommended)
- Storage: 100GB SSD (200GB recommended)
- Network: 100Mbps+ (1Gbps recommended)

**Software:**
- Docker Desktop 20.10+
- Docker Compose 2.0+
- PowerShell 5.1+ (Windows)
- Tailscale VPN client
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
git clone https://github.com/AnhDucDANG/He-thong-phan-tan.git
cd He-thong-phan-tan

# Tạo file .env
copy .env.example .env

# Cập nhật MY_TAILSCALE_IP trong .env
# MY_TAILSCALE_IP=100.69.63.99  # Thay bằng IP của bạn
```

### Bước 5: Chọn môi trường deployment

#### Option 1: Hybrid Sharding (Recommended - Thể hiện phân tán rõ nhất)
```powershell
# Start với 7 shards (4 vertical + 3 horizontal geographic)
docker-compose -f docker-compose.sharded-hybrid.yml --env-file .env up -d

# Xem logs initialization
docker-compose -f docker-compose.sharded-hybrid.yml logs -f cluster-init

# Chờ thấy: "✅ All initialization completed successfully!"
```

#### Option 2: Development Mode (All ports exposed)
```powershell
docker-compose -f docker-compose.dev.yml --env-file .env up -d
```

#### Option 3: Production Mode (Hidden ports)
```powershell
docker-compose -f docker-compose.prod.yml --env-file .env up -d
```

### Bước 6: Verify deployment

```powershell
# Kiểm tra tất cả containers
docker-compose -f docker-compose.sharded-hybrid.yml ps

# Kiểm tra cluster status
docker exec -it mongos-router mongosh --eval "sh.status()"

# Test API Gateway
curl http://localhost:8000/health

# Test User Service
curl http://localhost:8001/health
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

## 🗄️ Database Architecture

### MongoDB Hybrid Sharded Cluster

**Connection String (cho tất cả services):**
```
mongodb://mongos:27017/rental
```

**MongoDB Compass (từ bên ngoài):**
```
mongodb://100.69.63.99:27017
```

### 📊 Shard Distribution

| Shard | Port | Collection | Strategy | Zone | Shard Key |
|-------|------|-----------|----------|------|-----------|
| **Config** | 27019 | Metadata | - | - | - |
| **Shard 1** | 27021 | `users` | Vertical | ZONE_USERS | `{ _id: hashed }` |
| **Shard 2** | 27022 | `vehicles` | Vertical | ZONE_VEHICLES | `{ _id: hashed }` |
| **Shard 3A** | 27025 | `bookings` | Horizontal | ZONE_NORTH | `{ pickup_location: 1, _id: 1 }` |
| **Shard 3B** | 27026 | `bookings` | Horizontal | ZONE_SOUTH | `{ pickup_location: 1, _id: 1 }` |
| **Shard 3C** | 27027 | `bookings` | Horizontal | ZONE_CENTRAL | `{ pickup_location: 1, _id: 1 }` |
| **Shard 4** | 27024 | `payments` | Vertical | ZONE_PAYMENTS | `{ _id: hashed }` |

### 📋 Collection Schemas

#### Users Collection (Shard 1)
```javascript
{
  _id: ObjectId,
  username: String,
  email: String (unique),
  password_hash: String (bcrypt),
  role: String ("customer" | "admin"),
  full_name: String,
  phone: String,
  avatar_url: String,
  created_at: Date,
  updated_at: Date
}
```

#### Bookings Collection (Shards 3A/3B/3C - Geographic)
```javascript
{
  _id: ObjectId,
  user_id: ObjectId,
  vehicle_id: ObjectId,
  pickup_location: String,      // ← Shard Key (HANOI | HO_CHI_MINH | DA_NANG)
  dropoff_location: String,
  start_date: Date,
  end_date: Date,
  total_price: Number,
  status: String ("pending" | "confirmed" | "completed" | "cancelled"),
  created_at: Date,
  updated_at: Date
}
```

### 🌍 Geographic Zone Mapping

**ZONE_NORTH (Shard 3A):**
- HANOI, HAI_PHONG, QUANG_NINH, THAI_NGUYEN, NAM_DINH

**ZONE_SOUTH (Shard 3B):**
- HO_CHI_MINH, VUNG_TAU, CAN_THO, BIEN_HOA, MY_THO

**ZONE_CENTRAL (Shard 3C):**
- DA_NANG, HUE, NHA_TRANG, QUY_NHON, QUANG_NAM

### 🔍 Kiểm tra Cluster Status

```bash
# Kết nối mongos router
docker exec -it mongos-router mongosh

# Xem cluster status
sh.status()

# Xem shards
db.adminCommand({ listShards: 1 })

# Xem zone configuration
use config
db.tags.find({ ns: "rental.bookings" })

# Kiểm tra data distribution
use rental
db.bookings.getShardDistribution()
```

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


## 📋 Docker Compose Commands

### 🌐 Hybrid Sharding Mode (7 Shards - Recommended)

```powershell
# Start cluster
docker-compose -f docker-compose.sharded-hybrid.yml up -d

# Rebuild và start
docker-compose -f docker-compose.sharded-hybrid.yml up -d --build

# Stop
docker-compose -f docker-compose.sharded-hybrid.yml down

# Stop và xóa volumes
docker-compose -f docker-compose.sharded-hybrid.yml down -v

# Xem logs
docker-compose -f docker-compose.sharded-hybrid.yml logs -f

# Logs từng service
docker-compose -f docker-compose.sharded-hybrid.yml logs -f mongos
docker-compose -f docker-compose.sharded-hybrid.yml logs -f cluster-init

# Check status
docker-compose -f docker-compose.sharded-hybrid.yml ps
```

### 🔵 Development Mode (Expose all ports)

```powershell
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# Rebuild
docker-compose -f docker-compose.dev.yml up -d --build

# Stop
docker-compose -f docker-compose.dev.yml down

# Logs
docker-compose -f docker-compose.dev.yml logs -f
```

### 🔴 Production Mode (Hidden ports)

```powershell
# Start production environment
docker-compose -f docker-compose.prod.yml up -d

# Rebuild
docker-compose -f docker-compose.prod.yml up -d --build

# Stop
docker-compose -f docker-compose.prod.yml down

# Logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 🧹 Cleanup Commands

```powershell
# Dừng tất cả containers
docker-compose -f docker-compose.sharded-hybrid.yml down

# Xóa volumes (⚠️ mất dữ liệu)
docker-compose -f docker-compose.sharded-hybrid.yml down -v

# Xóa tất cả containers cũ
docker rm -f $(docker ps -aq)

# Xóa tất cả volumes
docker volume prune -f

# Xóa tất cả images không dùng
docker image prune -a -f
```

## 👤 Tạo Admin Account

### Qua MongoDB Compass

1. Kết nối: `mongodb://100.69.63.99:27017`
2. Chọn database: `rental`
3. Chọn collection: `users`
4. Insert document sau:

```json
{
  "username": "admin",
  "email": "admin@rental.com",
  "password_hash": "$2a$12$vyhPT8a8SOIzoI3rxH.wL.8FptFcVxYATCMIU14QXFPwE22vX4FMG",
  "role": "admin",
  "full_name": "System Administrator",
  "phone": "+84900000000",
  "address": null,
  "avatar_url": null,
  "is_email_verified": true,
  "email_verification_token": null,
  "email_verification_expires": null,
  "reset_password_token": null,
  "reset_password_expires": null,
  "created_at": { "$date": "2025-11-24T00:00:00.000Z" },
  "updated_at": { "$date": "2025-11-24T00:00:00.000Z" },
  "last_login": null,
  "is_active": true,
  "is_deleted": false
}
```

**Password mặc định:** `Admin@123`

### Qua mongosh CLI

```bash
docker exec -it mongos-router mongosh

use rental
db.users.insertOne({
  username: "admin",
  email: "admin@rental.com",
  password_hash: "$2a$12$vyhPT8a8SOIzoI3rxH.wL.8FptFcVxYATCMIU14QXFPwE22vX4FMG",
  role: "admin",
  full_name: "System Administrator",
  phone: "+84900000000",
  is_email_verified: true,
  is_active: true,
  is_deleted: false,
  created_at: new Date(),
  updated_at: new Date()
})
```

---

## 📚 Tài liệu kỹ thuật

### Architecture Deep Dive

Xem file [`HYBRID_SHARDING_DESIGN.md`](./HYBRID_SHARDING_DESIGN.md) để hiểu chi tiết về:
- Chiến lược Hybrid Sharding (Vertical + Horizontal)
- Geographic zone configuration
- Query routing optimization
- Performance comparison
- Scaling roadmap

### MongoDB Sharding Scripts

- `init-sharding/init-shards-hybrid.js` - Initialize 6 replica sets
- `init-sharding/add-shards-hybrid.js` - Add shards to cluster
- `init-sharding/setup-zones.js` - Configure geographic zones
- `init-sharding/setup-indexes-hybrid.js` - Create optimized indexes

---

## 🎯 Kết luận

Hệ thống này demonstrate **Hybrid Sharding Architecture** với:
- ✅ **Logical distribution** hoàn chỉnh trên 1 server
- ✅ **7 MongoDB shards** (4 vertical + 3 horizontal)
- ✅ **Geographic routing** cho Booking service
- ✅ **Production-ready**: Kiến trúc sẵn sàng scale lên nhiều servers

**Lợi ích:**
- 🎓 Thể hiện rõ kiến trúc phân tán trong môi trường học tập
- ⚡ Performance tốt với targeted queries (30-50% faster)
- 📈 Dễ dàng scale horizontally khi cần
- 🌍 Data locality optimization cho từng vùng địa lý