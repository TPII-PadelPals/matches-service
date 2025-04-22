import datetime
import uuid
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
    business_public_id = str(uuid.uuid4())
    court_name = "1"
    court_public_id = str(uuid.uuid4())
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
            court_name=court_name,
            latitude=latitude,
            longitude=longitude,
            date=date,
            time=time,
            is_reserved=False,
        )
    ]

    async def mock_get_available_times(
        self: Any,  # noqa: ARG001
        business_public_id: uuid.UUID,  # noqa: ARG001
        court_name: str,  # noqa: ARG001
        date: datetime.date,  # noqa: ARG001
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
        "court_name": court_name,
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
    assert match_extended["court_public_id"] == court_public_id
    assert match_extended["court_name"] == court_name
    assert match_extended["date"] == date
    assert match_extended["time"] == time

    match_players = match_extended["match_players"]
    match_assigned_players = [
        player
        for player in match_players
        if player["reserve"] == ReserveStatus.ASSIGNED
    ]
    assert len(match_assigned_players) == 1

    match_assigned_player = match_assigned_players[0]
    assert match_assigned_player["user_public_id"] == str(
        assigned_player.user_public_id
    )

    match_similar_players_user_public_ids = [
        player["user_public_id"]
        for player in match_players
        if player["reserve"] == ReserveStatus.SIMILAR
    ]
    assert set(match_similar_players_user_public_ids) == set(
        similar_players_user_public_ids
    )


async def test_generate_matches_given_three_avail_time(
    async_client: AsyncClient, x_api_key_header: dict[str, str], monkeypatch: Any
) -> None:
    # Test ctes
    business_public_id = str(uuid.uuid4())
    court_public_id = str(uuid.uuid4())
    court_name = "1"
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

    monkeypatch.setattr(
        BusinessService, "get_available_times", mock_get_available_times
    )

    # Mock PlayersService
    assigned_players = {}
    for time in times:
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

    # Main request
    data = {
        "business_public_id": business_public_id,
        "court_name": court_name,
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
        assert match_extended["court_public_id"] == court_public_id
        assert match_extended["court_name"] == court_name
        assert match_extended["date"] == date
        assert match_extended["time"] in times
        time = match_extended["time"]
        time_availability = PlayerFilters.to_time_availability(time)
        assigned_player = assigned_players[time_availability]["assigned"]
        similar_players = assigned_players[time_availability]["similar"]
        similar_players_user_public_ids = [
            str(player.user_public_id)
            for player in similar_players  # type: ignore
        ]

        match_players = match_extended["match_players"]
        match_assigned_players = [
            player
            for player in match_players
            if player["reserve"] == ReserveStatus.ASSIGNED
        ]
        assert len(match_assigned_players) == 1

        match_assigned_player = match_assigned_players[0]
        assert match_assigned_player["user_public_id"] == str(
            assigned_player.user_public_id  # type: ignore
        )

        match_similar_players_user_public_ids = [
            player["user_public_id"]
            for player in match_players
            if player["reserve"] == ReserveStatus.SIMILAR
        ]
        assert set(match_similar_players_user_public_ids) == set(
            similar_players_user_public_ids
        )


async def test_generate_matches_twice_for_the_same_day_and_same_times(
    async_client: AsyncClient, x_api_key_header: dict[str, str], monkeypatch: Any
) -> None:
    # Test ctes
    business_public_id = str(uuid.uuid4())
    court_public_id = str(uuid.uuid4())
    court_name = "1"
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

    monkeypatch.setattr(
        BusinessService, "get_available_times", mock_get_available_times
    )

    # Mock PlayersService
    assigned_players = {}
    for time in times:
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

    # Main request
    data = {
        "business_public_id": business_public_id,
        "court_name": court_name,
        "date": date,
    }
    response = await async_client.post(
        f"{test_settings.API_V1_STR}/matches/generation",
        headers=x_api_key_header,
        json=data,
    )

    assert response.status_code == 201

    matches_list = response.json()
    matches = matches_list["data"]
    assert len(matches) == 3
    # TEST

    response_for_new_generate = await async_client.post(
        f"{test_settings.API_V1_STR}/matches/generation",
        headers=x_api_key_header,
        json=data,
    )
    # ASSERT
    assert response_for_new_generate.status_code == 201
    new_matches_list = response_for_new_generate.json()
    new_matches = new_matches_list["data"]
    assert len(new_matches) == 0


async def test_generate_matches_twice_for_the_same_day_and_new_times(
    async_client: AsyncClient, x_api_key_header: dict[str, str], monkeypatch: Any
) -> None:
    # Test ctes
    business_public_id = str(uuid.uuid4())
    court_public_id = str(uuid.uuid4())
    court_name = "1"
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

    monkeypatch.setattr(
        BusinessService, "get_available_times", mock_get_available_times
    )

    # Mock PlayersService
    assigned_players = {}
    for time in times:
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

    # Main request
    data = {
        "business_public_id": business_public_id,
        "court_name": court_name,
        "date": date,
    }
    response = await async_client.post(
        f"{test_settings.API_V1_STR}/matches/generation",
        headers=x_api_key_header,
        json=data,
    )

    assert response.status_code == 201

    matches_list = response.json()
    matches = matches_list["data"]
    assert len(matches) == 3

    # add times
    new_times = [6, 7, 8, 9, 10, 11, 12]
    # Mock BusinessService
    new_avail_times = [
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
        for time in new_times
    ]

    async def mock_get_available_times_new(
        self: Any,  # noqa: ARG001
        business_public_id: uuid.UUID,  # noqa: ARG001
        court_name: str,  # noqa: ARG001
        date: datetime.date,  # noqa: ARG001
    ) -> Any:
        return new_avail_times

    monkeypatch.setattr(
        BusinessService, "get_available_times", mock_get_available_times_new
    )
    # Mock PlayersService
    assigned_players = {}
    for time in new_times:
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

    async def mock_get_players_by_filters_new(
        self: Any,  # noqa: ARG001
        player_filters: PlayerFilters,  # noqa: ARG001
    ) -> Any:
        time_availability = player_filters.time_availability
        assigned_player = assigned_players[time_availability]["assigned"]  # type: ignore
        similar_players = assigned_players[time_availability]["similar"]  # type: ignore
        if player_filters.user_public_id == assigned_player.user_public_id:  # type: ignore
            return similar_players
        return [assigned_player] + similar_players  # type: ignore

    monkeypatch.setattr(
        PlayersService, "get_players_by_filters", mock_get_players_by_filters_new
    )
    # TEST

    response_for_new_generate = await async_client.post(
        f"{test_settings.API_V1_STR}/matches/generation",
        headers=x_api_key_header,
        json=data,
    )
    # ASSERT
    diff_times = [6, 7, 11, 12]
    assert response_for_new_generate.status_code == 201
    new_matches_list = response_for_new_generate.json()
    new_matches = new_matches_list["data"]
    assert len(new_matches) == 4
    for match_extended in new_matches:
        # TODO: In Match, add business_public_id
        # assert match_extended["business_public_id"] == business_public_id
        assert match_extended["court_public_id"] == court_public_id
        assert match_extended["court_name"] == court_name
        assert match_extended["date"] == date
        assert match_extended["time"] in diff_times
        time = match_extended["time"]
        time_availability = PlayerFilters.to_time_availability(time)
        assigned_player = assigned_players[time_availability]["assigned"]
        similar_players = assigned_players[time_availability]["similar"]
        similar_players_user_public_ids = [
            str(player.user_public_id)
            for player in similar_players  # type: ignore
        ]

        match_players = match_extended["match_players"]
        match_assigned_players = [
            player
            for player in match_players
            if player["reserve"] == ReserveStatus.ASSIGNED
        ]
        assert len(match_assigned_players) == 1

        match_assigned_player = match_assigned_players[0]
        assert match_assigned_player["user_public_id"] == str(
            assigned_player.user_public_id  # type: ignore
        )

        match_similar_players_user_public_ids = [
            player["user_public_id"]
            for player in match_players
            if player["reserve"] == ReserveStatus.SIMILAR
        ]
        assert set(match_similar_players_user_public_ids) == set(
            similar_players_user_public_ids
        )


async def test_generate_matches_for_the_same_with_new_times_twice(
    async_client: AsyncClient, x_api_key_header: dict[str, str], monkeypatch: Any
) -> None:
    # Test ctes
    business_public_id = str(uuid.uuid4())
    court_public_id = str(uuid.uuid4())
    court_name = "1"
    date = "2025-03-19"
    times = [8, 9, 10]
    latitude = 0.0
    longitude = 0.0
    n_similar_players = 6

    # add times
    new_times = [6, 7, 8, 9, 10, 11, 12]

    # Mock BusinessService
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

    monkeypatch.setattr(
        BusinessService, "get_available_times", mock_get_available_times
    )

    # Mock PlayersService
    assigned_players = {}
    for time in new_times:
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

    # Main request
    data = {
        "business_public_id": business_public_id,
        "court_name": court_name,
        "date": date,
    }
    response = await async_client.post(
        f"{test_settings.API_V1_STR}/matches/generation",
        headers=x_api_key_header,
        json=data,
    )

    assert response.status_code == 201

    matches_list = response.json()
    matches = matches_list["data"]
    assert len(matches) == 3

    # Mock BusinessService
    new_avail_times = [
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
        for time in new_times
    ]

    async def mock_get_available_times_new(
        self: Any,  # noqa: ARG001
        business_public_id: uuid.UUID,  # noqa: ARG001
        court_name: str,  # noqa: ARG001
        date: datetime.date,  # noqa: ARG001
    ) -> Any:
        return new_avail_times

    monkeypatch.setattr(
        BusinessService, "get_available_times", mock_get_available_times_new
    )
    # Mock PlayersService
    # assigned_players = {}
    # for time in new_times:
    #     time_availability = PlayerFilters.to_time_availability(time)
    #
    #     assigned_players[time_availability] = {
    #         "assigned": Player(
    #             user_public_id=uuid.uuid4(), time_availability=time_availability
    #         ),
    #         "similar": [
    #             Player(user_public_id=uuid.uuid4(), time_availability=time_availability)
    #             for _ in range(n_similar_players)
    #         ],
    #     }
    #
    # async def mock_get_players_by_filters_new(
    #     self: Any,  # noqa: ARG001
    #     player_filters: PlayerFilters,  # noqa: ARG001
    # ) -> Any:
    #     time_availability = player_filters.time_availability
    #     assigned_player = assigned_players[time_availability]["assigned"]  # type: ignore
    #     similar_players = assigned_players[time_availability]["similar"]  # type: ignore
    #     if player_filters.user_public_id == assigned_player.user_public_id:  # type: ignore
    #         return similar_players
    #     return [assigned_player] + similar_players  # type: ignore
    #
    # monkeypatch.setattr(
    #     PlayersService, "get_players_by_filters", mock_get_players_by_filters_new
    # )

    response_for_new_generate = await async_client.post(
        f"{test_settings.API_V1_STR}/matches/generation",
        headers=x_api_key_header,
        json=data,
    )
    assert response_for_new_generate.status_code == 201
    new_matches_list = response_for_new_generate.json()
    new_matches = new_matches_list["data"]
    assert len(new_matches) == 4
    # TEST

    response_for_new_generate_double = await async_client.post(
        f"{test_settings.API_V1_STR}/matches/generation",
        headers=x_api_key_header,
        json=data,
    )
    # ASSERT
    assert response_for_new_generate_double.status_code == 201
    new_matches_list_generate_double = response_for_new_generate_double.json()
    new_matches_generate_double = new_matches_list_generate_double["data"]
    assert len(new_matches_generate_double) == 0


async def test_generate_matches_multiple_for_the_same_day(
    async_client: AsyncClient, x_api_key_header: dict[str, str], monkeypatch: Any
) -> None:
    # Test ctes
    business_public_id = str(uuid.uuid4())
    court_public_id = str(uuid.uuid4())
    court_name = "1"
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

    monkeypatch.setattr(
        BusinessService, "get_available_times", mock_get_available_times
    )

    # Mock PlayersService
    assigned_players = {}
    for time in range(8, 20):
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

    # Main request
    data = {
        "business_public_id": business_public_id,
        "court_name": court_name,
        "date": date,
    }
    response = await async_client.post(
        f"{test_settings.API_V1_STR}/matches/generation",
        headers=x_api_key_header,
        json=data,
    )

    assert response.status_code == 201

    matches_list = response.json()
    matches = matches_list["data"]
    assert len(matches) == 3

    for new_hour in range(11, 20):
        # add times
        times.append(new_hour)

        # Mock BusinessService
        async def mock_get_available_times_new(
            self: Any,  # noqa: ARG001
            business_public_id: uuid.UUID,  # noqa: ARG001
            court_name: str,  # noqa: ARG001
            date: datetime.date,  # noqa: ARG001
        ) -> Any:
            return [
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

        monkeypatch.setattr(
            BusinessService, "get_available_times", mock_get_available_times_new
        )
        # test

        response_for_new_generate = await async_client.post(
            f"{test_settings.API_V1_STR}/matches/generation",
            headers=x_api_key_header,
            json=data,
        )
        assert response_for_new_generate.status_code == 201
        new_matches_list = response_for_new_generate.json()
        new_matches = new_matches_list["data"]
        assert len(new_matches) == 1
        match_extended = new_matches[0]
        assert match_extended["court_public_id"] == court_public_id
        assert match_extended["court_name"] == court_name
        assert match_extended["date"] == date
        assert match_extended["time"] == new_hour
        time = match_extended["time"]
        time_availability = PlayerFilters.to_time_availability(time)
        assigned_player = assigned_players[time_availability]["assigned"]
        similar_players = assigned_players[time_availability]["similar"]
        similar_players_user_public_ids = [
            str(player.user_public_id)
            for player in similar_players  # type: ignore
        ]

        match_players = match_extended["match_players"]
        match_assigned_players = [
            player
            for player in match_players
            if player["reserve"] == ReserveStatus.ASSIGNED
        ]
        assert len(match_assigned_players) == 1

        match_assigned_player = match_assigned_players[0]
        assert match_assigned_player["user_public_id"] == str(
            assigned_player.user_public_id  # type: ignore
        )

        match_similar_players_user_public_ids = [
            player["user_public_id"]
            for player in match_players
            if player["reserve"] == ReserveStatus.SIMILAR
        ]
        assert set(match_similar_players_user_public_ids) == set(
            similar_players_user_public_ids
        )


async def test_generate_matches_multiple_for_the_same_day_inverse_time(
    async_client: AsyncClient, x_api_key_header: dict[str, str], monkeypatch: Any
) -> None:
    # Test ctes
    business_public_id = str(uuid.uuid4())
    court_public_id = str(uuid.uuid4())
    court_name = "1"
    date = "2025-03-19"
    times = [20, 19, 18]
    latitude = 0.0
    longitude = 0.0
    n_similar_players = 6

    # Mock BusinessService
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

    monkeypatch.setattr(
        BusinessService, "get_available_times", mock_get_available_times
    )

    # Mock PlayersService
    assigned_players = {}
    for time in range(8, 20):
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

    # Main request
    data = {
        "business_public_id": business_public_id,
        "court_name": court_name,
        "date": date,
    }
    response = await async_client.post(
        f"{test_settings.API_V1_STR}/matches/generation",
        headers=x_api_key_header,
        json=data,
    )

    assert response.status_code == 201

    matches_list = response.json()
    matches = matches_list["data"]
    assert len(matches) == 3

    for new_hour in range(17, 8, -1):
        # add times
        times.append(new_hour)

        # Mock BusinessService
        async def mock_get_available_times_new(
            self: Any,  # noqa: ARG001
            business_public_id: uuid.UUID,  # noqa: ARG001
            court_name: str,  # noqa: ARG001
            date: datetime.date,  # noqa: ARG001
        ) -> Any:
            return [
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

        monkeypatch.setattr(
            BusinessService, "get_available_times", mock_get_available_times_new
        )
        # test

        response_for_new_generate = await async_client.post(
            f"{test_settings.API_V1_STR}/matches/generation",
            headers=x_api_key_header,
            json=data,
        )
        assert response_for_new_generate.status_code == 201
        new_matches_list = response_for_new_generate.json()
        new_matches = new_matches_list["data"]
        assert len(new_matches) == 1
        match_extended = new_matches[0]
        assert match_extended["court_public_id"] == court_public_id
        assert match_extended["court_name"] == court_name
        assert match_extended["date"] == date
        assert match_extended["time"] == new_hour
        time = match_extended["time"]
        time_availability = PlayerFilters.to_time_availability(time)
        assigned_player = assigned_players[time_availability]["assigned"]
        similar_players = assigned_players[time_availability]["similar"]
        similar_players_user_public_ids = [
            str(player.user_public_id)
            for player in similar_players  # type: ignore
        ]

        match_players = match_extended["match_players"]
        match_assigned_players = [
            player
            for player in match_players
            if player["reserve"] == ReserveStatus.ASSIGNED
        ]
        assert len(match_assigned_players) == 1

        match_assigned_player = match_assigned_players[0]
        assert match_assigned_player["user_public_id"] == str(
            assigned_player.user_public_id  # type: ignore
        )

        match_similar_players_user_public_ids = [
            player["user_public_id"]
            for player in match_players
            if player["reserve"] == ReserveStatus.SIMILAR
        ]
        assert set(match_similar_players_user_public_ids) == set(
            similar_players_user_public_ids
        )
