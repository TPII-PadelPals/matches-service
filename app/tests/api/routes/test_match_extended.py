import uuid

from httpx import AsyncClient

from app.core.config import test_settings
from app.models.match_player import ReserveStatus
from app.tests.utils.matches import (
    create_match,
    serialize_match_data,
)


async def test_get_player_matches_returns_all_matches_associated_to_player(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    # Create match
    n_matches = 4
    match_public_ids = []
    for i in range(n_matches):
        _data = serialize_match_data(court_name="0", time=i, date="2024-11-25")
        _response = await create_match(async_client, x_api_key_header, _data)
        _content = _response.json()
        match_public_ids.append(_content["public_id"])

    # Add players to match
    user_public_id = str(uuid.uuid4())
    data = {"user_public_id": user_public_id, "distance": 0}
    for match_public_id in match_public_ids:
        await async_client.post(
            f"{test_settings.API_V1_STR}/matches/{match_public_id}/players/",
            headers=x_api_key_header,
            json=data,
        )
    response = await async_client.get(
        f"{test_settings.API_V1_STR}/players/{user_public_id}/matches/",
        headers=x_api_key_header,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == n_matches
    for response_data in content["data"]:
        assert response_data["public_id"] in match_public_ids
        assert response_data["court_name"] == "0"
        assert response_data["time"] >= 0 and response_data["time"] < n_matches
        assert response_data["date"] == "2024-11-25"
        assert response_data["status"] == ReserveStatus.PROVISIONAL
        assert len(response_data["match_players"]) == 1
        for player_data in response_data["match_players"]:
            assert player_data["user_public_id"] == user_public_id
            assert player_data["match_public_id"] in match_public_ids
            assert player_data["reserve"] == ReserveStatus.PROVISIONAL


async def test_get_player_matches_returns_all_matches_associated_to_player_multiple_days(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    # Create match
    n_matches = 2
    match_public_ids = []
    for i in range(n_matches):
        _data = serialize_match_data(court_name="0", time=i, date="2024-11-25")
        _response = await create_match(async_client, x_api_key_header, _data)
        _content = _response.json()
        match_public_ids.append(_content["public_id"])

    for i in range(n_matches):
        _data = serialize_match_data(court_name="1", time=i, date="2024-11-26")
        _response = await create_match(async_client, x_api_key_header, _data)
        _content = _response.json()
        match_public_ids.append(_content["public_id"])

    for i in range(n_matches):
        _data = serialize_match_data(court_name="2", time=i, date="2024-11-27")
        _response = await create_match(async_client, x_api_key_header, _data)
        _content = _response.json()
        match_public_ids.append(_content["public_id"])

    # Add players to match
    user_public_id = str(uuid.uuid4())
    data = {"user_public_id": user_public_id, "distance": 0}
    for match_public_id in match_public_ids:
        await async_client.post(
            f"{test_settings.API_V1_STR}/matches/{match_public_id}/players/",
            headers=x_api_key_header,
            json=data,
        )
    response = await async_client.get(
        f"{test_settings.API_V1_STR}/players/{user_public_id}/matches/",
        headers=x_api_key_header,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == n_matches * 3
    for response_data in content["data"]:
        assert response_data["public_id"] in match_public_ids
        # assert response_data["court_id"] >= 0 and response_data["court_id"] <= 2
        if response_data["court_name"] == "0":
            assert response_data["date"] == "2024-11-25"
        elif response_data["court_name"] == "1":
            assert response_data["date"] == "2024-11-26"
        elif response_data["court_name"] == "2":
            assert response_data["date"] == "2024-11-27"
        assert response_data["time"] >= 0 and response_data["time"] < n_matches
        assert response_data["status"] == ReserveStatus.PROVISIONAL
        assert len(response_data["match_players"]) == 1
        for player_data in response_data["match_players"]:
            assert player_data["user_public_id"] == user_public_id
            assert player_data["match_public_id"] in match_public_ids
            assert player_data["reserve"] == ReserveStatus.PROVISIONAL


async def test_get_player_matches_returns_all_matches_associated_to_multiple_player(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    # Create match
    n_matches = 4
    match_public_ids = []
    for i in range(n_matches):
        _data = serialize_match_data(court_name="0", time=i, date="2024-11-25")
        _response = await create_match(async_client, x_api_key_header, _data)
        _content = _response.json()
        match_public_ids.append(_content["public_id"])

    # Add players to match
    user_public_id = str(uuid.uuid4())
    list_users = [user_public_id, str(uuid.uuid4())]
    for match_public_id in match_public_ids:
        for user_id in list_users:
            await async_client.post(
                f"{test_settings.API_V1_STR}/matches/{match_public_id}/players/",
                headers=x_api_key_header,
                json={"user_public_id": user_id, "distance": 0},
            )
    response = await async_client.get(
        f"{test_settings.API_V1_STR}/players/{user_public_id}/matches/",
        headers=x_api_key_header,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == n_matches
    for response_data in content["data"]:
        assert response_data["public_id"] in match_public_ids
        assert response_data["court_name"] == "0"
        assert response_data["time"] >= 0 and response_data["time"] < n_matches
        assert response_data["date"] == "2024-11-25"
        assert response_data["status"] == ReserveStatus.PROVISIONAL
        assert len(response_data["match_players"]) == 2
        for player_data in response_data["match_players"]:
            assert player_data["user_public_id"] in list_users
            assert player_data["match_public_id"] in match_public_ids
            assert player_data["reserve"] == ReserveStatus.PROVISIONAL
