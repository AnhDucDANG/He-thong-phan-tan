from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
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
        
        # Log request details
        if body:
            try:
                body_preview = body[:200].decode('utf-8')
                logger.info(f"📦 Request body preview: {body_preview}...")
            except:
                logger.info(f"📦 Request body size: {len(body)} bytes")
        else:
            logger.info("📦 Request body: (empty)")
        
        # Prepare headers (forward all headers except host)
        headers = dict(request.headers)
        headers.pop("host", None)
        
        logger.info(f"🎯 Target URL: {target_url}")
        logger.info(f"📋 Query params: {dict(request.query_params)}")
        
        # Create HTTP client with timeout
        async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
            
            # Forward request
            logger.info(f"🚀 Sending {request.method} request...")
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                params=request.query_params,
                follow_redirects=True
            )
            
            logger.info(f"✅ Received response: {response.status_code}")
            logger.info(f"📄 Response content-type: {response.headers.get('content-type')}")
            
            # ✅ PARSE RESPONSE CORRECTLY
            try:
                # Try to parse as JSON
                if "application/json" in response.headers.get("content-type", ""):
                    content = response.json()
                    logger.info(f"📦 Response JSON: {str(content)[:200]}...")
                else:
                    content = response.text
                    logger.info(f"📦 Response text: {content[:200]}...")
            except Exception as parse_error:
                logger.warning(f"⚠️ Failed to parse response: {parse_error}")
                content = {"detail": response.text}
            
            # ✅ BUILD RESPONSE WITH PROPER HEADERS
            response_headers = {}
            for key, value in response.headers.items():
                # Skip headers that shouldn't be forwarded
                if key.lower() not in ['content-encoding', 'content-length', 'transfer-encoding', 'connection']:
                    response_headers[key] = value
            
            # Return response
            return JSONResponse(
                content=content,
                status_code=response.status_code,
                headers=response_headers
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
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    
    except Exception as e:
        logger.error(f"❌ Unexpected error forwarding to {target_url}: {e}", exc_info=True)
        raise HTTPException(
            status_code=502,
            detail=f"Bad Gateway: {str(e)}"
        )