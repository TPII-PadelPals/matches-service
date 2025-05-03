import uuid
from typing import Any

from ..core.config import settings
from ..models.message import BotMessage
from .base_service import BaseService
from .users_service import UserService


class BotService(BaseService):
    MESSAGE_NEW_MATCH: str = "NEW_MATCH"

    def __init__(self) -> None:
        """Init the service."""
        super().__init__()
        self._set_base_url(
            is_http=True,
            host=settings.BOT_SERVICE_HOST,
            port=settings.BOT_SERVICE_PORT,
        )
        if settings.BOT_SERVICE_API_KEY:
            self.set_base_headers({"x-api-key": settings.BOT_SERVICE_API_KEY})

    async def send_message(self, message: BotMessage) -> Any:
        """Send message with the bot."""
        return await self.post("/messages", data=message.model_dump())

    async def send_messages(self, messages: list[BotMessage]) -> Any:
        """Send messages with the bot."""
        return await self.post(
            "/messages/bulk", json=[message.model_dump() for message in messages]
        )

    async def send_new_matches(self, user_public_ids: list[uuid.UUID]) -> Any:
        if not user_public_ids:
            return None
        messages: list[BotMessage] = []
        user_service = UserService()
        for user_public_id in user_public_ids:
            telegram_id = await user_service.get_telegram_id(user_public_id)
            message = BotMessage(
                chat_id=telegram_id,
                message=self.MESSAGE_NEW_MATCH,
            )
            messages.append(message)
        return await self.send_messages(messages)
