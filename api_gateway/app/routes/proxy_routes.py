from fastapi import APIRouter, Request, HTTPException, Header
from fastapi.responses import JSONResponse
import logging
from typing import Optional
from ..core.config import settings
from ..core.forwarder import forward_request
from ..middleware.auth_middleware import verify_authentication

logger = logging.getLogger(__name__)

router = APIRouter()

PUBLIC_PATHS = [
    "/api/users/register",
    "/api/users/login",
    "/api/vehicles",  # Public for testing - vehicles listing
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
    authorization: Optional[str] = Header(None)
):
    """
    Proxy requests to microservices
    Route: /api/{service}/{path}
    """
    
    # Construct full path
    full_path = f"/api/{service}/{path}" if path else f"/api/{service}"
    
    logger.info(f"📨 Incoming: {request.method} {full_path}")
    logger.info(f"📍 Service: '{service}', Path: '{path}'")
    
    # Check authentication for protected routes
    if not is_public_route(full_path):
        try:
            await verify_authentication(request)
            logger.info(f"🔐 Authenticated")
        except HTTPException as e:
            logger.warning(f"🚫 Unauthorized")
            raise e
    else:
        logger.info(f"🌐 Public route")
    
    # Validate service exists
    if service not in settings.SERVICE_ROUTES:
        logger.error(f"❌ Unknown service: '{service}'")
        logger.error(f"📋 Available: {list(settings.SERVICE_ROUTES.keys())}")
        raise HTTPException(
            status_code=404,
            detail=f"Service '{service}' not found"
        )
    
    # Get target service URL
    target_base_url = settings.SERVICE_ROUTES[service]
    
    # Build full target URL based on service routing convention
    # - users: Routes at root (e.g., /register, /login, /me, /users)
    # - bookings: Routes at /bookings (e.g., /bookings/, /bookings/{id})
    # - vehicles: Routes at /api/vehicles 
    # - payments: Routes at /api/payments
    
    if service == "users":
        # User service: strip /api/users prefix
        if path:
            target_url = f"{target_base_url}/{path}"
        else:
            target_url = target_base_url
    elif service == "bookings":
        # Booking service: use /bookings prefix
        if path:
            target_url = f"{target_base_url}/bookings/{path}"
        else:
            target_url = f"{target_base_url}/bookings"
    else:
        # Other services (vehicles, payments): keep /api/{service} prefix
        if path:
            target_url = f"{target_base_url}/api/{service}/{path}"
        else:
            target_url = f"{target_base_url}/api/{service}"
    
    logger.info(f"🚀 Forward: {request.method} → {target_url}")
    
    # Forward request
    response = await forward_request(request, target_url, authorization)
    return response

@router.get("/services")
async def list_services():
    """List all available services"""
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