from fastapi import FastAPI
from app.database.connection import init_db, close_db
from app.routes.payment_routes import router as payment_router

app = FastAPI(title="Payment Service", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.on_event("shutdown")
async def shutdown_event():
    await close_db()

@app.get("/api/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": "payment_service"}

# mount API router
app.include_router(payment_router, prefix="/api")
