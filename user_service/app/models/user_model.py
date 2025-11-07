from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal
from datetime import datetime

class User(BaseModel):
    """User model with 2 roles: admin and customer"""
    username: str
    email: EmailStr
    password_hash: str
    role: Literal["admin", "customer"] = "customer" 
    
    # Extended profile fields
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    avatar_url: Optional[str] = None
    
    # Email verification
    is_email_verified: bool = False
    email_verification_token: Optional[str] = None
    email_verification_expires: Optional[datetime] = None
    
    # Password reset
    reset_password_token: Optional[str] = None
    reset_password_expires: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    # Account status
    is_active: bool = True
    is_deleted: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "john@example.com",
                "role": "customer",
                "full_name": "John Doe",
                "phone": "+84123456789",
                "address": "123 Main St, Hanoi"
            }
        }