from datetime import datetime
from typing import Any
from uuid import UUID

from app.core.config import settings
from app.models.player import Player

from .base_service import BaseService


class PlayersService(BaseService):
    def __init__(self) -> None:
        """Init the service."""
        super().__init__()
        self._set_base_url(settings.PLAYERS_SERVICE_HOST, settings.PLAYERS_SERVICE_PORT)
        if settings.PLAYERS_SERVICE_API_KEY:
            self.set_base_headers({"x-api-key": settings.PLAYERS_SERVICE_API_KEY})

    async def get_players_by_filters(
        self: Any,
        latitude: float | None,
        longitude: float | None,
        time_availability: int | None,
        date: datetime | None,
        user_public_id: UUID | None,
        n_players: int | None,
    ) -> list[Player]:
        "Get available times from PLAYERS service"
        day = date.isoweekday() if date else None
        params: dict[str, Any] = {
            "latitude": latitude,
            "longitude": longitude,
            "time_availability": time_availability,
            "available_days": [day],
            "user_public_id": user_public_id,
            "n_players": n_players,
        }
        content = await self.get("/api/v1/players", params=params)
        data = content["data"]
        players = []
        for datum in data:
            player = Player(**datum)
            players.append(player)
        return players
