import os

class Settings:
    # Gateway config
    GATEWAY_HOST = os.getenv("GATEWAY_HOST", "0.0.0.0")
    GATEWAY_PORT = int(os.getenv("GATEWAY_PORT", "8000"))
    
    # Service URLs - ĐỌC TỪ .env
    USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user_service:8001")
    VEHICLE_SERVICE_URL = os.getenv("VEHICLE_SERVICE_URL", "http://localhost:8002")
    BOOKING_SERVICE_URL = os.getenv("BOOKING_SERVICE_URL", "http://localhost:8003")
    PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://localhost:8004")
    
    # Timeout (tăng lên vì kết nối qua Tailscale có thể chậm hơn)
    REQUEST_TIMEOUT = 120  # 2 minutes
    
    # Service mapping
    SERVICE_MAP = {
        "users": USER_SERVICE_URL,
        "vehicles": VEHICLE_SERVICE_URL,
        "bookings": BOOKING_SERVICE_URL,
        "payments": PAYMENT_SERVICE_URL,
    }
    
    # Health check endpoints
    HEALTH_CHECK_ENDPOINTS = {
        "users": f"{USER_SERVICE_URL}/health",
        "vehicles": f"{VEHICLE_SERVICE_URL}/health",
        "bookings": f"{BOOKING_SERVICE_URL}/health",
        "payments": f"{PAYMENT_SERVICE_URL}/health",
    }

settings = Settings()