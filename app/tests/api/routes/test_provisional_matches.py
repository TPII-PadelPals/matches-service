from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.tests.utils.items import create_random_item
import datetime

from app.models.provisional_match import ProvisionalMatch

async def test_create_provisional_match(
        async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    # /api/v1/provisional-matches/
    data = {
        "player_id_1": "player_1",
        "player_id_2": "player_4",
        "court_id": 0,
        "time": 8,
        # "date": datetime.date(2024, 11, 25),
        "date": "2024-11-25",
    }
    response = await async_client.post(
        f"{settings.API_V1_STR}/provisional-matches/",
        headers=x_api_key_header,
        json=data,
    )
    assert response.status_code == 201
    content = response.json()
    assert content["player_id_1"] == data["player_id_1"]
    assert content["player_id_2"] == data["player_id_2"]
    assert content["court_id"] == data["court_id"]
    assert content["time"] == data["time"]
    assert content["date"] == data["date"]

async def test_create_provisional_matches(
        async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    # /api/v1/provisional-matches/
    data = [
        {
            "player_id_1": "player_1",
            "player_id_2": "player_2",
            "court_id": 0,
            "time": 8,
            # "date": datetime.date(2024, 11, 25),
            "date": "2024-11-25",
        },
        {
            "player_id_1": "player_1",
            "player_id_2": "player_3",
            "court_id": 1,
            "time": 8,
            # "date": datetime.date(2024, 11, 25),
            "date": "2024-11-25",
        },
        {
            "player_id_1": "player_1",
            "player_id_2": "player_2",
            "court_id": 1,
            "time": 8,
            # "date": datetime.date(2024, 11, 25),
            "date": "2024-11-25",
        }
    ]
    response = await async_client.post(
        f"{settings.API_V1_STR}/provisional-matches/bulk",
        headers=x_api_key_header,
        json=data,
    )
    assert response.status_code == 201
    content = response.json()
    assert len(content) == 3
    assert data[0] in content
    assert data[1] in content
    assert data[2] in content


async def test_read_item(
        async_client: AsyncClient, x_api_key_header: dict[str, str], session: AsyncSession
) -> None:
    provisional_match_in = {
        "player_id_1": "player_1",
        "player_id_2": "player_2",
        "court_id": 0,
        "time": 8,
        # "date": datetime.date(2024, 11, 25),
        "date": "2024-11-25",
    }
    await async_client.post(
        f"{settings.API_V1_STR}/provisional-matches/",
        headers=x_api_key_header,
        json=provisional_match_in,
    )
    response = await async_client.get(
        f"{settings.API_V1_STR}/provisional-matches/",
        headers=x_api_key_header,
        params={"player_id_1": "player_2"},
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content) == 1
    content = content[0]
    assert content["player_id_1"] == provisional_match_in["player_id_1"]
    assert content["player_id_2"] == provisional_match_in["player_id_2"]
    assert content["court_id"] == provisional_match_in["court_id"]
    assert content["time"] == provisional_match_in["time"]
    assert content["date"] == provisional_match_in["date"]


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

