from fastapi import APIRouter, HTTPException, Depends, status, Header, Form, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
import logging
import secrets
from bson import ObjectId

from ..schemas.user_schema import (
    UserRegister, UserLogin, UserResponse, TokenResponse, 
    MessageResponse, UserUpdate, ChangePassword, 
    ForgotPassword, ResetPassword, VerifyEmail,
    UserStatsResponse, DailySignup
)
from ..core.security import (
    verify_password, get_password_hash, create_access_token,
    verify_token, generate_verification_token, 
    create_verification_token_expiry, is_token_expired
)
from ..core.config import settings
from ..database.connection import get_database, client

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

# ✅ Helper function
def get_users_collection():
    """Get users collection from database"""
    db = get_database()
    return db.users


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
    user = await users_collection.find_one({"email": email, "is_deleted": False})
    
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


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegister):
    """
    Register a new user account
    - Customers can self-register
    - Admin accounts can be created via this endpoint
    """
    logger.info(f"📝 Registration attempt for: {user_data.email}")
    
    users_collection = get_users_collection()
    
    # Check email exists
    existing_user = await users_collection.find_one({
        "email": user_data.email,
        "is_deleted": False
    })
    
    if existing_user:
        logger.warning(f"⚠️ Email already exists: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check username exists
    existing_username = await users_collection.find_one({
        "username": user_data.username,
        "is_deleted": False
    })
    
    if existing_username:
        logger.warning(f"⚠️ Username already exists: {user_data.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Generate verification token
    verification_token = generate_verification_token()
    
    # Create user document
    user_doc = {
        "username": user_data.username,
        "email": user_data.email,
        "password_hash": get_password_hash(user_data.password),
        "role": user_data.role,  # ✅ Allow admin role
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
    
    # Insert user
    result = await users_collection.insert_one(user_doc)
    
    logger.info(f"✅ User registered successfully: {user_data.email} (role: {user_data.role})")
    
    return {
        "message": f"{user_data.role.capitalize()} registered successfully",
        "user_id": str(result.inserted_id),
        "email": user_data.email,
        "role": user_data.role,
        "verification_token": verification_token
    }

@router.post("/login", response_model=TokenResponse)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login user (both customer and admin) and return access token
    
    Accepts OAuth2 form data:
    - username: email address
    - password: user password
    """
    # OAuth2PasswordRequestForm uses 'username' field, but we treat it as email
    email = form_data.username
    password = form_data.password
    
    logger.info(f"🔐 Login attempt for: {email}")
    
    users_collection = get_users_collection()
    user = await users_collection.find_one({
        "email": email,
        "is_deleted": False
    })
    
    if not user or not verify_password(password, user["password_hash"]):
        logger.warning(f"⚠️ Invalid credentials for: {email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.get("is_active", True):
        logger.warning(f"⚠️ Inactive account login attempt: {email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Please contact support."
        )
    
    # Update last login
    await users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login": datetime.utcnow()}}
    )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    
    logger.info(f"✅ Login successful for: {email} (role: {user['role']})")
    
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
    user = await users_collection.find_one({
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
    
    await users_collection.update_one(
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
    
    await users_collection.update_one(
        {"_id": current_user["_id"]},
        {"$set": update_data}
    )
    
    updated_user = await users_collection.find_one({"_id": current_user["_id"]})
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
    await users_collection.update_one(
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
    user = await users_collection.find_one({
        "email": data.email,
        "is_deleted": False
    })
    
    if not user:
        return {"message": "If email exists, password reset link has been sent"}
    
    reset_token = generate_verification_token()
    reset_expires = create_verification_token_expiry(settings.PASSWORD_RESET_EXPIRE_HOURS)
    
    await users_collection.update_one(
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
    user = await users_collection.find_one({
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
    
    await users_collection.update_one(
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


@router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(admin_user: dict = Depends(get_current_admin)):
    """Get user statistics (Admin only)"""
    logger.info(f"📊 Stats request from admin: {admin_user['email']}")
    
    users_collection = get_users_collection()
    
    total_users = await users_collection.count_documents({"is_deleted": False})
    verified_users = await users_collection.count_documents({
        "is_email_verified": True,
        "is_deleted": False
    })
    customers = await users_collection.count_documents({
        "role": "customer",
        "is_deleted": False
    })
    admins = await users_collection.count_documents({
        "role": "admin",
        "is_deleted": False
    })
    
    # Get daily signups for last 7 days
    from datetime import timedelta
    daily_signups = []
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    for i in range(6, -1, -1):  # Last 7 days
        day_start = today - timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        
        count = await users_collection.count_documents({
            "created_at": {
                "$gte": day_start,
                "$lt": day_end
            },
            "is_deleted": False
        })
        
    
    users_collection = get_users_collection()
    await users_collection.update_one(
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

# ==================== ADMIN USER MANAGEMENT ====================

@router.get("/users", response_model=list[UserResponse])
async def get_all_users(admin_user: dict = Depends(get_current_admin)):
    """Get all users (Admin only)"""
    users_collection = get_users_collection()
    users_cursor = users_collection.find({"is_deleted": False})
    users = await users_cursor.to_list(length=None)
    
    # Convert _id to string
    for user in users:
        user["_id"] = str(user["_id"])
        
    return users

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: str,
    admin_user: dict = Depends(get_current_admin)
):
    """Get user by ID (Admin only)"""
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
        
    users_collection = get_users_collection()
    user = await users_collection.find_one({"_id": ObjectId(user_id), "is_deleted": False})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user["_id"] = str(user["_id"])
    return user

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user_by_admin(
    user_id: str,
    user_update: UserUpdate,
    admin_user: dict = Depends(get_current_admin)
):
    """Update user by ID (Admin only)"""
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
        
    users_collection = get_users_collection()
    
    # Check if user exists
    existing_user = await users_collection.find_one({"_id": ObjectId(user_id), "is_deleted": False})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = {"updated_at": datetime.utcnow()}
    
    if user_update.full_name is not None:
        update_data["full_name"] = user_update.full_name
    if user_update.phone is not None:
        update_data["phone"] = user_update.phone
    if user_update.address is not None:
        update_data["address"] = user_update.address
    if user_update.avatar_url is not None:
        update_data["avatar_url"] = user_update.avatar_url
        
    await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )
    
    updated_user = await users_collection.find_one({"_id": ObjectId(user_id)})
    updated_user["_id"] = str(updated_user["_id"])
    
    return updated_user

@router.delete("/users/{user_id}", response_model=MessageResponse)
async def delete_user_by_admin(
    user_id: str,
    admin_user: dict = Depends(get_current_admin)
):
    """Delete user by ID (Admin only)"""
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
        
    users_collection = get_users_collection()
    
    result = await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {
            "$set": {
                "is_deleted": True,
                "is_active": False,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
async def get_sharding_status():
    """Get detailed sharding information"""
    from ..database.connection import get_database, client
    
    try:
        db = get_database()
        admin_db = client.admin
        
        # Get server status
        server_status = await admin_db.command('serverStatus')
        is_mongos = server_status.get('process') == 'mongos'
        
        if not is_mongos:
            return {
                "sharded": False,
                "message": "Not connected to mongos router",
                "process": server_status.get('process', 'unknown')
            }
        
        # Get shards list
        shards_info = await admin_db.command('listShards')
        
        # Get database stats
        db_stats = await db.command('dbStats')
        
        # Get collections sharding info
        collections_info = {}
        for coll_name in ['users', 'vehicles', 'bookings', 'payments']:
            try:
                coll_stats = await db.command('collStats', coll_name)
                collections_info[coll_name] = {
                    "sharded": coll_stats.get('sharded', False),
                    "count": coll_stats.get('count', 0),
                    "size": coll_stats.get('size', 0),
                    "shardKey": coll_stats.get('shardKey', {}),
                    "shards": {}
                }
                
                # Get shard distribution if sharded
                if coll_stats.get('sharded') and 'shards' in coll_stats:
                    for shard_name, shard_data in coll_stats['shards'].items():
                        collections_info[coll_name]['shards'][shard_name] = {
                            "count": shard_data.get('count', 0),
                            "size": shard_data.get('size', 0)
                        }
                        
            except Exception as e:
                collections_info[coll_name] = {
                    "error": str(e),
                    "sharded": False
                }
        
        return {
            "sharded": True,
            "process": "mongos",
            "shards": shards_info.get('shards', []),
            "database": {
                "name": db.name,
                "collections": db_stats.get('collections', 0),
                "dataSize": db_stats.get('dataSize', 0),
                "storageSize": db_stats.get('storageSize', 0),
                "indexes": db_stats.get('indexes', 0)
            },
            "collections": collections_info
        }
        
    except Exception as e:
        logger.error(f"Error getting sharding status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/sharding/list-shards", response_model=dict)
async def list_shards():
    """List all shards in the cluster"""
    from ..database.connection import client
    
    try:
        admin_db = client.admin
        result = await admin_db.command('listShards')
        
        shards_list = []
        for shard in result.get('shards', []):
            shards_list.append({
                "id": shard.get('_id'),
                "host": shard.get('host'),
                "state": shard.get('state', 1),
                "tags": shard.get('tags', [])
            })
        
        return {
            "ok": result.get('ok', 0),
            "shard_count": len(shards_list),
            "shards": shards_list
        }
        
    except Exception as e:
        logger.error(f"Error listing shards: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/sharding/db-stats", response_model=dict)
async def get_db_stats():
    """Get database statistics"""
    from ..database.connection import get_database
    
    try:
        db = get_database()
        stats = await db.command('dbStats')
        
        return {
            "database": db.name,
            "collections": stats.get('collections', 0),
            "views": stats.get('views', 0),
            "objects": stats.get('objects', 0),
            "dataSize": stats.get('dataSize', 0),
            "storageSize": stats.get('storageSize', 0),
            "indexes": stats.get('indexes', 0),
            "indexSize": stats.get('indexSize', 0),
            "totalSize": stats.get('totalSize', 0),
            "scaleFactor": stats.get('scaleFactor', 1)
        }
        
    except Exception as e:
        logger.error(f"Error getting db stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/test-data/populate", response_model=dict)
async def populate_test_data(
    count: int = 50,
    authorization: str = Header(None)
):
    """Populate test data for sharding demonstration"""
    user = await verify_token(authorization)
    
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    from ..database.connection import get_database
    from ..core.security import get_password_hash
    from datetime import datetime
    
    db = get_database()
    
    # Insert test users
    users_data = [
        {
            "username": f"test_user_{i}",
            "email": f"test{i}@example.com",
            "full_name": f"Test User {i}",
            "hashed_password": get_password_hash("Test123!"),
            "role": "customer",
            "phone": f"090{i:07d}",
            "is_active": True,
            "is_deleted": False,
            "is_email_verified": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        for i in range(1, count + 1)
    ]
    
    result = await db.users.insert_many(users_data)
    
    return {
        "message": f"{count} test users populated successfully",
        "users_inserted": len(result.inserted_ids),
        "note": "Check distribution with /distribution endpoint"
    }

@router.get("/distribution", response_model=dict)
async def get_user_distribution(authorization: str = Header(None)):
    """Get user distribution across shards"""
    user = await verify_token(authorization)
    
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    from ..database.connection import get_database
    
    db = get_database()
    
    try:
        # Get collection stats
        stats = await db.command('collStats', 'users')
        
        total_count = stats.get('count', 0)
        
        distribution = {
            "collection": "users",
            "total_users": total_count,
            "sharded": stats.get('sharded', False),
            "shard_key": stats.get('shardKey', {}),
            "shard_distribution": {}
        }
        
        if stats.get('sharded') and 'shards' in stats:
            for shard_name, shard_data in stats['shards'].items():
                count = shard_data.get('count', 0)
                percentage = round(count / total_count * 100, 2) if total_count > 0 else 0
                
                distribution["shard_distribution"][shard_name] = {
                    "count": count,
                    "size_bytes": shard_data.get('size', 0),
                    "percentage": f"{percentage}%"
                }
        else:
            distribution["message"] = "Collection is not sharded or no shards info available"
        
        return distribution
        
    except Exception as e:
        logger.error(f"Error getting distribution: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/sharding/explain", response_model=dict)
async def get_query_explain(
    collection: str = "users",
    authorization: str = Header(None)
):
    """Get explain plan for sharded query"""
    user = await verify_token(authorization)
    
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    from ..database.connection import get_database
    
    db = get_database()
    
    try:
        # Get explain for a simple query
        cursor = db[collection].find({}).limit(10)
        explain = await cursor.explain()
        
        return {
            "collection": collection,
            "queryPlanner": explain.get('queryPlanner', {}),
            "executionStats": explain.get('executionStats', {}),
            "serverInfo": explain.get('serverInfo', {})
        }
        
    except Exception as e:
        logger.error(f"Error getting explain: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )