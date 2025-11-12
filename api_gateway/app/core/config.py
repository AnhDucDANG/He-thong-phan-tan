import os
from typing import Dict

class Settings:
    # Gateway
    GATEWAY_HOST: str = os.getenv("GATEWAY_HOST", "0.0.0.0")
    GATEWAY_PORT: int = int(os.getenv("GATEWAY_PORT", "8000"))
    
    # Microservices URLs
    USER_SERVICE_URL: str = os.getenv("USER_SERVICE_URL", "http://user_service:8001")
    VEHICLE_SERVICE_URL: str = os.getenv("VEHICLE_SERVICE_URL", "http://localhost:8002")
    BOOKING_SERVICE_URL: str = os.getenv("BOOKING_SERVICE_URL", "http://localhost:8003")
    PAYMENT_SERVICE_URL: str = os.getenv("PAYMENT_SERVICE_URL", "http://100.108.163.69:8004")
    
    SERVICE_ROUTES: Dict[str, str] = {
        "users": USER_SERVICE_URL,
        "vehicles": VEHICLE_SERVICE_URL,
        "bookings": BOOKING_SERVICE_URL,
        "payments": PAYMENT_SERVICE_URL,
    }
    
    # Service map (for logging and health checks)
    SERVICE_MAP: Dict[str, str] = {
        "user_service": USER_SERVICE_URL,
        "vehicle_service": VEHICLE_SERVICE_URL,
        "booking_service": BOOKING_SERVICE_URL,
        "payment_service": PAYMENT_SERVICE_URL,
    }
    
    # Health check endpoints
    HEALTH_CHECK_ENDPOINTS: Dict[str, str] = {
        "user_service": f"{USER_SERVICE_URL}/health",
        "vehicle_service": f"{VEHICLE_SERVICE_URL}/health",
        "booking_service": f"{BOOKING_SERVICE_URL}/health",
        "payment_service": f"{PAYMENT_SERVICE_URL}/health",
    }
    
    # Request timeout
    REQUEST_TIMEOUT: float = 30.0
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # CORS
    CORS_ORIGINS: list = ["*"]
    
    # Public routes (không cần authentication)
    PUBLIC_ROUTES: list = [
        "/api/users/register",
        "/api/users/login",
        "/health",
        "/",
        "/docs",
        "/redoc",
        "/openapi.json"
    ]
    
settings = Settings()