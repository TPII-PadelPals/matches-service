import copy
import uuid
from typing import Any

from httpx import AsyncClient

from app.core.config import test_settings
from app.models.match_player import ReserveStatus
from app.models.player import PlayerFilters
from app.services.business_service import BusinessService
from app.tests.utils.utils import (
    get_mock_get_available_times,
    initial_apply_mocks_for_generate_matches,
)


async def test_generate_matches_given_one_avail_time(
    async_client: AsyncClient, x_api_key_header: dict[str, str], monkeypatch: Any
) -> None:
    # Test ctes
    times = [9]
    test_data = {
        "business_public_id": str(uuid.uuid4()),
        "court_name": "1",
        "court_public_id": str(uuid.uuid4()),
        "latitude": 0.0,
        "longitude": 0.0,
        "date": "2025-03-19",
        "times": times,
        "all_times": times,
        "is_reserved": False,
        "n_similar_players": 6,
    }

    assigned_players = initial_apply_mocks_for_generate_matches(
        monkeypatch, **test_data
    )

    # Main request
    data = {
        k: v
        for k, v in test_data.items()
        if k in ["business_public_id", "court_name", "date"]
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
    for k in ["court_public_id", "court_name", "date"]:
        assert match_extended[k] == test_data[k]
    assert match_extended["time"] == test_data["times"][0]  # type: ignore
    match_time = match_extended["time"]
    time_avail = PlayerFilters.to_time_availability(match_time)
    assigned_player = assigned_players[time_avail]["assigned"]
    similar_players = assigned_players[time_avail]["similar"]
    similar_players_user_public_ids = [
        str(player.user_public_id) for player in similar_players
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
    times = [8, 9, 10]
    test_data = {
        "business_public_id": str(uuid.uuid4()),
        "court_name": "1",
        "court_public_id": str(uuid.uuid4()),
        "latitude": 0.0,
        "longitude": 0.0,
        "date": "2025-03-19",
        "times": times,
        "all_times": times,
        "is_reserved": False,
        "n_similar_players": 6,
    }

    assigned_players = initial_apply_mocks_for_generate_matches(
        monkeypatch, **test_data
    )

    # Main request
    data = {
        k: v
        for k, v in test_data.items()
        if k in ["business_public_id", "court_name", "date"]
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
        for k in ["court_public_id", "court_name", "date"]:
            assert match_extended[k] == test_data[k]
        time = match_extended["time"]
        time_avail = PlayerFilters.to_time_availability(time)
        assigned_player = assigned_players[time_avail]["assigned"]
        similar_players = assigned_players[time_avail]["similar"]
        similar_players_user_public_ids = [
            str(player.user_public_id) for player in similar_players
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


async def test_generate_matches_twice_for_the_same_day_and_same_times(
    async_client: AsyncClient, x_api_key_header: dict[str, str], monkeypatch: Any
) -> None:
    # Test ctes
    times = [8, 9, 10]
    test_data = {
        "business_public_id": str(uuid.uuid4()),
        "court_name": "1",
        "court_public_id": str(uuid.uuid4()),
        "latitude": 0.0,
        "longitude": 0.0,
        "date": "2025-03-19",
        "times": times,
        "all_times": times,
        "is_reserved": False,
        "n_similar_players": 6,
    }

    _ = initial_apply_mocks_for_generate_matches(monkeypatch, **test_data)

    data = {
        k: v
        for k, v in test_data.items()
        if k in ["business_public_id", "court_name", "date"]
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
    times = [8, 9, 10]
    new_times = [6, 7, 8, 9, 10, 11, 12]
    test_data = {
        "business_public_id": str(uuid.uuid4()),
        "court_name": "1",
        "court_public_id": str(uuid.uuid4()),
        "latitude": 0.0,
        "longitude": 0.0,
        "date": "2025-03-19",
        "times": times,
        "all_times": new_times,
        "is_reserved": False,
        "n_similar_players": 6,
    }

    assigned_players = initial_apply_mocks_for_generate_matches(
        monkeypatch, **test_data
    )
    # Main request
    data = {
        k: v
        for k, v in test_data.items()
        if k in ["business_public_id", "court_name", "date"]
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
    new_test_data = copy.deepcopy(test_data)
    new_test_data["times"] = new_times
    mock_get_available_times_new = get_mock_get_available_times(**new_test_data)

    monkeypatch.setattr(
        BusinessService, "get_available_times", mock_get_available_times_new
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
        for k in ["court_public_id", "court_name", "date"]:
            assert match_extended[k] == test_data[k]
        assert match_extended["time"] in diff_times
        time = match_extended["time"]
        time_avail = PlayerFilters.to_time_availability(time)
        assigned_player = assigned_players[time_avail]["assigned"]
        similar_players = assigned_players[time_avail]["similar"]
        similar_players_user_public_ids = [
            str(player.user_public_id) for player in similar_players
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


async def test_generate_matches_for_the_same_with_new_times_twice(
    async_client: AsyncClient, x_api_key_header: dict[str, str], monkeypatch: Any
) -> None:
    # Test ctes
    times = [8, 9, 10]
    new_times = [6, 7, 8, 9, 10, 11, 12]
    test_data = {
        "business_public_id": str(uuid.uuid4()),
        "court_public_id": str(uuid.uuid4()),
        "court_name": "1",
        "latitude": 0.0,
        "longitude": 0.0,
        "date": "2025-03-19",
        "times": times,
        "all_times": new_times,
        "is_reserved": False,
        "n_similar_players": 6,
    }

    _ = initial_apply_mocks_for_generate_matches(monkeypatch, **test_data)

    data = {
        k: v
        for k, v in test_data.items()
        if k in ["business_public_id", "court_name", "date"]
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
    new_test_data = copy.deepcopy(test_data)
    new_test_data["times"] = new_times
    mock_get_available_times_new = get_mock_get_available_times(**new_test_data)
    monkeypatch.setattr(
        BusinessService, "get_available_times", mock_get_available_times_new
    )

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
    test_data = {
        "business_public_id": str(uuid.uuid4()),
        "court_public_id": str(uuid.uuid4()),
        "court_name": "1",
        "latitude": 0.0,
        "longitude": 0.0,
        "date": "2025-03-19",
        "times": [8, 9, 10],
        "all_times": list(range(8, 20)),
        "is_reserved": False,
        "n_similar_players": 6,
    }

    assigned_players = initial_apply_mocks_for_generate_matches(
        monkeypatch, **test_data
    )
    # Main request
    data = {
        k: v
        for k, v in test_data.items()
        if k in ["business_public_id", "court_name", "date"]
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
        test_data["times"].append(new_hour)  # type: ignore

        # Mock BusinessService
        mock_get_available_times_new = get_mock_get_available_times(**test_data)
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
        for k in ["court_public_id", "court_name", "date"]:
            assert match_extended[k] == test_data[k]
        assert match_extended["time"] == new_hour
        time = match_extended["time"]
        time_avail = PlayerFilters.to_time_availability(time)
        assigned_player = assigned_players[time_avail]["assigned"]
        similar_players = assigned_players[time_avail]["similar"]
        similar_players_user_public_ids = [
            str(player.user_public_id) for player in similar_players
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


async def test_generate_matches_multiple_for_the_same_day_inverse_time(
    async_client: AsyncClient, x_api_key_header: dict[str, str], monkeypatch: Any
) -> None:
    # Test ctes
    test_data = {
        "business_public_id": str(uuid.uuid4()),
        "court_public_id": str(uuid.uuid4()),
        "court_name": "1",
        "latitude": 0.0,
        "longitude": 0.0,
        "date": "2025-03-19",
        "times": [20, 19, 18],
        "all_times": list(range(8, 20)),
        "is_reserved": False,
        "n_similar_players": 6,
    }
    assigned_players = initial_apply_mocks_for_generate_matches(
        monkeypatch, **test_data
    )
    # Main request
    data = {
        k: v
        for k, v in test_data.items()
        if k in ["business_public_id", "court_name", "date"]
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
        test_data["times"].append(new_hour)  # type: ignore

        # Mock BusinessService
        mock_get_available_times_new = get_mock_get_available_times(**test_data)
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
        for k in ["court_public_id", "court_name", "date"]:
            assert match_extended[k] == test_data[k]
        assert match_extended["time"] == new_hour
        time = match_extended["time"]
        time_avail = PlayerFilters.to_time_availability(time)
        assigned_player = assigned_players[time_avail]["assigned"]
        similar_players = assigned_players[time_avail]["similar"]
        similar_players_user_public_ids = [
            str(player.user_public_id) for player in similar_players
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


async def test_generate_matches_creates_match_players_with_distance_equal_to_arriving_order(
    async_client: AsyncClient, x_api_key_header: dict[str, str], monkeypatch: Any
) -> None:
    # Test ctes
    times = [9]
    test_data = {
        "business_public_id": str(uuid.uuid4()),
        "court_public_id": str(uuid.uuid4()),
        "court_name": "1",
        "latitude": 0.0,
        "longitude": 0.0,
        "date": "2025-03-19",
        "times": times,
        "all_times": times,
        "is_reserved": False,
        "n_similar_players": 6,
    }
    assigned_players = initial_apply_mocks_for_generate_matches(
        monkeypatch, **test_data
    )

    # Main request
    data = {
        k: v
        for k, v in test_data.items()
        if k in ["business_public_id", "court_name", "date"]
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
    for k in ["court_public_id", "court_name", "date"]:
        assert match_extended[k] == test_data[k]

    assert match_extended["time"] == test_data["times"][0]  # type: ignore
    time = match_extended["time"]
    time_avail = PlayerFilters.to_time_availability(time)
    assigned_player = assigned_players[time_avail]["assigned"]
    similar_players = assigned_players[time_avail]["similar"]
    similar_players_uuids = [str(player.user_public_id) for player in similar_players]

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

    match_similar_players = [
        player for player in match_players if player["reserve"] == ReserveStatus.SIMILAR
    ]
    match_similar_players_sorted = sorted(
        match_similar_players, key=lambda player: player["distance"]
    )
    match_similar_players_uuids = [
        player["user_public_id"] for player in match_similar_players_sorted
    ]
    assert match_similar_players_uuids == similar_players_uuids
