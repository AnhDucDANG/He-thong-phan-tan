# CHANGELOG - Vehicle Service

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
