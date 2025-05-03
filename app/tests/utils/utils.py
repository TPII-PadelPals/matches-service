import datetime
import random
import string
import uuid
from typing import Any
from unittest.mock import Mock

from app.core.config import settings
from app.models.available_time import AvailableTime
from app.models.court import Court
from app.models.message import BotMessage
from app.models.player import Player, PlayerFilters
from app.services.bot_service import BotService
from app.services.business_service import BusinessService
from app.services.match_generator_service import MatchGeneratorService
from app.services.players_service import PlayersService
from app.services.users_service import UserService


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def get_x_api_key_header() -> dict[str, str]:
    headers = {"x-api-key": f"{settings.API_KEY}"}
    return headers


def get_mock_get_players_by_filters(**match_data: Any) -> Any:
    assigned_players = {}
    for time in match_data["all_times"]:
        time_avail = PlayerFilters.to_time_availability(time)

        assigned_players[time_avail] = {
            "assigned": Player(
                user_public_id=uuid.uuid4(), time_availability=time_avail
            ),
            "similar": [
                Player(user_public_id=uuid.uuid4(), time_availability=time_avail)
                for _ in range(match_data["n_similar_players"])
            ],
        }

    async def mock_get_players_by_filters(
        self: Any,  # noqa: ARG001
        player_filters: PlayerFilters,  # noqa: ARG001
    ) -> Any:
        time_avail = player_filters.time_availability
        if time_avail is None:
            raise ValueError()
        assigned_player = assigned_players[time_avail]["assigned"]
        similar_players = assigned_players[time_avail]["similar"]
        if player_filters.user_public_id == assigned_player.user_public_id:  # type: ignore
            return similar_players
        return [assigned_player] + similar_players  # type: ignore

    return mock_get_players_by_filters, assigned_players


def get_mock_get_courts(**match_data: Any) -> Any:
    courts = []
    for court_public_id, court_name in zip(
        match_data["court_public_ids"], match_data["court_names"], strict=False
    ):
        courts.append(
            Court(
                business_public_id=match_data["business_public_id"],
                court_public_id=court_public_id,
                court_name=court_name,
                price_per_hour=0.0,
            )
        )

    async def mock_get_courts(
        self: Any,  # noqa: ARG001
        business_public_id: uuid.UUID,  # noqa: ARG001
    ) -> Any:
        return courts

    return mock_get_courts


def get_mock_get_available_times(**match_data: Any) -> Any:
    avail_times = {}
    for court_public_id, court_name in zip(
        match_data["court_public_ids"], match_data["court_names"], strict=False
    ):
        avail_times[court_name] = [
            AvailableTime(
                court_public_id=court_public_id,
                court_name=court_name,
                time=time,
                **match_data,
            )
            for time in match_data["times"]
        ]

    async def mock_get_available_times(
        self: Any,  # noqa: ARG001
        business_public_id: uuid.UUID,  # noqa: ARG001
        court_name: str,
        date: datetime.date,  # noqa: ARG001
    ) -> Any:
        return avail_times[court_name]

    return mock_get_available_times


def get_mock_send_messages_disable() -> Any:
    async def send_new_matches(
        self: Any,  # noqa: ARG001
        user_public_ids: list[uuid.UUID],  # noqa: ARG001
    ) -> Any:
        return None

    return send_new_matches


def set_mock_send_messages(monkeypatch: Any) -> Any:
    mock_get_telegram_id = Mock(return_value=0)

    async def get_telegram_id(
        self: Any,  # noqa: ARG001
        user_public_id: uuid.UUID,  # noqa: ARG001
    ) -> Any:
        return mock_get_telegram_id()

    monkeypatch.setattr(UserService, "get_telegram_id", get_telegram_id)

    mock_send_messages = Mock()

    async def send_messages(
        self: Any,  # noqa: ARG001
        messages: list[BotMessage],  # noqa: ARG001
    ) -> Any:
        """Send messages with the bot."""
        return mock_send_messages()

    monkeypatch.setattr(BotService, "send_messages", send_messages)
    return mock_get_telegram_id, mock_send_messages


def initial_apply_mocks_for_generate_matches(
    monkeypatch: Any, **match_data: Any
) -> dict[int, dict[str, Any]]:
    # Mock BusinessService Courts
    mock_get_courts = get_mock_get_courts(**match_data)
    monkeypatch.setattr(BusinessService, "get_courts", mock_get_courts)

    # Mock BusinessService AvailableTimes
    mock_get_available_times = get_mock_get_available_times(**match_data)
    monkeypatch.setattr(
        BusinessService, "get_available_times", mock_get_available_times
    )

    # Mock PlayersService
    mock_get_players_by_filters, assigned_players = get_mock_get_players_by_filters(
        **match_data
    )
    monkeypatch.setattr(
        PlayersService, "get_players_by_filters", mock_get_players_by_filters
    )

    # Mock MatchGeneratorService
    def mock_choose_priority_player(
        self: Any,  # noqa: ARG001
        players: list[Player],  # noqa: ARG001
    ) -> Player:
        time_avail = players[0].time_availability
        return assigned_players[time_avail]["assigned"]  # type: ignore

    monkeypatch.setattr(
        MatchGeneratorService, "_choose_priority_player", mock_choose_priority_player
    )

    if (
        not match_data.get("WHITOUT_MESSAGE")
        and match_data.get("WHITOUT_MESSAGE") is None
    ):
        mock_send_messages = get_mock_send_messages_disable()
        monkeypatch.setattr(BotService, "send_new_matches", mock_send_messages)

    return assigned_players  # type: ignore
