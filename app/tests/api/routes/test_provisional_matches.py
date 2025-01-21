
import uuid

from app.tests.utils.provisional_matches import create_provisional_match, generate_provisional_match, set_provisional_match_data
from app.utilities.exceptions import NotUniqueException
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings


async def test_create_provisional_match(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    data = set_provisional_match_data(0, 8, "2024-11-25")
    response = await create_provisional_match(async_client, x_api_key_header, data)
    assert response.status_code == 201
    content = response.json()
    assert content == data


async def test_create_multiple_provisional_matches_returns_all(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    data = [
        set_provisional_match_data(0, 8, "2024-11-25"),
        set_provisional_match_data(1, 8, "2024-11-25"),
        set_provisional_match_data(1, 8, "2024-11-25"),
    ]
    response = await async_client.post(
        f"{settings.API_V1_STR}/provisional-matches/bulk",
        headers=x_api_key_header,
        json=data,
    )
    assert response.status_code == 201
    content = response.json()
    assert len(content) == 3
    assert all(item in content for item in data)


async def test_create_provisional_matches_on_multiple_raises_not_unique_exception(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    data = set_provisional_match_data(0, 8, "2024-11-25")
    first_response = await create_provisional_match(async_client, x_api_key_header, data)
    assert first_response.status_code == 201
    assert data == first_response.json()
    second_response = await create_provisional_match(async_client, x_api_key_header, data)
    assert second_response.status_code == 409
    response_detail = second_response.json().get('detail')
    expected_detail = NotUniqueException("provisional match").detail

    assert response_detail == expected_detail, f"Expected '{expected_detail}' but got '{response_detail}'"

async def test_read_provisional_match(
    async_client: AsyncClient, x_api_key_header: dict[str, str], session: AsyncSession
) -> None:
    provisional_match_in = set_provisional_match_data(
       0, 8, "2024-11-25"
    )
    await generate_provisional_match(session, provisional_match_in)
    response = await async_client.get(
        f"{settings.API_V1_STR}/provisional-matches/",
        headers=x_api_key_header,
        params={"user_public_id_1": provisional_match_in.get("user_public_id_1")},
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content) == 1
    content = content[0]
    assert content == provisional_match_in


async def test_read_provisional_matches_returns_empty_list_when_player_has_zero_provisional_matches(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    response = await async_client.get(
        f"{settings.API_V1_STR}/provisional-matches/",
        headers=x_api_key_header,
        params={"user_public_id_1": uuid.uuid4()},
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content) == 0
