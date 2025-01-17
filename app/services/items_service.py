from typing import Any

from app.core.config import settings

from .base_service import BaseService


class ItemsService(BaseService):
    def __init__(self) -> None:
        """Init the service."""
        super().__init__()
        self._set_base_url(settings.ITEMS_SERVICE_HOST, settings.ITEMS_SERVICE_PORT)
        if settings.ITEMS_SERVICE_API_KEY:
            self.set_base_headers({"x-api-key": settings.ITEMS_SERVICE_API_KEY})

    async def get_items(self) -> Any:
        """Get items from items service."""
        return await self.get("/api/v2/breeds")
