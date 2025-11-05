from fastapi import APIRouter, HTTPException, status, Depends, Header
from ..database.connection import db
from ..core.security import hash_password, verify_password, create_access_token, verify_token
from ..schemas.user_schema import UserRegister, UserLogin, TokenResponse, UserResponse
from ..models.user_model import UserModel

router = APIRouter()

# Collection users
users_collection = db["users"]

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
def register_user(user: UserRegister):
    """Đăng ký người dùng mới"""
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Kiểm tra username đã tồn tại
    if users_collection.find_one({"username": user.username}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Hash password
    hashed_password = hash_password(user.password)
    
    # Tạo user document
    user_dict = UserModel.create_user_dict(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )
    
    # Insert vào MongoDB
    result = users_collection.insert_one(user_dict)
    
    return {
        "message": "User registered successfully",
        "user_id": str(result.inserted_id)
    }

@router.post("/login", response_model=TokenResponse)
def login_user(credentials: UserLogin):
    """Đăng nhập và trả về JWT token"""
    # Tìm user theo email
    user = users_collection.find_one({"email": credentials.email})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Tạo JWT token
    token_data = {
        "sub": user["email"],
        "user_id": str(user["_id"]),
        "role": user["role"]
    }
    access_token = create_access_token(token_data)
    
    # Serialize user data (loại bỏ password)
    user_response = UserModel.serialize_user(user)
    user_response.pop("password", None)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )

@router.get("/me", response_model=UserResponse)
def get_current_user(authorization: str = Header(None)):
    """Lấy thông tin user hiện tại từ JWT token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    # Lấy user từ database
    user = users_collection.find_one({"email": payload.get("sub")})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user_response = UserModel.serialize_user(user)
    user_response.pop("password", None)
    
    return user_response

@router.get("/users", response_model=list)
def get_all_users(authorization: str = Header(None)):
    """Lấy danh sách tất cả users (chỉ admin)"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    
    if not payload or payload.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    users = list(users_collection.find())
    users_response = []
    
    for user in users:
        user_data = UserModel.serialize_user(user)
        user_data.pop("password", None)
        users_response.append(user_data)
    
    return users_response