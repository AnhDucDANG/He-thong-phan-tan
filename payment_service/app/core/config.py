import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # ======================= SERVICE INFO ==========================
    SERVICE_HOST: str = os.getenv("SERVICE_HOST", "0.0.0.0")
    SERVICE_PORT: int = int(os.getenv("SERVICE_PORT", "8004"))

    USER_SERVICE_URL: str = os.getenv("USER_SERVICE_URL", "http://user_service:8001")
    VEHICLE_SERVICE_URL: str = os.getenv("VEHICLE_SERVICE_URL", "http://vehicle_service:8002")
    BOOKING_SERVICE_URL: str = os.getenv("BOOKING_SERVICE_URL", "http://booking_service:8003")
    PAYMENT_SERVICE_URL: str = os.getenv("PAYMENT_SERVICE_URL", "http://payment_service:8004")

    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "120"))

    # ======================= AUTH CONFIG ===========================
    SECRET_KEY: str = os.getenv("SECRET_KEY", "CHANGE_ME")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # ======================= MONGO CONFIG ==========================
    MONGO_URL: Optional[str] = os.getenv("MONGO_URL")
    MONGO_USER: str = os.getenv("MONGO_USER", "hieutm")
    MONGO_PASSWORD: str = os.getenv("MONGO_PASSWORD", "12032002")
    MONGO_HOST: str = os.getenv("MONGO_HOST", "cluster0.oeq0jbr.mongodb.net")
    MONGO_DB: str = os.getenv("MONGO_DB", "db-payment")

    # ======================= VNPay CONFIG ==========================
    VNPAY_TMN_CODE: str = os.getenv("VNPAY_TMN_CODE", "")
    VNPAY_HASH_SECRET: str = os.getenv("VNPAY_HASH_SECRET", "")
    VNPAY_URL: str = os.getenv("VNPAY_URL", "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html")
    VNPAY_RETURN_URL: str = os.getenv("VNPAY_RETURN_URL", "http://localhost:8004/api/payments/vnpay/return")
    VNPAY_API_URL: str = os.getenv("VNPAY_API_URL", "https://sandbox.vnpayment.vn/merchant_webapi/api/transaction")

    def get_mongo_url(self) -> str:
        """
        Use MONGO_URL if provided; otherwise construct atlas URL.
        """
        if self.MONGO_URL:
            return self.MONGO_URL

        return (
            f"mongodb+srv://{self.MONGO_USER}:{self.MONGO_PASSWORD}"
            f"@{self.MONGO_HOST}/{self.MONGO_DB}"
            f"?retryWrites=true&w=majority"
        )

    @property
    def SERVICE_MAP(self):
        return {
            "users": self.USER_SERVICE_URL,
            "vehicles": self.VEHICLE_SERVICE_URL,
            "bookings": self.BOOKING_SERVICE_URL,
            "payments": self.PAYMENT_SERVICE_URL,
        }

    @property
    def HEALTH_CHECK_ENDPOINTS(self):
        return {
            "users": f"{self.USER_SERVICE_URL}/health",
            "vehicles": f"{self.VEHICLE_SERVICE_URL}/health",
            "bookings": f"{self.BOOKING_SERVICE_URL}/health",
            "payments": f"{self.PAYMENT_SERVICE_URL}/health",
        }


settings = Settings()
