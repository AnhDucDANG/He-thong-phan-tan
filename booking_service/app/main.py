from fastapi import FastAPI
from fastapi import APIRouter
from pydantic import BaseModel
from app.database import create_tables
from app.routes.booking_routes import router as booking_router
from app.routes.health_routes import router as health_router # <-- DÒNG MỚI ĐÃ THÊM

app = FastAPI()

create_tables()
# router = APIRouter() # Dòng này không cần thiết vì bạn đã có booking_router
app = FastAPI(title="Service 2 - Booking API")

# Đăng ký Health Route ở cấp độ GỐC (root path) để Docker dễ dàng kiểm tra
app.include_router(health_router, prefix="")

# Đăng ký Booking Route với prefix /api/v1
app.include_router(booking_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"Service": "Service 2 - Booking", "status": "running"}