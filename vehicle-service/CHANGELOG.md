# CHANGELOG - Vehicle Service

## [2025-11-27] - Tailscale Distributed Deployment Setup

### 🌐 Distributed Architecture

Vehicle Service được thiết kế để deploy riêng biệt trên Server 2, kết nối với API Gateway qua Tailscale VPN.

#### Architecture Overview
```
Server 1 (100.69.63.99):
├─> API Gateway (:8000)
├─> User Service (:8001)
└─> MongoDB Cluster (:27017)

Server 2 (100.73.22.88):  ← VEHICLE SERVICE HERE
└─> Vehicle Service (:8002)

Server 3 (100.65.117.32):
└─> Booking Service (:8003)
```

### 📝 Tailscale Deployment Guide

#### Prerequisites
1. Install Tailscale trên Server 2:
   ```bash
   curl -fsSL https://tailscale.com/install.sh | sh
   tailscale up
   ```

2. Lấy Tailscale IP:
   ```bash
   tailscale ip -4
   # Output: 100.73.22.88 (ví dụ)
   ```

#### Environment Configuration

Tạo file `.env` trong thư mục `vehicle-service/`:

```env
# MongoDB Connection (qua Tailscale đến Server 1)
MONGO_URI=mongodb://100.69.63.99:27017/rental

# Service Configuration
PORT=8002

# API Gateway Connection (Tailscale IP của Server 1)
API_GATEWAY_URL=http://100.69.63.99:8000

# Backup Direct Service URL (không dùng nếu có API_GATEWAY_URL)
USER_SERVICE_URL=http://100.69.63.99:8001
```

#### Docker Compose for Server 2

Tạo file `docker-compose.server2.yml`:

```yaml
version: '3.8'

services:
  vehicle_service:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: vehicle-service-server2
    restart: unless-stopped
    network_mode: host  # Dùng host network để expose ra Tailscale IP
    environment:
      - MONGO_URI=mongodb://100.69.63.99:27017/rental
      - PORT=8002
      - API_GATEWAY_URL=http://100.69.63.99:8000
      - USER_SERVICE_URL=http://100.69.63.99:8001
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8002/health || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 20s
```

#### Deployment Steps

1. **Clone repository trên Server 2:**
   ```bash
   cd /opt
   git clone https://github.com/AnhDucDANG/He-thong-phan-tan.git
   cd He-thong-phan-tan/vehicle-service
   ```

2. **Tạo file .env với Tailscale IPs:**
   ```bash
   nano .env  # Cập nhật các Tailscale IPs như trên
   ```

3. **Build và start service:**
   ```bash
   docker compose -f docker-compose.server2.yml up -d --build
   ```

4. **Verify connectivity:**
   ```bash
   # Test MongoDB connection
   docker logs vehicle-service-server2
   
   # Test API Gateway connection
   curl http://100.69.63.99:8000/health
   
   # Test vehicle service health
   curl http://localhost:8002/health
   
   # Test get vehicles
   curl http://localhost:8002/api/vehicles
   ```

### 🔧 Configuration Changes

#### Inter-Service Communication
- **Updated**: `src/services/userService.js` - Gọi User Service qua API Gateway
- **Old**: Direct call to `USER_SERVICE_URL`
- **New**: Call via `API_GATEWAY_URL/api/users/{id}`

```javascript
// Before
const url = `${process.env.USER_SERVICE_URL}/${ownerId}`;

// After
const gatewayUrl = process.env.API_GATEWAY_URL || process.env.USER_SERVICE_URL;
const url = gatewayUrl.includes('/api/users') 
  ? `${gatewayUrl}/${ownerId}`
  : `${gatewayUrl}/api/users/${ownerId}`;
```

#### Routing Pattern
- Vehicle Service routes: `/api/vehicles/*`
- API Gateway forwards: `GET /api/vehicles/{id}` → `http://100.73.22.88:8002/api/vehicles/{id}`

#### Security Considerations
1. **Tailscale ACLs**: Cấu hình access control
   ```json
   {
     "acls": [
       {
         "action": "accept",
         "src": ["100.73.22.88"],
         "dst": ["100.69.63.99:8000", "100.69.63.99:27017"]
       },
       {
         "action": "accept",
         "src": ["100.69.63.99"],
         "dst": ["100.73.22.88:8002"]
       }
     ]
   }
   ```

2. **MongoDB Security**: Bind MongoDB trên Server 1 để accept Tailscale connections
   ```yaml
   # Server 1 - docker-compose
   mongos:
     command: mongos --configdb configReplSet/mongo-config:27019 --port 27017 --bind_ip_all
   ```

3. **Node.js Process**: Bind to all interfaces
   ```javascript
   app.listen(PORT, '0.0.0.0', () => {
     console.log(`Vehicle Service running on port ${PORT}`);
   });
   ```

### 📊 Monitoring & Troubleshooting

#### Health Checks
```bash
# Vehicle Service
curl http://100.73.22.88:8002/health

# Qua API Gateway (từ client)
curl http://100.69.63.99:8000/api/vehicles

# Check specific vehicle
curl http://100.69.63.99:8000/api/vehicles/{vehicle_id}
```

#### Common Issues

**Issue 1: Cannot connect to MongoDB**
```bash
# Test connectivity từ Server 2
ping 100.69.63.99
nc -zv 100.69.63.99 27017

# Test từ container
docker exec vehicle-service-server2 nc -zv 100.69.63.99 27017
```

**Issue 2: Gateway cannot reach Vehicle Service**
```bash
# Test từ Server 1 (Gateway)
curl http://100.73.22.88:8002/health

# Check if port is open
nmap -p 8002 100.73.22.88
```

**Issue 3: User validation fails**
```bash
# Check logs
docker logs vehicle-service-server2 | grep "User Service"

# Manual test User Service call
curl http://100.69.63.99:8000/api/users/{user_id}
```

### 🚀 Performance Optimization

1. **Enable Tailscale Direct Connections:**
   ```bash
   tailscale up --accept-routes --advertise-routes=100.73.22.88/32
   ```

2. **MongoDB Connection Pooling:**
   ```javascript
   // In src/config/database.js
   mongoose.connect(MONGO_URI, {
     maxPoolSize: 50,
     minPoolSize: 10,
     serverSelectionTimeoutMS: 5000,
   });
   ```

3. **Axios Timeout Configuration:**
   ```javascript
   // In src/services/userService.js
   axios.get(url, { timeout: 5000 });
   ```

### 🔄 API Gateway Integration

#### Server 1 - API Gateway Configuration

Update `docker-compose.sharded-hybrid.yml` trên Server 1:

```yaml
api_gateway:
  environment:
    - VEHICLE_SERVICE_URL=http://100.73.22.88:8002
    - BOOKING_SERVICE_URL=http://100.65.117.32:8003
```

#### Request Flow
```
Client → API Gateway (100.69.63.99:8000)
         ↓
         /api/vehicles/{id}
         ↓
Vehicle Service (100.73.22.88:8002)
         ↓
         /api/vehicles/{id}
         ↓
MongoDB (100.69.63.99:27017)
```

### 📝 Team Member Notes

**Để deploy Vehicle Service trên server của bạn:**

1. Cài Tailscale và join vào mạng team:
   ```bash
   curl -fsSL https://tailscale.com/install.sh | sh
   tailscale up
   ```

2. Clone repo và checkout branch `lam`:
   ```bash
   git clone https://github.com/AnhDucDANG/He-thong-phan-tan.git
   cd He-thong-phan-tan/vehicle-service
   git checkout lam
   ```

3. Tạo file `.env`:
   ```bash
   nano .env
   # Paste environment variables như trên
   # Thay <YOUR_TAILSCALE_IP> bằng IP thật của server bạn
   ```

4. Build và run:
   ```bash
   docker compose -f docker-compose.server2.yml up -d --build
   ```

5. Verify deployment:
   ```bash
   # Check logs
   docker logs vehicle-service-server2
   
   # Test locally
   curl http://localhost:8002/health
   curl http://localhost:8002/api/vehicles
   
   # Test from Gateway
   curl http://100.69.63.99:8000/api/vehicles
   ```

**Để update code:**
```bash
cd /opt/He-thong-phan-tan/vehicle-service
git pull origin lam
docker compose -f docker-compose.server2.yml up -d --build
```

**Để xem logs real-time:**
```bash
docker compose -f docker-compose.server2.yml logs -f
```

**Để restart service:**
```bash
docker compose -f docker-compose.server2.yml restart
```

### 🧪 Testing Checklist

- [ ] Tailscale installed và running
- [ ] Tailscale IP đã lấy: `tailscale ip -4`
- [ ] MongoDB connection test: `nc -zv 100.69.63.99 27017`
- [ ] Service health check: `curl http://localhost:8002/health`
- [ ] Get vehicles: `curl http://localhost:8002/api/vehicles`
- [ ] Create vehicle test qua Postman
- [ ] Gateway can reach service: `curl http://100.69.63.99:8000/api/vehicles`
- [ ] User validation works: Check logs khi tạo vehicle với owner_id

---

## [2025-11-26] - Integration into Hybrid Sharded Cluster

### Added
- **Merged from duc branch**: Toàn bộ Vehicle Service được merge từ nhánh duc vào nhánh lam
  - 13 files total
  - Node.js + Express implementation
  - MongoDB Mongoose integration

### Integration Details
- **Docker Compose**: Thêm service definition vào `docker-compose.sharded-hybrid.yml`
  - Container name: `rental-vehicle-service`
  - Port: 8002
  - Image: Node.js 20-alpine
  - Network: rental-network

- **MongoDB Connection**:
  - URI: `mongodb://mongos:27017/rental`
  - Connects to hybrid sharded cluster
  - Collection: `vehicles` (shard key: location-based)

### API Endpoints
- **Base URL**: http://vehicle_service:8002/api/vehicles
- **Main Endpoints**:
  - `GET /api/vehicles` - List all vehicles
  - `GET /api/vehicles/:id` - Get vehicle by ID
  - `POST /api/vehicles` - Create new vehicle
  - `PUT /api/vehicles/:id` - Update vehicle
  - `DELETE /api/vehicles/:id` - Soft delete vehicle
  - `GET /health` - Health check

### Response Format
Vehicle Service trả về dữ liệu với **camelCase naming convention**:
```json
{
  "_id": "ObjectId",
  "make": "Toyota",
  "model": "Camry",
  "year": 2024,
  "licensePlate": "30A-12345",
  "dailyRate": 500000,
  "location": "HANOI",
  "status": "available",
  "isDeleted": false,
  "bookingRecords": [],
  "createdAt": "2025-11-26T10:00:00.000Z",
  "updatedAt": "2025-11-26T10:00:00.000Z"
}
```

### Key Fields
- **dailyRate** (camelCase): Giá thuê theo ngày (VND)
- **status**: Enum - `"available"`, `"on_rent"`, `"maintenance"`
- **isDeleted**: Boolean - Soft delete flag
- **location**: Enum - `"HANOI"`, `"HOCHIMINH"`, `"DANANG"`
- **bookingRecords**: Array - Lịch sử đặt xe

### Integration with Booking Service
- **URL**: Booking Service gọi qua `http://vehicle_service:8002`
- **Environment Variable**: `VEHICLE_SERVICE_URL=http://vehicle_service:8002`
- **Used By**:
  - Booking Service để check availability
  - Booking Service để cập nhật status khi booking
  - API Gateway để forward requests

### Technical Stack
- **Runtime**: Node.js 20-alpine
- **Framework**: Express 5.1.0
- **ODM**: Mongoose 8.19.2
- **HTTP Client**: Axios (for calling User Service)
- **Port**: 8002

### File Structure
```
vehicle-service/
├── server.js                    # Entry point
├── package.json                 # Dependencies
├── Dockerfile                   # Container definition
└── src/
    ├── config/
    │   └── database.js          # MongoDB connection
    ├── models/
    │   └── Vehicle.js           # Mongoose schema
    ├── controllers/
    │   └── vehicleController.js # Business logic
    ├── routes/
    │   └── vehicleRoutes.js     # Express routes
    └── services/
        └── userService.js       # User verification
```

### Dependencies
- express: ^5.1.0
- mongoose: ^8.19.2
- axios: ^1.7.9
- dotenv: ^16.4.7

### Environment Variables
```env
MONGO_URI=mongodb://mongos:27017/rental
PORT=8002
USER_SERVICE_URL=http://user_service:8001
```

### Health Check
- Endpoint: `GET /health`
- Expected Response: `{ status: "OK", service: "Vehicle Service" }`
- Status Code: 200

### Git Integration
- **Source Branch**: duc
- **Target Branch**: lam
- **Merge Commits**:
  - e533391: "Merge origin/duc - Add vehicle service from Duc's branch"
  - 8ce2a5a: "Integrate vehicle service from duc branch into hybrid sharded cluster"

### Docker Build
```bash
# Build image
docker compose -f docker-compose.sharded-hybrid.yml build vehicle_service

# Start service
docker compose -f docker-compose.sharded-hybrid.yml up -d vehicle_service
```

### Testing
- ✅ Service starts successfully on port 8002
- ✅ Connects to MongoDB sharded cluster
- ✅ Health endpoint returns 200 OK
- ✅ GET /api/vehicles returns vehicle list
- ✅ Integration with Booking Service successful

### Known Issues
- ⚠️ Healthcheck trong docker-compose shows unhealthy (curl not installed in alpine)
  - Non-blocking issue
  - Service vẫn hoạt động bình thường
  - Có thể fix bằng cách add curl vào Dockerfile hoặc dùng node-based healthcheck

### Naming Convention
**IMPORTANT**: Vehicle Service sử dụng **camelCase** (JavaScript/Node.js convention)
- Các service Python phải adapt khi consume API này
- Ví dụ: `dailyRate` (NOT `daily_rate`), `licensePlate` (NOT `license_plate`)

### Notes
- Service được merge từ nhánh duc của team member
- Fully compatible với hybrid sharded MongoDB cluster
- Tích hợp hoàn chỉnh với Booking Service và API Gateway
- Sử dụng Mongoose ODM thay vì MongoDB native driver

### Added
- **Merged from duc branch**: Toàn bộ Vehicle Service được merge từ nhánh duc vào nhánh lam
  - 13 files total
  - Node.js + Express implementation
  - MongoDB Mongoose integration

### Integration Details
- **Docker Compose**: Thêm service definition vào `docker-compose.sharded-hybrid.yml`
  - Container name: `rental-vehicle-service`
  - Port: 8002
  - Image: Node.js 20-alpine
  - Network: rental-network

- **MongoDB Connection**:
  - URI: `mongodb://mongos:27017/rental`
  - Connects to hybrid sharded cluster
  - Collection: `vehicles` (shard key: location-based)

### API Endpoints
- **Base URL**: http://vehicle_service:8002/api/vehicles
- **Main Endpoints**:
  - `GET /api/vehicles` - List all vehicles
  - `GET /api/vehicles/:id` - Get vehicle by ID
  - `POST /api/vehicles` - Create new vehicle
  - `PUT /api/vehicles/:id` - Update vehicle
  - `DELETE /api/vehicles/:id` - Soft delete vehicle
  - `GET /health` - Health check

### Response Format
Vehicle Service trả về dữ liệu với **camelCase naming convention**:
```json
{
  "_id": "ObjectId",
  "make": "Toyota",
  "model": "Camry",
  "year": 2024,
  "licensePlate": "30A-12345",
  "dailyRate": 500000,
  "location": "HANOI",
  "status": "available",
  "isDeleted": false,
  "bookingRecords": [],
  "createdAt": "2025-11-26T10:00:00.000Z",
  "updatedAt": "2025-11-26T10:00:00.000Z"
}
```

### Key Fields
- **dailyRate** (camelCase): Giá thuê theo ngày (VND)
- **status**: Enum - `"available"`, `"on_rent"`, `"maintenance"`
- **isDeleted**: Boolean - Soft delete flag
- **location**: Enum - `"HANOI"`, `"HOCHIMINH"`, `"DANANG"`
- **bookingRecords**: Array - Lịch sử đặt xe

### Integration with Booking Service
- **URL**: Booking Service gọi qua `http://vehicle_service:8002`
- **Environment Variable**: `VEHICLE_SERVICE_URL=http://vehicle_service:8002`
- **Used By**:
  - Booking Service để check availability
  - Booking Service để cập nhật status khi booking
  - API Gateway để forward requests

### Technical Stack
- **Runtime**: Node.js 20-alpine
- **Framework**: Express 5.1.0
- **ODM**: Mongoose 8.19.2
- **HTTP Client**: Axios (for calling User Service)
- **Port**: 8002

### File Structure
```
vehicle-service/
├── server.js                    # Entry point
├── package.json                 # Dependencies
├── Dockerfile                   # Container definition
└── src/
    ├── config/
    │   └── database.js          # MongoDB connection
    ├── models/
    │   └── Vehicle.js           # Mongoose schema
    ├── controllers/
    │   └── vehicleController.js # Business logic
    ├── routes/
    │   └── vehicleRoutes.js     # Express routes
    └── services/
        └── userService.js       # User verification
```

### Dependencies
- express: ^5.1.0
- mongoose: ^8.19.2
- axios: ^1.7.9
- dotenv: ^16.4.7

### Environment Variables
```env
MONGO_URI=mongodb://mongos:27017/rental
PORT=8002
USER_SERVICE_URL=http://user_service:8001
```

### Health Check
- Endpoint: `GET /health`
- Expected Response: `{ status: "OK", service: "Vehicle Service" }`
- Status Code: 200

### Git Integration
- **Source Branch**: duc
- **Target Branch**: lam
- **Merge Commits**:
  - e533391: "Merge origin/duc - Add vehicle service from Duc's branch"
  - 8ce2a5a: "Integrate vehicle service from duc branch into hybrid sharded cluster"

### Docker Build
```bash
# Build image
docker compose -f docker-compose.sharded-hybrid.yml build vehicle_service

# Start service
docker compose -f docker-compose.sharded-hybrid.yml up -d vehicle_service
```

### Testing
- ✅ Service starts successfully on port 8002
- ✅ Connects to MongoDB sharded cluster
- ✅ Health endpoint returns 200 OK
- ✅ GET /api/vehicles returns vehicle list
- ✅ Integration with Booking Service successful

### Known Issues
- ⚠️ Healthcheck trong docker-compose shows unhealthy (curl not installed in alpine)
  - Non-blocking issue
  - Service vẫn hoạt động bình thường
  - Có thể fix bằng cách add curl vào Dockerfile hoặc dùng node-based healthcheck

### Naming Convention
**IMPORTANT**: Vehicle Service sử dụng **camelCase** (JavaScript/Node.js convention)
- Các service Python phải adapt khi consume API này
- Ví dụ: `dailyRate` (NOT `daily_rate`), `licensePlate` (NOT `license_plate`)

### Notes
- Service được merge từ nhánh duc của team member
- Fully compatible với hybrid sharded MongoDB cluster
- Tích hợp hoàn chỉnh với Booking Service và API Gateway
- Sử dụng Mongoose ODM thay vì MongoDB native driver
