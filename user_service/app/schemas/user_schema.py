from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Literal
from datetime import datetime
import re


class UserRegister(BaseModel):
    """Schema for user registration"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: Literal["customer", "admin"] = "customer"
    full_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = None
    address: Optional[str] = None
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username must be alphanumeric and underscores only')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not re.match(r'^\+?[0-9]{10,15}$', v):
            raise ValueError('Invalid phone number format')
        return v


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Schema for updating user profile"""
    full_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = None
    address: Optional[str] = None
    avatar_url: Optional[str] = None
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not re.match(r'^\+?[0-9]{10,15}$', v):
            raise ValueError('Invalid phone number format')
        return v


class ChangePassword(BaseModel):
    """Schema for changing password"""
    old_password: str
    new_password: str = Field(..., min_length=6)
    
    @validator('new_password')
    def passwords_different(cls, v, values):
        if 'old_password' in values and v == values['old_password']:
            raise ValueError('New password must be different from old password')
        return v


class ForgotPassword(BaseModel):
    """Schema for forgot password request"""
    email: EmailStr


class ResetPassword(BaseModel):
    """Schema for resetting password"""
    token: str
    new_password: str = Field(..., min_length=6)


class VerifyEmail(BaseModel):
    """Schema for email verification"""
    token: str


class UserResponse(BaseModel):
    """Schema for user response (without sensitive data)"""
    id: str = Field(alias="_id")
    username: str
    email: str
    role: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    avatar_url: Optional[str] = None
    is_email_verified: bool
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "username": "johndoe",
                "email": "john@example.com",
                "role": "customer",
                "full_name": "John Doe",
                "phone": "+84123456789",
                "is_email_verified": True,
                "is_active": True
            }
        }


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class MessageResponse(BaseModel):
    """Schema for simple message response"""
    message: str


class DailySignup(BaseModel):
    date: str
    count: int


class UserStatsResponse(BaseModel):
    """Schema for user statistics"""
    total_users: int
    verified_users: int
    customers: int
    admins: int
    daily_signups: list[DailySignup]