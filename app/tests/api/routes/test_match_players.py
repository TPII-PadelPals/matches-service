import uuid

from httpx import AsyncClient

from app.core.config import test_settings
from app.tests.utils.provisional_matches import (
    create_provisional_match,
    set_provisional_match_data,
)


async def test_add_player_to_match(
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
        f"{test_settings.API_V1_STR}/provisional-matches/{match_public_id}/players",
        headers=x_api_key_header,
        json=data,
    )
    assert response.status_code == 201
    content = response.json()
    data["match_public_id"] = match_public_id
    data["reserve"] = "provisional"
    assert content == data
