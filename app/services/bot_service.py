import uuid
from typing import Any

from ..core.config import settings
from ..models.message import BotMessage
from .base_service import BaseService


class BotService(BaseService):
    def __init__(self) -> None:
        """Init the service."""
        super().__init__()
        self._set_base_url(
            is_http=True,
            host=settings.BOT_SERVICE_HOST,
            port=settings.BOT_SERVICE_PORT,
        )
        if settings.PLAYERS_SERVICE_API_KEY:
            self.set_base_headers({"x-api-key": settings.PLAYERS_SERVICE_API_KEY})

    async def send_message(self, message: BotMessage) -> Any:
        """Send message with the bot."""
        return await self.post("/messages", data=message.model_dump())

    async def send_messages(self, messages: list[BotMessage]) -> Any:
        """Send messages with the bot."""
        return await self.post(
            "/messages/bulk", json=[message.model_dump() for message in messages]
        )

    async def send_new_matches(self, user_public_ids: list[uuid.UUID]) -> None:
        _messages: list[BotMessage] = []
