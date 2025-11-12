from fastapi import FastAPI
from app.routes.health_routes import router as health_router
from fastapi import APIRouter
from pydantic import BaseModel
from booking_service.database import create_tables
from booking_service.api.v1.booking_routes import router as booking_router

app = FastAPI()

create_tables()
router = APIRouter()
app = FastAPI(title="Service 2 - Booking API")
# đăng ký health route
app.include_router(health_router)
app.include_router(booking_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"Service": "Service 2 - Booking", "status": "running"}