from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .routes import user_routes
from .database.connection import check_connection

app = FastAPI(
    title="User Service",
    description="Microservice quản lý người dùng cho hệ thống cho thuê xe",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user_routes.router, prefix="/users", tags=["Users"])

@app.on_event("startup")
async def startup_event():
    """Kiểm tra kết nối MongoDB khi khởi động"""
    if not check_connection():
        raise Exception("Cannot connect to MongoDB. Please check your configuration.")
    print("✅ Connected to MongoDB successfully!")

@app.get("/", tags=["Root"])
def read_root():
    return {
        "service": "User Service",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint"""
    db_status = check_connection()
    
    if not db_status:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    return {
        "status": "healthy",
        "database": "connected"
    }