from typing import Any

from app.core.config import settings
from app.models.player import Player, PlayerFilters

from .base_service import BaseService


class PlayersService(BaseService):
    def __init__(self) -> None:
        """Init the service."""
        super().__init__()
        self._set_base_url(
            is_http=True,
            host=settings.PLAYERS_SERVICE_HOST,
            port=settings.PLAYERS_SERVICE_PORT,
        )
        if settings.PLAYERS_SERVICE_API_KEY:
            self.set_base_headers({"x-api-key": settings.PLAYERS_SERVICE_API_KEY})

    async def get_players_by_filters(
        self: Any, player_filters: PlayerFilters
    ) -> list[Player]:
        "Get players by filters from players service"
        content = await self.get(
            "/api/v1/players/", params=player_filters.model_dump(exclude_none=True)
        )
        players_data = content["data"]
        players = []
        for player_data in players_data:
            player = Player(**player_data)
            players.append(player)
        return players
