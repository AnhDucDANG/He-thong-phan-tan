# CHANGELOG - Booking Service

## [2025-11-27] - Tailscale Distributed Deployment Setup

### 🌐 Distributed Architecture

Booking Service được thiết kế để deploy riêng biệt trên Server 3, kết nối với API Gateway qua Tailscale VPN.

#### Architecture Overview
```
Server 1 (100.69.63.99):
├─> API Gateway (:8000)
├─> User Service (:8001)
└─> MongoDB Cluster (:27017)

Server 2 (100.73.22.88):
└─> Vehicle Service (:8002)

Server 3 (100.65.117.32):  ← BOOKING SERVICE HERE
└─> Booking Service (:8003)
```

### 📝 Tailscale Deployment Guide

#### Prerequisites
1. Install Tailscale trên Server 3:
   ```bash
   curl -fsSL https://tailscale.com/install.sh | sh
   tailscale up
   ```

2. Lấy Tailscale IP:
   ```bash
   tailscale ip -4
   # Output: 100.65.117.32 (ví dụ)
   ```

#### Environment Configuration

Tạo file `.env` trong thư mục `booking_service/`:

```env
# MongoDB Connection (qua Tailscale đến Server 1)
MONGO_URL=mongodb://100.69.63.99:27017
MONGO_DB=rental

# Service Configuration
SERVICE_HOST=0.0.0.0
SERVICE_PORT=8003

# API Gateway Connection (Tailscale IP của Server 1)
API_GATEWAY_URL=http://100.69.63.99:8000

# Backup Direct Service URLs (không dùng nếu có API_GATEWAY_URL)
USER_SERVICE_URL=http://100.69.63.99:8001
VEHICLE_SERVICE_URL=http://100.73.22.88:8002
PAYMENT_SERVICE_URL=http://100.108.163.69:8004

# JWT Configuration
SECRET_KEY=35a91c468c0a8a62d3669ba143ddf1db
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

#### Docker Compose for Server 3

Tạo file `docker-compose.server3.yml`:

```yaml
version: '3.8'

services:
  booking_service:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: booking-service-server3
    restart: unless-stopped
    network_mode: host  # Dùng host network để expose ra Tailscale IP
    environment:
      - MONGO_URL=mongodb://100.69.63.99:27017
      - MONGO_DB=rental
      - SERVICE_HOST=0.0.0.0
      - SERVICE_PORT=8003
      - API_GATEWAY_URL=http://100.69.63.99:8000
      - USER_SERVICE_URL=http://100.69.63.99:8001
      - VEHICLE_SERVICE_URL=http://100.73.22.88:8002
      - PAYMENT_SERVICE_URL=http://100.108.163.69:8004
      - SECRET_KEY=${SECRET_KEY}
      - ALGORITHM=${ALGORITHM}
      - ACCESS_TOKEN_EXPIRE_MINUTES=${ACCESS_TOKEN_EXPIRE_MINUTES}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8003/health"]
      interval: 10s
      timeout: 5s
      retries: 5
```

#### Deployment Steps

1. **Clone repository trên Server 3:**
   ```bash
   cd /opt
   git clone https://github.com/AnhDucDANG/He-thong-phan-tan.git
   cd He-thong-phan-tan/booking_service
   ```

2. **Tạo file .env với Tailscale IPs:**
   ```bash
   cp .env.example .env
   nano .env  # Cập nhật các Tailscale IPs
   ```

3. **Build và start service:**
   ```bash
   docker compose -f docker-compose.server3.yml up -d --build
   ```

4. **Verify connectivity:**
   ```bash
   # Test MongoDB connection
   docker logs booking-service-server3
   
   # Test API Gateway connection
   curl http://100.69.63.99:8000/health
   
   # Test booking service health
   curl http://localhost:8003/health
   ```

### 🔧 Configuration Changes

#### Inter-Service Communication
- **Routing**: Tất cả requests từ Booking Service đến các services khác đều qua API Gateway
- **Path Pattern**: `/api/{service}/{path}`
  - User Service: `/api/users/*`
  - Vehicle Service: `/api/vehicles/*`
  - Payment Service: `/api/payments/*`

#### Security Considerations
1. **Tailscale ACLs**: Cấu hình access control trong Tailscale admin
   ```json
   {
     "acls": [
       {
         "action": "accept",
         "src": ["100.65.117.32"],
         "dst": ["100.69.63.99:8000", "100.69.63.99:27017"]
       }
     ]
   }
   ```

2. **MongoDB Security**: Nếu cần authentication:
   ```env
   MONGO_URL=mongodb://username:password@100.69.63.99:27017
   ```

3. **Firewall Rules**: MongoDB port 27017 chỉ accept từ Tailscale IPs

### 📊 Monitoring & Troubleshooting

#### Health Checks
```bash
# Booking Service
curl http://100.65.117.32:8003/health

# Qua API Gateway (từ client)
curl http://100.69.63.99:8000/api/bookings/health
```

#### Common Issues

**Issue 1: Cannot connect to MongoDB**
```bash
# Test từ container
docker exec booking-service-server3 ping 100.69.63.99

# Check MongoDB logs trên Server 1
docker logs mongo-config-server
```

**Issue 2: API Gateway timeout**
```bash
# Increase timeout in docker-compose
environment:
  - HTTP_TIMEOUT=60
```

**Issue 3: Slow inter-service calls**
```bash
# Check Tailscale direct connection
tailscale ping 100.69.63.99

# If relay connection, enable direct path
tailscale up --accept-routes
```

### 🚀 Performance Optimization

1. **Enable Tailscale Direct Connections:**
   ```bash
   tailscale up --accept-routes --advertise-routes=100.65.117.32/32
   ```

2. **MongoDB Connection Pooling:**
   ```python
   # Already configured in app/database/connection.py
   maxPoolSize=50
   minPoolSize=10
   ```

3. **HTTP Client Timeout:**
   ```python
   # In app/routes/http_client.py
   timeout = httpx.Timeout(10.0, connect=5.0)
   ```

### 📝 Team Member Notes

**Để deploy Booking Service trên server của bạn:**

1. Cài Tailscale và join vào mạng team
2. Clone repo và checkout branch `lam`
3. Copy file `.env` và thay Tailscale IPs
4. Run: `docker compose -f docker-compose.server3.yml up -d`
5. Verify: Service accessible tại `http://<your-tailscale-ip>:8003`

**Để update code:**
```bash
git pull origin lam
docker compose -f docker-compose.server3.yml up -d --build
```

**Để xem logs:**
```bash
docker compose -f docker-compose.server3.yml logs -f
```

---

## [2025-11-26] - Integration with Vehicle Service

### Fixed
- **Field Name Mismatch**: Cập nhật để đọc đúng field `dailyRate` (camelCase) từ Vehicle Service thay vì `daily_rate` (snake_case)
  - File: `app/routes/booking_routes.py` - Line 24
  - File: `app/services/booking_service.py` - Line 15

- **Database Model Mismatch**: Sửa lỗi lưu sai field vào MongoDB
  - File: `app/database/crud.py`
  - **Problem**: Function `create_booking_transaction` cố lưu các field không tồn tại trong model:
    - `total_amount` (không có trong model)
    - `dropoff_location` (không có trong model)
    - `payment_status` (không có trong model)
  - **Solution**: Cập nhật function signature và logic để lưu đúng các field:
    - `book_price` (tổng giá trị booking)
    - `daily_rate` (giá thuê theo ngày)
    - `total_days` (số ngày thuê)
  - **Change**: Signature từ `create_booking_transaction(booking_data, total_amount)` thành `create_booking_transaction(booking_data, book_price, daily_rate, total_days)`

### Changed
- **API Endpoint Updates**: Cập nhật endpoint gọi Vehicle Service
  - File: `app/services/car_service.py`
  - Từ: `/api/v1/cars/{car_id}/availability`
  - Thành: `/api/vehicles/{car_id}`
  - Cập nhật logic check availability: kiểm tra `status == "available"` và `isDeleted == false`

- **Response Field Mapping**: Xử lý response từ Vehicle Service với đúng structure
  - Đọc field `dailyRate` thay vì `daily_rate`
  - Đọc field `status` và `isDeleted` thay vì `is_available`

### Technical Details
- **Root Cause 1**: Node.js (Vehicle Service) sử dụng camelCase, Python (Booking Service) ban đầu expect snake_case
- **Root Cause 2**: Function CRUD không khớp với Beanie Document model definition
- **Impact**: Gây lỗi 500 Internal Server Error khi tạo booking
- **Resolution**: 
  1. Cập nhật field name extraction trong booking_routes.py
  2. Refactor create_booking_transaction để nhận và lưu đúng fields
  3. Rebuild Docker container với code mới

### Integration
- **Vehicle Service**: http://vehicle_service:8002
- **API Used**: GET `/api/vehicles/{car_id}` 
- **Response Format**:
  ```json
  {
    "_id": "ObjectId",
    "dailyRate": 500000,
    "status": "available",
    "isDeleted": false,
    ...
  }
  ```

### Testing
- ✅ User verification endpoint: 200 OK
- ✅ Vehicle service call: 200 OK
- ✅ Booking creation: 201 Created (after fixes)
- ✅ All database fields saved correctly

### Notes
- Booking Service giờ đã tương thích hoàn toàn với Vehicle Service từ nhánh duc
- Các field trong model Booking phải khớp chính xác với những gì được lưu vào database
- Luôn kiểm tra response structure của external service khi integrate

### Fixed
- **Field Name Mismatch**: Cập nhật để đọc đúng field `dailyRate` (camelCase) từ Vehicle Service thay vì `daily_rate` (snake_case)
  - File: `app/routes/booking_routes.py` - Line 24
  - File: `app/services/booking_service.py` - Line 15

- **Database Model Mismatch**: Sửa lỗi lưu sai field vào MongoDB
  - File: `app/database/crud.py`
  - **Problem**: Function `create_booking_transaction` cố lưu các field không tồn tại trong model:
    - `total_amount` (không có trong model)
    - `dropoff_location` (không có trong model)
    - `payment_status` (không có trong model)
  - **Solution**: Cập nhật function signature và logic để lưu đúng các field:
    - `book_price` (tổng giá trị booking)
    - `daily_rate` (giá thuê theo ngày)
    - `total_days` (số ngày thuê)
  - **Change**: Signature từ `create_booking_transaction(booking_data, total_amount)` thành `create_booking_transaction(booking_data, book_price, daily_rate, total_days)`

### Changed
- **API Endpoint Updates**: Cập nhật endpoint gọi Vehicle Service
  - File: `app/services/car_service.py`
  - Từ: `/api/v1/cars/{car_id}/availability`
  - Thành: `/api/vehicles/{car_id}`
  - Cập nhật logic check availability: kiểm tra `status == "available"` và `isDeleted == false`

- **Response Field Mapping**: Xử lý response từ Vehicle Service với đúng structure
  - Đọc field `dailyRate` thay vì `daily_rate`
  - Đọc field `status` và `isDeleted` thay vì `is_available`

### Technical Details
- **Root Cause 1**: Node.js (Vehicle Service) sử dụng camelCase, Python (Booking Service) ban đầu expect snake_case
- **Root Cause 2**: Function CRUD không khớp với Beanie Document model definition
- **Impact**: Gây lỗi 500 Internal Server Error khi tạo booking
- **Resolution**: 
  1. Cập nhật field name extraction trong booking_routes.py
  2. Refactor create_booking_transaction để nhận và lưu đúng fields
  3. Rebuild Docker container với code mới

### Integration
- **Vehicle Service**: http://vehicle_service:8002
- **API Used**: GET `/api/vehicles/{car_id}` 
- **Response Format**:
  ```json
  {
    "_id": "ObjectId",
    "dailyRate": 500000,
    "status": "available",
    "isDeleted": false,
    ...
  }
  ```

### Testing
- ✅ User verification endpoint: 200 OK
- ✅ Vehicle service call: 200 OK
- ✅ Booking creation: 201 Created (after fixes)
- ✅ All database fields saved correctly

### Notes
- Booking Service giờ đã tương thích hoàn toàn với Vehicle Service từ nhánh duc
- Các field trong model Booking phải khớp chính xác với những gì được lưu vào database
- Luôn kiểm tra response structure của external service khi integrate
