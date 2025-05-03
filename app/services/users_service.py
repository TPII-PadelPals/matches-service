import uuid

from app.core.config import settings
from app.services.base_service import BaseService


class UserService(BaseService):
    def __init__(self) -> None:
        """Init the service."""
        super().__init__()
        self._set_base_url(
            is_http=True,
            host=settings.USER_SERVICE_HOST,
            port=settings.USER_SERVICE_PORT,
        )
        if settings.USER_SERVICE_API_KEY:
            self.set_base_headers({"x-api-key": settings.USER_SERVICE_API_KEY})

    async def get_telegram_id(self, user_public_id: uuid.UUID) -> int:
        response = await self.get(f"/api/v1/users/{user_public_id}")
        content = response.json()
        return int(content["telegram_id"])
