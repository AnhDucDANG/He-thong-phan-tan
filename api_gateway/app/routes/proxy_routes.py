from fastapi import APIRouter, Request, HTTPException, Header
from fastapi.responses import JSONResponse
import httpx
import logging
from ..core.config import settings
from ..core.forwarder import forward_request
from ..middleware.auth_middleware import verify_authentication

logger = logging.getLogger(__name__)

router = APIRouter()

PUBLIC_PATHS = [
    "/api/users/register",
    "/api/users/login",
]

def is_public_route(path: str) -> bool:
    """Check if route is public"""
    return any(path.startswith(public) for public in PUBLIC_PATHS)

@router.api_route(
    "/{service}/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
async def proxy_request(
    service: str,
    path: str,
    request: Request,
    authorization: str = Header(None)
):

    # Construct full path for logging
    full_path = f"/api/{service}/{path}" if path else f"/api/{service}"
    
    logger.info(f"📨 Received: {request.method} {request.url.path}")
    logger.info(f"📍 Parsed - Service: '{service}', Path: '{path}'")
    
    if not is_public_route(full_path):
        try:
            await verify_authentication(request)
            logger.info(f"🔐 Authenticated request to {full_path}")
        except HTTPException as e:
            logger.warning(f"🚫 Unauthorized request to {full_path}")
            raise e
    else:
        logger.info(f"🌐 Public request to {full_path}")
    
    # Validate service exists
    if service not in settings.SERVICE_ROUTES:
        logger.error(f"❌ Unknown service: '{service}'")
        logger.error(f"Available services: {list(settings.SERVICE_ROUTES.keys())}")
        raise HTTPException(
            status_code=404,
            detail=f"Service '{service}' not found"
        )
    
    # Get target service URL
    target_url = settings.SERVICE_ROUTES[service]
    
    if service == "vehicles":
        full_url = f"{target_url}/api/vehicles/{path}" if path else f"{target_url}/api/vehicles"
    else:
        full_url = f"{target_url}/{service}/{path}" if path else f"{target_url}/{service}"
    
    logger.info(f"📡 Forwarding: {request.method} {full_path} → {full_url}")
    
    # Forward request
    response = await forward_request(request, full_url, authorization)
    return response

@router.get("/services")
async def list_services():
    return {
        "gateway": "API Gateway v1.0.0",
        "total_services": len(settings.SERVICE_MAP),
        "services": [
            {
                "name": name,
                "url": url,
                "health_check": settings.HEALTH_CHECK_ENDPOINTS.get(name, "N/A")
            }
            for name, url in settings.SERVICE_MAP.items()
        ]
    }