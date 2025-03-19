import uuid
from datetime import datetime
from typing import Any

from httpx import AsyncClient

from app.core.config import test_settings
from app.models.available_time import AvailableTime
from app.models.match_player import ReserveStatus
from app.models.player import Player, PlayerFilters
from app.services.business_service import BusinessService
from app.services.match_generator_service import MatchGeneratorService
from app.services.players_service import PlayersService


async def test_generate_matches_given_one_avail_time(
    async_client: AsyncClient, x_api_key_header: dict[str, str], monkeypatch: Any
) -> None:
    # Test ctes
    business_public_id = 1000
    court_public_id = "1"
    date = "2025-03-19"
    time = 9
    latitude = 0.0
    longitude = 0.0
    assigned_user_public_id = uuid.uuid4()
    n_similar_players = 6

    # Mock BusinessService
    avail_times = [
        AvailableTime(
            business_public_id=business_public_id,
            court_public_id=court_public_id,
            latitude=latitude,
            longitude=longitude,
            date=date,
            time=time,
            is_reserved=False,
        )
    ]

    async def mock_get_available_times(
        self: Any,  # noqa: ARG001
        business_public_id: int,  # noqa: ARG001
        court_public_id: str,  # noqa: ARG001
        date: datetime,  # noqa: ARG001
    ) -> Any:
        return avail_times

    monkeypatch.setattr(
        BusinessService, "get_available_times", mock_get_available_times
    )

    # Mock PlayersService
    assigned_player = Player(user_public_id=assigned_user_public_id)
    similar_players = [
        Player(user_public_id=uuid.uuid4()) for _ in range(n_similar_players)
    ]
    similar_players_user_public_ids = [
        str(player.user_public_id) for player in similar_players
    ]
    avail_players = [assigned_player] + similar_players

    async def mock_get_players_by_filters(
        self: Any,  # noqa: ARG001
        player_filters: PlayerFilters,  # noqa: ARG001
    ) -> Any:
        if player_filters.user_public_id == assigned_user_public_id:
            return similar_players
        return avail_players

    monkeypatch.setattr(
        PlayersService, "get_players_by_filters", mock_get_players_by_filters
    )

    # Mock MatchGeneratorService
    def mock_choose_priority_player(
        self: Any,  # noqa: ARG001
        players: list[Player],  # noqa: ARG001
    ) -> Player:
        return assigned_player

    monkeypatch.setattr(
        MatchGeneratorService, "_choose_priority_player", mock_choose_priority_player
    )

    # Main request
    data = {
        "business_public_id": business_public_id,
        "court_public_id": court_public_id,
        "date": date,
    }
    response = await async_client.post(
        f"{test_settings.API_V1_STR}/matches/generation",
        headers=x_api_key_header,
        json=data,
    )

    # Assertions
    assert response.status_code == 201

    matches_list = response.json()
    matches = matches_list["data"]
    assert len(matches) == 1

    match_extended = matches[0]
    # TODO: In Match, add business_public_id
    # assert match_extended["business_public_id"] == business_public_id
    # TODO: In Match, rename court_id to court_public_id
    assert match_extended["court_id"] == court_public_id
    assert match_extended["date"] == date
    assert match_extended["time"] == time

    match_players = match_extended["match_players"]
    match_assigned_players = [
        player
        for player in match_players
        if player["reserve"] == ReserveStatus.Assigned
    ]
    assert len(match_assigned_players) == 1

    match_assigned_player = match_assigned_players[0]
    assert match_assigned_player["user_public_id"] == str(
        assigned_player.user_public_id
    )

    match_similar_players_user_public_ids = [
        player["user_public_id"]
        for player in match_players
        if player["reserve"] == ReserveStatus.Similar
    ]
    assert set(match_similar_players_user_public_ids) == set(
        similar_players_user_public_ids
    )


async def test_generate_matches_given_three_avail_time(
    async_client: AsyncClient, x_api_key_header: dict[str, str], monkeypatch: Any
) -> None:
    # Test ctes
    business_public_id = 1000
    court_public_id = "1"
    date = "2025-03-19"
    times = [8, 9, 10]
    latitude = 0.0
    longitude = 0.0
    n_similar_players = 6

    # Mock BusinessService
    avail_times = [
        AvailableTime(
            business_public_id=business_public_id,
            court_public_id=court_public_id,
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
        business_public_id: int,  # noqa: ARG001
        court_public_id: str,  # noqa: ARG001
        date: datetime,  # noqa: ARG001
    ) -> Any:
        return avail_times

    monkeypatch.setattr(
        BusinessService, "get_available_times", mock_get_available_times
    )

    # Mock PlayersService
    assigned_players = {}
    for time in times:
        assigned_players[time] = {
            "assigned": Player(user_public_id=uuid.uuid4(), time_availability=time),
            "similar": [
                Player(user_public_id=uuid.uuid4(), time_availability=time)
                for _ in range(n_similar_players)
            ],
        }

    async def mock_get_players_by_filters(
        self: Any,  # noqa: ARG001
        player_filters: PlayerFilters,  # noqa: ARG001
    ) -> Any:
        time = player_filters.time_availability
        assigned_player = assigned_players[time]["assigned"]  # type: ignore
        similar_players = assigned_players[time]["similar"]  # type: ignore
        if player_filters.user_public_id == assigned_player.user_public_id:  # type: ignore
            return similar_players
        return [assigned_player] + similar_players  # type: ignore

    monkeypatch.setattr(
        PlayersService, "get_players_by_filters", mock_get_players_by_filters
    )

    # Mock MatchGeneratorService
    def mock_choose_priority_player(
        self: Any,  # noqa: ARG001
        players: list[Player],  # noqa: ARG001
    ) -> Player:
        time = players[0].time_availability
        return assigned_players[time]["assigned"]  # type: ignore

    monkeypatch.setattr(
        MatchGeneratorService, "_choose_priority_player", mock_choose_priority_player
    )

    # Main request
    data = {
        "business_public_id": business_public_id,
        "court_public_id": court_public_id,
        "date": date,
    }
    response = await async_client.post(
        f"{test_settings.API_V1_STR}/matches/generation",
        headers=x_api_key_header,
        json=data,
    )

    # Assertions
    assert response.status_code == 201

    matches_list = response.json()
    matches = matches_list["data"]
    assert len(matches) == 3

    for match_extended in matches:
        # TODO: In Match, add business_public_id
        # assert match_extended["business_public_id"] == business_public_id
        # TODO: In Match, rename court_id to court_public_id
        assert match_extended["court_id"] == court_public_id
        assert match_extended["date"] == date
        assert match_extended["time"] in times
        time = match_extended["time"]
        assigned_player = assigned_players[time]["assigned"]
        similar_players = assigned_players[time]["similar"]
        similar_players_user_public_ids = [
            str(player.user_public_id)
            for player in similar_players  # type: ignore
        ]

        match_players = match_extended["match_players"]
        match_assigned_players = [
            player
            for player in match_players
            if player["reserve"] == ReserveStatus.Assigned
        ]
        assert len(match_assigned_players) == 1

        match_assigned_player = match_assigned_players[0]
        assert match_assigned_player["user_public_id"] == str(
            assigned_player.user_public_id  # type: ignore
        )

        match_similar_players_user_public_ids = [
            player["user_public_id"]
            for player in match_players
            if player["reserve"] == ReserveStatus.Similar
        ]
        assert set(match_similar_players_user_public_ids) == set(
            similar_players_user_public_ids
        )
