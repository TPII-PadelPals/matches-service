import uuid

from httpx import AsyncClient

from app.core.config import test_settings
from app.tests.utils.provisional_matches import (
    create_provisional_match,
    set_provisional_match_data,
)


async def test_add_one_player_to_match_reserve_is_provisional(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    # Create match
    data = set_provisional_match_data(0, 8, "2024-11-25")
    response = await create_provisional_match(async_client, x_api_key_header, data)
    content = response.json()
    match_public_id = content["public_id"]
    # Add player to match
    data = {"user_public_id": str(uuid.uuid4())}
    response = await async_client.post(
        f"{test_settings.API_V1_STR}/provisional-matches/{match_public_id}/players/",
        headers=x_api_key_header,
        json=data,
    )
    assert response.status_code == 201
    content = response.json()
    data["match_public_id"] = match_public_id
    data["reserve"] = "provisional"
    assert content == data


async def test_add_same_player_to_match_raises_exception(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    # Create match
    data = set_provisional_match_data(0, 8, "2024-11-25")
    response = await create_provisional_match(async_client, x_api_key_header, data)
    content = response.json()
    match_public_id = content["public_id"]
    # Add player to match
    data = {"user_public_id": str(uuid.uuid4())}
    for _ in range(2):
        response = await async_client.post(
            f"{test_settings.API_V1_STR}/provisional-matches/{match_public_id}/players/",
            headers=x_api_key_header,
            json=data,
        )
    assert response.status_code == 409
    content = response.json()
    assert content["detail"] == "Couple (match, player) already exists."


async def test_add_many_players_to_match(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    # Create match
    _data = set_provisional_match_data(0, 8, "2024-11-25")
    _response = await create_provisional_match(async_client, x_api_key_header, _data)
    _content = _response.json()
    match_public_id = _content["public_id"]

    # Add players to match
    n_players = 4
    data = [{"user_public_id": str(uuid.uuid4())} for _ in range(n_players)]
    response = await async_client.post(
        f"{test_settings.API_V1_STR}/provisional-matches/{match_public_id}/players/bulk/",
        headers=x_api_key_header,
        json=data,
    )
    assert response.status_code == 201
    content = response.json()
    for value in data:
        value["match_public_id"] = match_public_id
        value["reserve"] = "provisional"
    all(match_player in data for match_player in content)


async def test_update_one_player_reserve_to_accept(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    # Create match
    data = set_provisional_match_data(0, 8, "2024-11-25")
    response = await create_provisional_match(async_client, x_api_key_header, data)
    content = response.json()
    match_public_id = content["public_id"]
    # Add player to match
    data = {"user_public_id": str(uuid.uuid4())}
    response = await async_client.post(
        f"{test_settings.API_V1_STR}/provisional-matches/{match_public_id}/players/",
        headers=x_api_key_header,
        json=data,
    )
    content = response.json()
    user_public_id = content["user_public_id"]
    # Update match player
    data = {"reserve": "accept"}
    response = await async_client.patch(
        f"{test_settings.API_V1_STR}/provisional-matches/{match_public_id}/players/{user_public_id}/",
        headers=x_api_key_header,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["match_public_id"] == match_public_id
    assert content["user_public_id"] == user_public_id
    assert content["reserve"] == data["reserve"]
