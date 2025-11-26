import asyncio
import httpx
from httpx import HTTPStatusError, RequestError
from app.core.config import settings
from typing import Dict, Any, Union, Optional
from datetime import date, datetime

client = httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT)

async def check_service_availability(base_url: str, endpoint: str) -> httpx.Response:
    """Gọi API GET/HEAD để kiểm tra một service có sẵn hay không."""
    url = f"{base_url}{endpoint}"
    try:
        response = await client.head(url)
        response.raise_for_status() # Ném lỗi nếu status >= 400
        return response
    except httpx.HTTPStatusError as e:
        # Xử lý các lỗi HTTP cụ thể (ví dụ: 404, 403)
        raise e
    except httpx.RequestError as e:
        # Xử lý lỗi kết nối, timeout, DNS (Service down/unreachable)
        raise Exception(f"External service connection error to {url}: {e}") from e

async def post_request(base_url: str, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Gửi Request POST đến một service bên ngoài."""
    url = f"{base_url}{endpoint}"
    try:
        response = await client.post(
            url,
            json=data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        # Ném lỗi HTTP (ví dụ: 400 Bad Request, 403 Forbidden)
        raise e
    except httpx.RequestError as e:
        # Lỗi kết nối
        raise Exception(f"External POST connection error to {url}: {e}") from e

def build_url(base_url: str, endpoint: str) -> str:
    return f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"

async def get_request(base_url: str, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Gửi Request GET đến một service bên ngoài."""
    url = build_url(base_url, endpoint)
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()

    except httpx.RequestError as e:
        print("GET ERROR:", repr(e))
        raise Exception(f"External GET connection error: {repr(e)}") from e