import os
import urllib.parse
from pydantic_settings import BaseSettings

class Settings:
    # Service host/port (tương thích với .env: SERVICE_HOST, SERVICE_PORT)
    SERVICE_HOST = os.getenv("SERVICE_HOST", "0.0.0.0")
    SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8003"))

    # External / internal service URLs (ưu tiên biến môi trường, ngược lại dùng tên service trong docker)
    USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user_service:8001")
    VEHICLE_SERVICE_URL = os.getenv("VEHICLE_SERVICE_URL", "http://vehicle_service:8002")
    BOOKING_SERVICE_URL = os.getenv("BOOKING_SERVICE_URL", f"http://booking_service:{SERVICE_PORT}")
    PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://payment_service:8004")

    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "120"))

    # Auth / token config
    SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_ME")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    MONGO_URL = os.getenv("MONGO_URL")
    if not MONGO_URL:
        MONGO_USER = os.getenv("MONGO_USER", "appUser")
        MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "Lyly250502")
        MONGO_HOST = os.getenv("MONGO_HOST", "db-booking")
        MONGO_PORT = os.getenv("MONGO_PORT", "27017")
        MONGO_DB = os.getenv("MONGO_DB", "BookingCar")
        
        # Tạo URL cơ bản
        MONGO_USER_QUOTED = urllib.parse.quote_plus(MONGO_USER)
        MONGO_PASSWORD_QUOTED = urllib.parse.quote_plus(MONGO_PASSWORD)
        MONGO_URL = f"mongodb://{MONGO_USER_QUOTED}:{MONGO_PASSWORD_QUOTED}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}?authSource=admin"
    
    SERVICE_MAP = {
        "users": USER_SERVICE_URL,
        "vehicles": VEHICLE_SERVICE_URL,
        "bookings": BOOKING_SERVICE_URL,
        "payments": PAYMENT_SERVICE_URL,
    }

    HEALTH_CHECK_ENDPOINTS = {
        "users": f"{USER_SERVICE_URL}/health",
        "vehicles": f"{VEHICLE_SERVICE_URL}/health",
        "bookings": f"{BOOKING_SERVICE_URL}/health",
        "payments": f"{PAYMENT_SERVICE_URL}/health",
    }

settings = Settings()