from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
import logging
from .config import settings

logger = logging.getLogger(__name__)

async def forward_request(request: Request, target_url: str, authorization: str = None):
    """
    Forward HTTP request to target service
    """
    try:
        # Get request data
        body = await request.body()
        
        # Prepare headers
        headers = dict(request.headers)
        headers.pop("host", None)
        
        # Add authorization if provided
        if authorization:
            headers["authorization"] = authorization
        
        logger.info(f"🎯 Forwarding to: {target_url}")
        logger.info(f"📋 Headers: {list(headers.keys())}")
        
        # Create HTTP client with timeout
        async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
            
            # Forward request
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                params=request.query_params,
                follow_redirects=True
            )
            
            logger.info(f"✅ Response: {response.status_code}")
            
            # Parse response
            try:
                if "application/json" in response.headers.get("content-type", ""):
                    content = response.json()
                else:
                    content = {"data": response.text}
            except Exception:
                content = {"data": response.text}
            
            # Build response headers
            response_headers = {}
            for key, value in response.headers.items():
                if key.lower() not in ['content-encoding', 'content-length', 'transfer-encoding', 'connection']:
                    response_headers[key] = value
            
            return JSONResponse(
                content=content,
                status_code=response.status_code,
                headers=response_headers
            )
            
    except httpx.ConnectError as e:
        logger.error(f"❌ Connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Service unavailable: Could not connect to backend service"
        )
    
    except httpx.TimeoutException as e:
        logger.error(f"⏱️ Timeout error: {e}")
        raise HTTPException(
            status_code=504,
            detail="Service timeout: Backend service took too long to respond"
        )
    
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=502,
            detail=f"Bad Gateway: {str(e)}"
        )