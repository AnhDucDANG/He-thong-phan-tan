from fastapi import APIRouter, Request, HTTPException, Depends
from typing import Dict, Any
import logging
from ..core.forwarder import forwarder
from ..core.config import settings
from ..middleware.auth_middleware import verify_authentication

logger = logging.getLogger(__name__)

router = APIRouter()

@router.api_route(
    "/{service}/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    dependencies=[Depends(verify_authentication)]
)
async def proxy_request(
    service: str,
    path: str,
    request: Request
):
    """
    Proxy request to appropriate microservice
    
    URL format: /api/{service}/{path}
    Example: /api/users/register -> forwards to USER_SERVICE/users/register
    """
    
    # Check if service exists
    if service not in settings.SERVICE_MAP:
        raise HTTPException(
            status_code=404,
            detail=f"Service '{service}' not found"
        )
    
    service_url = settings.SERVICE_MAP[service]
    full_path = f"{service}/{path}" if path else service
    
    logger.info(f"Gateway received: /{service}/{path}")
    logger.info(f"Forwarding to: {service_url}/{full_path}")
    
    # Get request body for POST/PUT/PATCH
    body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.json()
        except Exception as e:
            logger.error(f"Error parsing JSON body: {e}")
            body = None
    
    # Get query parameters
    params = dict(request.query_params)
    
    # Get headers
    headers = dict(request.headers)
    
    # Forward request to service
    try:
        response = await forwarder.forward_request(
            service_url=service_url,
            path=full_path,
            method=request.method,
            data=body,
            headers=headers,
            params=params
        )
        
        # Log response status
        logger.info(f"Service responded with status: {response.status_code}")
        
        # Return response from service
        try:
            return response.json()
        except:
            # If response is not JSON, return text
            return {"response": response.text}
        
    except HTTPException as he:
        logger.error(f"HTTP Exception: {he.detail}")
        raise
    except Exception as e:
        logger.error(f"Error proxying request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Gateway error: {str(e)}"
        )

@router.get("/services")
async def list_services():
    """List all available services"""
    return {
        "services": list(settings.SERVICE_MAP.keys()),
        "service_urls": settings.SERVICE_MAP
    }