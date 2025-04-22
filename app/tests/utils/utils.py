import datetime
import random
import string
import uuid
from typing import Any

from app.core.config import settings
from app.models.available_time import AvailableTime
from app.models.player import Player, PlayerFilters
from app.services.business_service import BusinessService
from app.services.match_generator_service import MatchGeneratorService
from app.services.players_service import PlayersService


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


def get_mock_get_available_times(
    business_public_id: str,
    court_public_id: str,
    court_name: str,
    date: str,
    times: list[int],
    latitude: float,
    longitude: float,
) -> Any:
    avail_times = [
        AvailableTime(
            business_public_id=business_public_id,
            court_public_id=court_public_id,
            court_name=court_name,
            latitude=latitude,
            longitude=longitude,
            date=date,
            time=time,
            is_reserved=False,
        )
        for time in times
    ]

    async def mock_get_available_times(
        self: Any,  # noqa: ARG001
        business_public_id: uuid.UUID,  # noqa: ARG001
        court_name: str,  # noqa: ARG001
        date: datetime.date,  # noqa: ARG001
    ) -> Any:
        return avail_times

    return mock_get_available_times


def initial_apply_mocks_for_generate_matches(
    monkeypatch: Any,
    business_public_id: str,
    court_public_id: str,
    court_name: str,
    date: str,
    times: list[int],
    all_times: list[int],
    latitude: float,
    longitude: float,
    n_similar_players: int,
) -> dict[int, dict[str, Any]]:
    # Mock BusinessService
    mock_get_available_times = get_mock_get_available_times(
        business_public_id,
        court_public_id,
        court_name,
        date,
        times,
        latitude,
        longitude,
    )
    monkeypatch.setattr(
        BusinessService, "get_available_times", mock_get_available_times
    )

    # Mock PlayersService
    mock_get_players_by_filters, assigned_players = get_mock_get_players_by_filters(
        all_times, n_similar_players
    )
    monkeypatch.setattr(
        PlayersService, "get_players_by_filters", mock_get_players_by_filters
    )

    # Mock MatchGeneratorService
    def mock_choose_priority_player(
        self: Any,  # noqa: ARG001
        players: list[Player],  # noqa: ARG001
    ) -> Player:
        time_availability = players[0].time_availability
        return assigned_players[time_availability]["assigned"]  # type: ignore

    monkeypatch.setattr(
        MatchGeneratorService, "_choose_priority_player", mock_choose_priority_player
    )

    return assigned_players  # type: ignore
