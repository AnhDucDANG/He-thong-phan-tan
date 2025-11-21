from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # MongoDB
    MONGO_HOST: str = "localhost"
    MONGO_PORT: str = "27017"
    MONGO_DB: str = "db-payment"
    
    @property
    def MONGO_URL(self) -> str:
        return f"mongodb://{self.MONGO_HOST}:{self.MONGO_PORT}/{self.MONGO_DB}"
    
    # Service
    SERVICE_PORT: int = 8004
    SERVICE_HOST: str = "0.0.0.0"
    
    # JWT
    SECRET_KEY: str = "35a91c468c0a8a62d3669ba143ddf1db"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # External Services
    USER_SERVICE_URL: str = "http://localhost:8001"
    BOOKING_SERVICE_URL: str = "http://localhost:8003"
    VEHICLE_SERVICE_URL: str = "http://localhost:8002"
    
    # VNPay
    VNPAY_TMN_CODE: str = "M49B55TZ"
    VNPAY_HASH_SECRET: str = "M4K2A62SXWDHH5A4LO1I5ZXQSYVVKE70"
    VNPAY_URL: str = "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"
    VNPAY_RETURN_URL: str = "http://localhost:8004/api/v1/payments/vnpay-return"
    VNPAY_API_URL: str = "https://sandbox.vnpayment.vn/merchant_webapi/api/transaction"
    
    class Config:
        env_file = ".env.payment"
        case_sensitive = False

settings = Settings()