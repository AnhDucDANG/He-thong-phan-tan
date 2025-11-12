import os
import urllib.parse

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

    # Database: nếu có SQLALCHEMY_DATABASE_URL thì dùng trực tiếp, nếu không xây dựng từ các biến DB_*
    SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")
    if not SQLALCHEMY_DATABASE_URL:
        DB_USER = os.getenv("DB_USER", "sa")
        DB_PASSWORD = os.getenv("DB_PASSWORD", os.getenv("SA_PASSWORD", "Lyly2505"))
        DB_HOST = os.getenv("DB_HOST", "db-booking")
        DB_PORT = os.getenv("DB_PORT", "1433")
        DB_NAME = os.getenv("SQL_DB", os.getenv("DB_NAME", "rental_user_db"))
        # escape driver string
        DB_DRIVER = urllib.parse.quote_plus(os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server"))
        SQLALCHEMY_DATABASE_URL = f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?driver={DB_DRIVER}"

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