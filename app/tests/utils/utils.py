import random
import string
import uuid
from typing import Any

from app.core.config import settings
from app.models.player import Player, PlayerFilters


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def get_x_api_key_header() -> dict[str, str]:
    headers = {"x-api-key": f"{settings.API_KEY}"}
    return headers


def get_mock_get_players_by_filters(
    list_range: list[int], n_similar_players: int
) -> Any:
    assigned_players = {}
    for time in list_range:
        time_availability = PlayerFilters.to_time_availability(time)

        assigned_players[time_availability] = {
            "assigned": Player(
                user_public_id=uuid.uuid4(), time_availability=time_availability
            ),
            "similar": [
                Player(user_public_id=uuid.uuid4(), time_availability=time_availability)
                for _ in range(n_similar_players)
            ],
        }

    async def mock_get_players_by_filters(
        self: Any,  # noqa: ARG001
        player_filters: PlayerFilters,  # noqa: ARG001
    ) -> Any:
        time_availability = player_filters.time_availability
        assigned_player = assigned_players[time_availability]["assigned"]  # type: ignore
        similar_players = assigned_players[time_availability]["similar"]  # type: ignore
        if player_filters.user_public_id == assigned_player.user_public_id:  # type: ignore
            return similar_players
        return [assigned_player] + similar_players  # type: ignore

    return mock_get_players_by_filters, assigned_players
