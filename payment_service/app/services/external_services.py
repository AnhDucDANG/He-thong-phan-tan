import httpx
from app.config import settings

class ExternalServices:
    async def get_booking(self, booking_id: str) -> dict:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.BOOKING_SERVICE_URL}/api/v1/bookings/{booking_id}",
                    timeout=10.0
                )
                if response.status_code == 200:
                    return response.json()
                return None
        except Exception:
            return None

    async def get_user(self, user_id: str) -> dict:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.USER_SERVICE_URL}/api/v1/users/{user_id}",
                    timeout=10.0
                )
                if response.status_code == 200:
                    return response.json()
                return None
        except Exception:
            return None

    async def update_booking_status(self, booking_id: str, status: str) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{settings.BOOKING_SERVICE_URL}/api/v1/bookings/{booking_id}/status",
                    json={"status": status},
                    timeout=10.0
                )
                return response.status_code == 200
        except Exception:
            return False