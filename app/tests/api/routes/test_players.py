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
        _data = serialize_match_data(court_id=0, time=i, date="2024-11-25")
        _response = await create_match(async_client, x_api_key_header, _data)
        _content = _response.json()
        match_public_ids.append(_content["public_id"])

    # Add players to match
    user_public_id = str(uuid.uuid4())
    data = {"user_public_id": user_public_id}
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
    for match_player in content["data"]:
        assert match_player["match_public_id"] in match_public_ids
        assert match_player["user_public_id"] == user_public_id
        assert match_player["reserve"] == ReserveStatus.provisional
