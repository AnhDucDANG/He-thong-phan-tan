from decouple import config

class Settings:
    # API Gateway
    GATEWAY_HOST = config("GATEWAY_HOST", default="0.0.0.0")
    GATEWAY_PORT = int(config("GATEWAY_PORT", default=8000))
    
    # Service URLs - Dùng tên container khi chạy trong Docker
    USER_SERVICE_URL = config("USER_SERVICE_URL", default="http://localhost:8001")
    VEHICLE_SERVICE_URL = config("VEHICLE_SERVICE_URL", default="http://localhost:8002")
    BOOKING_SERVICE_URL = config("BOOKING_SERVICE_URL", default="http://localhost:8003")
    PAYMENT_SERVICE_URL = config("PAYMENT_SERVICE_URL", default="http://localhost:8004")
    
    # Timeout settings
    REQUEST_TIMEOUT = 30
    
    # Service mapping
    SERVICE_MAP = {
        "users": USER_SERVICE_URL,
        "vehicles": VEHICLE_SERVICE_URL,
        "bookings": BOOKING_SERVICE_URL,
        "payments": PAYMENT_SERVICE_URL,
    }

settings = Settings()