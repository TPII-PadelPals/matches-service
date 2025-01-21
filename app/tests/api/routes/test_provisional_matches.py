import datetime

from app.tests.utils.provisional_matches import create_provisional_match, set_provisional_match_data
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.models.provisional_match import ProvisionalMatchCreate
from app.services.provisional_match_service import ProvisionalMatchService


async def test_create_provisional_match(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    data = set_provisional_match_data("player_1", "player_4", 0, 8, "2024-11-25")
    response = await create_provisional_match(async_client, x_api_key_header, data)
    assert response.status_code == 201
    content = response.json()
    assert content == data


async def test_create_provisional_matches(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    data = [
        set_provisional_match_data("player_1", "player_2", 0, 8, "2024-11-25"),
        set_provisional_match_data("player_1", "player_3", 1, 8, "2024-11-25"),
        set_provisional_match_data("player_1", "player_2", 1, 8, "2024-11-25"),
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


async def test_create_repeat_provisional_match(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    data = set_provisional_match_data("player_1", "player_4", 0, 8, "2024-11-25")
    response = await create_provisional_match(async_client, x_api_key_header, data)
    assert response.status_code == 201
    response = await create_provisional_match(async_client, x_api_key_header, data)
    assert response.status_code == 409


async def test_read_item(
    async_client: AsyncClient, x_api_key_header: dict[str, str], session: AsyncSession
) -> None:
    provisional_match_in_info = set_provisional_match_data(
        "player_1", "player_2", 0, 8, "2024-11-25"
    )
    provisional_match_in = ProvisionalMatchCreate(
        player_id_1=provisional_match_in_info["player_id_1"],
        player_id_2=provisional_match_in_info["player_id_2"],
        court_id=provisional_match_in_info["court_id"],
        time=provisional_match_in_info["time"],
        date=datetime.date.fromisoformat(provisional_match_in_info["date"]),
    )
    service = ProvisionalMatchService()
    _ = await service.create_match(session, provisional_match_in)
    response = await async_client.get(
        f"{settings.API_V1_STR}/provisional-matches/",
        headers=x_api_key_header,
        params={"player_id_1": "player_2"},
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content) == 1
    content = content[0]
    assert content == provisional_match_in_info


async def test_read_item_not_found(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    response = await async_client.get(
        f"{settings.API_V1_STR}/provisional-matches/",
        headers=x_api_key_header,
        params={"player_id_1": "player_2"},
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content) == 0
