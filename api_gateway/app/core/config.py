import os

class Settings:
    GATEWAY_HOST = os.getenv("GATEWAY_HOST", "0.0.0.0")
    GATEWAY_PORT = int(os.getenv("GATEWAY_PORT", "8000"))
    
    USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user_service:8001")
    VEHICLE_SERVICE_URL = os.getenv("VEHICLE_SERVICE_URL", "http://vehicle_service:8002")
    BOOKING_SERVICE_URL = os.getenv("BOOKING_SERVICE_URL", "http://booking_service:8003")
    PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://payment_service:8004")

    REQUEST_TIMEOUT = 120

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