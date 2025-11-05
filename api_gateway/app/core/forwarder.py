from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
import httpx
import logging
from .config import settings

logger = logging.getLogger(__name__)

async def forward_request(request: Request, target_url: str):
    """
    Forward HTTP request to target service
    """
    try:
        # Get request data
        body = await request.body()
        
        # Prepare headers (forward all headers except host)
        headers = dict(request.headers)
        headers.pop("host", None)
        
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
            
            # Return response
            return JSONResponse(
                content=response.json() if response.headers.get("content-type") == "application/json" else response.text,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
            
    except httpx.ConnectError as e:
        logger.error(f"❌ Connection error to {target_url}: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: Could not connect to backend service"
        )
    
    except httpx.TimeoutException as e:
        logger.error(f"⏱️ Timeout error to {target_url}: {e}")
        raise HTTPException(
            status_code=504,
            detail=f"Service timeout: Backend service took too long to respond"
        )
    
    except Exception as e:
        logger.error(f"❌ Unexpected error forwarding to {target_url}: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"Bad Gateway: {str(e)}"
        )