from fastapi import Request, HTTPException
from typing import Optional

PUBLIC_PATHS = [
    "/",
    "/health",
    "/docs",
    "/openapi.json",
    "/users/register",
    "/users/login",
]

def is_public_path(path: str) -> bool:
    """Check if path is public (doesn't require authentication)"""
    for public_path in PUBLIC_PATHS:
        if path.startswith(public_path):
            return True
    return False

def extract_token(request: Request) -> Optional[str]:
    """Extract JWT token from Authorization header"""
    auth_header = request.headers.get("authorization")
    
    if not auth_header:
        return None
    
    if not auth_header.startswith("Bearer "):
        return None
    
    return auth_header.replace("Bearer ", "")

async def verify_authentication(request: Request):
    """
    Verify if request has valid authentication
    Gateway doesn't validate JWT, just checks if token exists
    Actual validation is done by User Service
    """
    path = request.url.path
    
    # Skip authentication for public paths
    if is_public_path(path):
        return
    
    # Check if Authorization header exists
    token = extract_token(request)
    
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Missing authentication token"
        )