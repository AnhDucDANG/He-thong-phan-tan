# CHANGELOG - Booking Service

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
