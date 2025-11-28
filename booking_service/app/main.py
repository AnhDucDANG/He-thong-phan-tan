from fastapi import FastAPI
from app.database.connection import init_db, close_db
from app.routes.booking_routes import router as booking_router
from app.routes.health_routes import router as health_router

app = FastAPI(title="Service 3 - Booking API")

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.on_event("shutdown")
async def shutdown_event():
    await close_db()

app.include_router(health_router)
app.include_router(booking_router, prefix="/api/bookings")

@app.get("/")
async def root():
    return {"Service": "Booking Service (MongoDB)", "status": "running"}