from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
import logging
import secrets  

from ..schemas.user_schema import (
    UserRegister, UserLogin, UserResponse, TokenResponse, 
    UserUpdate, ChangePassword, ForgotPassword, ResetPassword,
    VerifyEmail, MessageResponse, UserStatsResponse
)
from ..core.security import (
    verify_password, get_password_hash, create_access_token,
    verify_token, generate_verification_token, 
    create_verification_token_expiry, is_token_expired
)
from ..core.config import settings
from ..database.connection import get_users_collection

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

# ==================== HELPER FUNCTIONS ====================

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    email = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    users_collection = get_users_collection()
    user = users_collection.find_one({"email": email, "is_deleted": False})
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    return user

async def get_current_admin(current_user: dict = Depends(get_current_user)):
    """Verify current user is admin"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

# ==================== AUTHENTICATION ENDPOINTS ====================

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegister):
    """
    Register a new customer account
    - Only customers can self-register
    - Admin accounts must be created via script/seeding
    """
    logger.info(f"📝 Registration attempt for: {user_data.email}")
    
    users_collection = get_users_collection()
    
    # Check if email exists
    if users_collection.find_one({"email": user_data.email, "is_deleted": False}):
        logger.warning(f"⚠️ Email already exists: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username exists
    if users_collection.find_one({"username": user_data.username, "is_deleted": False}):
        logger.warning(f"⚠️ Username already exists: {user_data.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Generate verification token
    verification_token = generate_verification_token()
    
    # Create user document (always customer for self-registration)
    user_doc = {
        "username": user_data.username,
        "email": user_data.email,
        "password_hash": get_password_hash(user_data.password),
        "role": "customer",  # ✅ Always customer
        "full_name": user_data.full_name,
        "phone": user_data.phone,
        "address": user_data.address,
        "avatar_url": None,
        "is_email_verified": False,
        "email_verification_token": verification_token,
        "email_verification_expires": create_verification_token_expiry(
            settings.EMAIL_VERIFICATION_EXPIRE_HOURS
        ),
        "reset_password_token": None,
        "reset_password_expires": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "last_login": None,
        "is_active": True,
        "is_deleted": False
    }
    
    result = users_collection.insert_one(user_doc)
    
    logger.info(f"✅ User registered successfully: {user_data.email}")
    
    return {
        "message": "User registered successfully. Please check your email for verification.",
        "user_id": str(result.inserted_id),
        "verification_token": verification_token
    }

@router.post("/login", response_model=TokenResponse)
async def login_user(credentials: UserLogin):
    """Login user (both customer and admin) and return access token"""
    logger.info(f"🔐 Login attempt for: {credentials.email}")
    
    users_collection = get_users_collection()
    user = users_collection.find_one({
        "email": credentials.email,
        "is_deleted": False
    })
    
    if not user or not verify_password(credentials.password, user["password_hash"]):
        logger.warning(f"⚠️ Invalid credentials for: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.get("is_active", True):
        logger.warning(f"⚠️ Inactive account login attempt: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Please contact support."
        )
    
    # Update last login
    users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login": datetime.utcnow()}}
    )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    
    logger.info(f"✅ Login successful for: {credentials.email} (role: {user['role']})")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(data: VerifyEmail):
    """Verify user email with token"""
    logger.info(f"📧 Email verification attempt")
    
    users_collection = get_users_collection()
    user = users_collection.find_one({
        "email_verification_token": data.token,
        "is_deleted": False
    })
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )
    
    if user.get("is_email_verified", False):
        return {"message": "Email already verified"}
    
    if is_token_expired(user["email_verification_expires"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token has expired"
        )
    
    # Verify email
    users_collection.update_one(
        {"_id": user["_id"]},
        {
            "$set": {
                "is_email_verified": True,
                "email_verification_token": None,
                "email_verification_expires": None,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    logger.info(f"✅ Email verified for: {user['email']}")
    
    return {"message": "Email verified successfully"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    logger.info(f"👤 Profile request from: {current_user['email']}")
    
    current_user["_id"] = str(current_user["_id"])
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update current user profile"""
    logger.info(f"✏️ Profile update request from: {current_user['email']}")
    
    users_collection = get_users_collection()
    
    update_data = {"updated_at": datetime.utcnow()}
    
    if user_update.full_name is not None:
        update_data["full_name"] = user_update.full_name
    if user_update.phone is not None:
        update_data["phone"] = user_update.phone
    if user_update.address is not None:
        update_data["address"] = user_update.address
    if user_update.avatar_url is not None:
        update_data["avatar_url"] = user_update.avatar_url
    
    users_collection.update_one(
        {"_id": current_user["_id"]},
        {"$set": update_data}
    )
    
    updated_user = users_collection.find_one({"_id": current_user["_id"]})
    updated_user["_id"] = str(updated_user["_id"])
    
    logger.info(f"✅ Profile updated for: {current_user['email']}")
    
    return updated_user

@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    data: ChangePassword,
    current_user: dict = Depends(get_current_user)
):
    """Change user password"""
    logger.info(f"🔑 Password change request from: {current_user['email']}")
    
    if not verify_password(data.old_password, current_user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password"
        )
    
    users_collection = get_users_collection()
    users_collection.update_one(
        {"_id": current_user["_id"]},
        {
            "$set": {
                "password_hash": get_password_hash(data.new_password),
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    logger.info(f"✅ Password changed for: {current_user['email']}")
    
    return {"message": "Password changed successfully"}

@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(data: ForgotPassword):
    """Request password reset"""
    logger.info(f"🔐 Password reset request for: {data.email}")
    
    users_collection = get_users_collection()
    user = users_collection.find_one({
        "email": data.email,
        "is_deleted": False
    })
    
    if not user:
        # Don't reveal if email exists
        return {"message": "If email exists, password reset link has been sent"}
    
    reset_token = generate_verification_token()
    reset_expires = create_verification_token_expiry(settings.PASSWORD_RESET_EXPIRE_HOURS)
    
    users_collection.update_one(
        {"_id": user["_id"]},
        {
            "$set": {
                "reset_password_token": reset_token,
                "reset_password_expires": reset_expires,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    logger.info(f"✅ Password reset token generated for: {data.email}")
    
    return {
        "message": "If email exists, password reset link has been sent",
        "reset_token": reset_token
    }

@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(data: ResetPassword):
    """Reset password using token"""
    logger.info(f"🔄 Password reset attempt")
    
    users_collection = get_users_collection()
    user = users_collection.find_one({
        "reset_password_token": data.token,
        "is_deleted": False
    })
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    if is_token_expired(user["reset_password_expires"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired"
        )
    
    users_collection.update_one(
        {"_id": user["_id"]},
        {
            "$set": {
                "password_hash": get_password_hash(data.new_password),
                "reset_password_token": None,
                "reset_password_expires": None,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    logger.info(f"✅ Password reset successful for: {user['email']}")
    
    return {"message": "Password reset successfully"}

# ==================== ADMIN ENDPOINTS ====================

@router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(admin_user: dict = Depends(get_current_admin)):
    """Get user statistics (Admin only)"""
    logger.info(f"📊 Stats request from admin: {admin_user['email']}")
    
    users_collection = get_users_collection()
    
    total_users = users_collection.count_documents({"is_deleted": False})
    verified_users = users_collection.count_documents({
        "is_email_verified": True,
        "is_deleted": False
    })
    customers = users_collection.count_documents({
        "role": "customer",
        "is_deleted": False
    })
    admins = users_collection.count_documents({
        "role": "admin",
        "is_deleted": False
    })
    
    return {
        "total_users": total_users,
        "verified_users": verified_users,
        "customers": customers,
        "admins": admins
    }

@router.delete("/me", response_model=MessageResponse)
async def delete_account(current_user: dict = Depends(get_current_user)):
    """Soft delete user account"""
    logger.info(f"🗑️ Account deletion request from: {current_user['email']}")
    
    users_collection = get_users_collection()
    users_collection.update_one(
        {"_id": current_user["_id"]},
        {
            "$set": {
                "is_deleted": True,
                "is_active": False,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    logger.info(f"✅ Account deleted for: {current_user['email']}")
    
    return {"message": "Account deleted successfully"}