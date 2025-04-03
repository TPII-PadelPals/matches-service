import uuid

from httpx import AsyncClient

from app.core.config import test_settings
from app.models.match_player import ReserveStatus
from app.tests.utils.matches import (
    create_match,
    serialize_match_data,
)


async def test_add_one_player_to_match_reserve_is_provisional(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    # Create match
    data = serialize_match_data(court_id="0", time=8, date="2024-11-25")
    response = await create_match(async_client, x_api_key_header, data)
    content = response.json()
    match_public_id = content["public_id"]
    # Add player to match
    data = {"user_public_id": str(uuid.uuid4())}
    response = await async_client.post(
        f"{test_settings.API_V1_STR}/matches/{match_public_id}/players/",
        headers=x_api_key_header,
        json=data,
    )
    assert response.status_code == 201
    content = response.json()
    data["match_public_id"] = match_public_id
    data["reserve"] = ReserveStatus.PROVISIONAL
    assert content == data


async def test_add_same_player_to_match_raises_exception(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    # Create match
    data = serialize_match_data(court_id="0", time=8, date="2024-11-25")
    response = await create_match(async_client, x_api_key_header, data)
    content = response.json()
    match_public_id = content["public_id"]
    # Add player to match
    data = {"user_public_id": str(uuid.uuid4())}
    for _ in range(2):
        response = await async_client.post(
            f"{test_settings.API_V1_STR}/matches/{match_public_id}/players/",
            headers=x_api_key_header,
            json=data,
        )
    assert response.status_code == 409
    content = response.json()
    assert content["detail"] == "MatchPlayer already exists."


async def test_add_many_players_to_match(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    # Create match
    _data = serialize_match_data(court_id="0", time=8, date="2024-11-25")
    _response = await create_match(async_client, x_api_key_header, _data)
    _content = _response.json()
    match_public_id = _content["public_id"]

    # Add players to match
    n_players = 4
    data = [{"user_public_id": str(uuid.uuid4())} for _ in range(n_players)]
    response = await async_client.post(
        f"{test_settings.API_V1_STR}/matches/{match_public_id}/players/bulk/",
        headers=x_api_key_header,
        json=data,
    )
    assert response.status_code == 201
    content = response.json()
    for value in data:
        value["match_public_id"] = match_public_id
        value["reserve"] = ReserveStatus.PROVISIONAL
    all(match_player in data for match_player in content)


async def test_get_one_match_player(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    # Create match
    data = serialize_match_data(court_id="0", time=8, date="2024-11-25")
    response = await create_match(async_client, x_api_key_header, data)
    content = response.json()
    match_public_id = content["public_id"]
    # Add player to match
    user_public_id = str(uuid.uuid4())
    data = {"user_public_id": user_public_id}
    await async_client.post(
        f"{test_settings.API_V1_STR}/matches/{match_public_id}/players/",
        headers=x_api_key_header,
        json=data,
    )
    response = await async_client.get(
        f"{test_settings.API_V1_STR}/matches/{match_public_id}/players/{user_public_id}",
        headers=x_api_key_header,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["match_public_id"] == match_public_id
    assert content["user_public_id"] == user_public_id
    assert content["reserve"] == ReserveStatus.PROVISIONAL


async def test_get_match_players_returns_all_players_associated_to_match(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    # Create match
    _data = serialize_match_data(court_id="0", time=8, date="2024-11-25")
    _response = await create_match(async_client, x_api_key_header, _data)
    _content = _response.json()
    match_public_id = _content["public_id"]

    # Add players to match
    n_players = 4
    user_public_ids = [str(uuid.uuid4()) for _ in range(n_players)]
    data = [{"user_public_id": user_public_id} for user_public_id in user_public_ids]
    await async_client.post(
        f"{test_settings.API_V1_STR}/matches/{match_public_id}/players/bulk/",
        headers=x_api_key_header,
        json=data,
    )
    response = await async_client.get(
        f"{test_settings.API_V1_STR}/matches/{match_public_id}/players/",
        headers=x_api_key_header,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == n_players
    for match_player in content["data"]:
        assert match_player["match_public_id"] == match_public_id
        assert match_player["user_public_id"] in user_public_ids
        assert match_player["reserve"] == ReserveStatus.PROVISIONAL


async def test_update_one_player_reserve_to_inside(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    # Create match
    data = serialize_match_data(court_id="0", time=8, date="2024-11-25")
    response = await create_match(async_client, x_api_key_header, data)
    content = response.json()
    match_public_id = content["public_id"]
    # Add player to match
    data = {"user_public_id": str(uuid.uuid4())}
    response = await async_client.post(
        f"{test_settings.API_V1_STR}/matches/{match_public_id}/players/",
        headers=x_api_key_header,
        json=data,
    )
    content = response.json()
    user_public_id = content["user_public_id"]
    _response = await async_client.patch(
        f"{test_settings.API_V1_STR}/matches/{match_public_id}/players/{user_public_id}/",
        headers=x_api_key_header,
        json={"reserve": ReserveStatus.ASSIGNED},
    )
    # Update match player

    data = {"reserve": ReserveStatus.INSIDE}

    response = await async_client.patch(
        f"{test_settings.API_V1_STR}/matches/{match_public_id}/players/{user_public_id}/",
        headers=x_api_key_header,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["match_public_id"] == match_public_id
    assert content["user_public_id"] == user_public_id
    assert content["reserve"] == data["reserve"]


async def test_update_one_player_reserve_to_reject(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    # Create match
    data = serialize_match_data(court_id="0", time=8, date="2024-11-25")
    response = await create_match(async_client, x_api_key_header, data)
    content = response.json()
    match_public_id = content["public_id"]
    # Add player to match
    data = {"user_public_id": str(uuid.uuid4())}
    response = await async_client.post(
        f"{test_settings.API_V1_STR}/matches/{match_public_id}/players/",
        headers=x_api_key_header,
        json=data,
    )
    content = response.json()
    user_public_id = content["user_public_id"]
    # Update match player
    data = {"reserve": ReserveStatus.REJECTED}
    response = await async_client.patch(
        f"{test_settings.API_V1_STR}/matches/{match_public_id}/players/{user_public_id}/",
        headers=x_api_key_header,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["match_public_id"] == match_public_id
    assert content["user_public_id"] == user_public_id
    assert content["reserve"] == data["reserve"]


async def test_update_one_player_raises_exception_when_match_player_not_exists(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    match_public_id = str(uuid.uuid4())
    user_public_id = str(uuid.uuid4())
    data = {"reserve": ReserveStatus.INSIDE}

    response = await async_client.patch(
        f"{test_settings.API_V1_STR}/matches/{match_public_id}/players/{user_public_id}/",
        headers=x_api_key_header,
        json=data,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "MatchPlayer not found."


async def test_one_player_reserve_to_inside(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    # Create match
    data = serialize_match_data(court_id="0", time=8, date="2024-11-25")
    response = await create_match(async_client, x_api_key_header, data)
    content = response.json()

    match_public_id = content["public_id"]
    # Add player to match
    data = {"user_public_id": str(uuid.uuid4())}
    response = await async_client.post(
        f"{test_settings.API_V1_STR}/matches/{match_public_id}/players/",
        headers=x_api_key_header,
        json=data,
    )
    content = response.json()
    user_public_id = content["user_public_id"]
    _response = await async_client.patch(
        f"{test_settings.API_V1_STR}/matches/{match_public_id}/players/{user_public_id}/",
        headers=x_api_key_header,
        json={"reserve": ReserveStatus.ASSIGNED},
    )
    # Update match player
    response = await async_client.patch(
        f"{test_settings.API_V1_STR}/matches/{match_public_id}/players/{user_public_id}/",
        headers=x_api_key_header,
        json={"reserve": ReserveStatus.INSIDE},
    )
    assert response.status_code == 200
    content = response.json()
    assert content["match_public_id"] == match_public_id
    assert content["user_public_id"] == user_public_id
    assert content["reserve"] == ReserveStatus.INSIDE


async def test_one_player_reserve_to_accept_not_assigned_is_rejected(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    # Create match
    data = serialize_match_data(court_id="0", time=8, date="2024-11-25")
    response = await create_match(async_client, x_api_key_header, data)
    content = response.json()
    match_public_id = content["public_id"]
    # Add player to match
    data = {"user_public_id": str(uuid.uuid4())}
    response = await async_client.post(
        f"{test_settings.API_V1_STR}/matches/{match_public_id}/players/",
        headers=x_api_key_header,
        json=data,
    )
    content = response.json()
    user_public_id = content["user_public_id"]
    _ = await async_client.patch(
        f"{test_settings.API_V1_STR}/matches/{match_public_id}/players/{user_public_id}/",
        headers=x_api_key_header,
        json={"reserve": ReserveStatus.INSIDE},
    )
    # Update match player
    response = await async_client.patch(
        f"{test_settings.API_V1_STR}/matches/{match_public_id}/players/{user_public_id}/",
        headers=x_api_key_header,
        json={"reserve": ReserveStatus.INSIDE},
    )
    assert response.status_code == 401


async def test_one_player_reserve_to_accept_not_provisional_is_rejected(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    # Create match
    data = serialize_match_data(court_id="0", time=8, date="2024-11-25")
    response = await create_match(async_client, x_api_key_header, data)
    content = response.json()
    match_public_id = content["public_id"]
    # Add player to match
    data = {"user_public_id": str(uuid.uuid4())}
    response = await async_client.post(
        f"{test_settings.API_V1_STR}/matches/{match_public_id}/players/",
        headers=x_api_key_header,
        json=data,
    )
    content = response.json()
    user_public_id = content["user_public_id"]
    _ = await async_client.patch(
        f"{test_settings.API_V1_STR}/matches/{match_public_id}/players/{user_public_id}/",
        headers=x_api_key_header,
        json={"reserve": ReserveStatus.REJECTED},
    )
    # Update match player
    response = await async_client.patch(
        f"{test_settings.API_V1_STR}/matches/{match_public_id}/players/{user_public_id}/",
        headers=x_api_key_header,
        json={"reserve": ReserveStatus.INSIDE},
    )
    assert response.status_code == 401
