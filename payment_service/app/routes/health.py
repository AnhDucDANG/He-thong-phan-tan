from fastapi import APIRouter
from app.database import db
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health_check():
    try:
        await db.client.admin.command('ping')
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy",
        "service": "payment_service",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }