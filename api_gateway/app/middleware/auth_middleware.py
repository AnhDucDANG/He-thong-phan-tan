from fastapi import Request, HTTPException
from typing import Optional
import logging

logger = logging.getLogger(__name__)

PUBLIC_ROUTES = [
    "/",
    "/health",
    "/api/health/all",
    "/api/services",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/users/register",
    "/api/users/login",
]

PUBLIC_ROUTE_PATTERNS = [
    "/api/users/register",
    "/api/users/login",
]

async def verify_authentication(request: Request) -> Optional[dict]:
    path = request.url.path
    
    if path in PUBLIC_ROUTES:
        logger.info(f"Public route accessed: {path}")
        return None
    
    for pattern in PUBLIC_ROUTE_PATTERNS:
        if path.startswith(pattern):
            logger.info(f"Public route accessed: {path}")
            return None
    
    auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
    
    if not auth_header:
        logger.warning(f"No authorization header for protected route: {path}")
        raise HTTPException(
            status_code=401,
            detail="Missing authorization header"
        )
    
    if not auth_header.startswith("Bearer "):
        logger.warning(f"Invalid authorization header format for: {path}")
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format"
        )
    
    logger.info(f"Token found for protected route: {path}")
    return {"authenticated": True}