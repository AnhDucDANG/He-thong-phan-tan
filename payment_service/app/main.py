from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import init_db
from app.routes import health, payments
from app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    print("🚀 Payment Service started successfully")
    yield
    # Shutdown
    print("🛑 Payment Service shutting down")

app = FastAPI(
    title="Payment Service API",
    description="Microservice xử lý thanh toán cho hệ thống Rental Car",
    version="1.0.0",
    lifespan=lifespan
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
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["Payments"])

@app.get("/")
async def root():
    return {
        "message": "Payment Service is running!",
        "version": "1.0.0",
        "docs": "/docs"
    }