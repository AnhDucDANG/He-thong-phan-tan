from fastapi import APIRouter, HTTPException
import httpx
import logging
from ..core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/api/services")
async def get_services():
    """Lấy danh sách tất cả services - Public"""
    return {
        "services": settings.SERVICE_MAP,
        "gateway_version": "1.0.0"
    }

@router.get("/api/health/all")
async def check_all_services():
    """Kiểm tra health của tất cả services - Public"""
    logger.info("🔍 Checking health of all services...")
    
    results = {}
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        for service_name, endpoint in settings.HEALTH_CHECK_ENDPOINTS.items():
            try:
                logger.info(f"   Checking {service_name} at {endpoint}")
                response = await client.get(endpoint)
                
                if response.status_code == 200:
                    data = response.json()
                    results[service_name] = {
                        "status": data.get("status", "unknown"),
                        "url": endpoint
                    }
                    logger.info(f"   ✅ {service_name}: healthy")
                else:
                    results[service_name] = {
                        "status": "unhealthy",
                        "url": endpoint,
                        "error": f"HTTP {response.status_code}"
                    }
                    logger.warning(f"   ⚠️ {service_name}: unhealthy (HTTP {response.status_code})")
                    
            except httpx.ConnectError:
                results[service_name] = {
                    "status": "unreachable",
                    "url": endpoint,
                    "error": "Connection refused"
                }
                logger.warning(f"   ⚠️ {service_name}: unreachable")
                
            except Exception as e:
                results[service_name] = {
                    "status": "error",
                    "url": endpoint,
                    "error": str(e)
                }
                logger.error(f"   ❌ {service_name}: error - {e}")
    
    # Determine overall status
    all_healthy = all(
        service["status"] == "healthy" 
        for service in results.values()
    )
    
    return {
        "gateway": "healthy",
        "overall_status": "healthy" if all_healthy else "degraded",
        "services": results,
        "timestamp": httpx.get("http://worldtimeapi.org/api/timezone/Etc/UTC").json()["datetime"] if all_healthy else None
    }