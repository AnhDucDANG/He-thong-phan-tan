import httpx
from fastapi import HTTPException
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class RequestForwarder:
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
    
    async def forward_request(
        self,
        service_url: str,
        path: str,
        method: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> httpx.Response:
        """
        Forward request to microservice
        """
        # ✅ Construct URL properly
        # Remove trailing slash from service_url
        service_url = service_url.rstrip('/')
        # Add leading slash to path if needed
        if not path.startswith('/'):
            path = '/' + path
        
        url = f"{service_url}{path}"
        
        # Loại bỏ headers không cần thiết
        clean_headers = self._clean_headers(headers) if headers else {}
        
        logger.info(f"Forwarding {method} to {url}")
        if data:
            logger.debug(f"Request body: {data}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                
                if method.upper() == "GET":
                    response = await client.get(
                        url,
                        headers=clean_headers,
                        params=params
                    )
                elif method.upper() == "POST":
                    response = await client.post(
                        url,
                        json=data,
                        headers=clean_headers,
                        params=params
                    )
                elif method.upper() == "PUT":
                    response = await client.put(
                        url,
                        json=data,
                        headers=clean_headers,
                        params=params
                    )
                elif method.upper() == "DELETE":
                    response = await client.delete(
                        url,
                        headers=clean_headers,
                        params=params
                    )
                elif method.upper() == "PATCH":
                    response = await client.patch(
                        url,
                        json=data,
                        headers=clean_headers,
                        params=params
                    )
                else:
                    raise HTTPException(
                        status_code=405,
                        detail=f"Method {method} not allowed"
                    )
                
                logger.info(f"Received response: {response.status_code}")
                
                # ✅ Check if service returned error
                if response.status_code >= 400:
                    logger.error(f"Service error: {response.text}")
                    # Forward the error from service
                    try:
                        error_detail = response.json()
                    except:
                        error_detail = response.text
                    
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=error_detail
                    )
                
                return response
                
        except httpx.TimeoutException:
            logger.error(f"Timeout when forwarding to {url}")
            raise HTTPException(
                status_code=504,
                detail="Service timeout"
            )
        except httpx.ConnectError as e:
            logger.error(f"Cannot connect to service at {url}: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Service unavailable: {str(e)}"
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error forwarding request: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Gateway error: {str(e)}"
            )
    
    def _clean_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """
        Remove headers that shouldn't be forwarded
        """
        excluded_headers = {
            'host',
            'content-length',
            'connection',
            'keep-alive',
            'proxy-authenticate',
            'proxy-authorization',
            'te',
            'trailers',
            'transfer-encoding',
            'upgrade'
        }
        
        return {
            key: value for key, value in headers.items()
            if key.lower() not in excluded_headers
        }

# Singleton instance
forwarder = RequestForwarder()