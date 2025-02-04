import uuid

from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.tests.utils.provisional_matches import (
    create_provisional_match,
    generate_provisional_match,
    set_provisional_match_data,
)
from app.utilities.exceptions import NotUniqueException


async def test_create_provisional_match(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    data = set_provisional_match_data(0, 8, "2024-11-25")
    response = await create_provisional_match(async_client, x_api_key_header, data)
    assert response.status_code == 201
    content = response.json()
    public_id = content.pop("public_id")
    assert len(public_id) == len(str(uuid.uuid4()))
    assert content == data


async def test_create_multiple_provisional_matches_returns_all(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    data = [
        set_provisional_match_data(0, 8, "2024-11-25"),
        set_provisional_match_data(1, 8, "2024-11-25"),
        set_provisional_match_data(1, 9, "2024-11-25"),
    ]
    response = await async_client.post(
        f"{settings.API_V1_STR}/provisional-matches/bulk",
        headers=x_api_key_header,
        json=data,
    )
    assert response.status_code == 201
    content = response.json()
    [item.pop("public_id") for item in content]
    assert len(content) == 3
    assert all(item in content for item in data)


async def test_create_provisional_matches_on_multiple_raises_not_unique_exception(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    data = set_provisional_match_data(0, 8, "2024-11-25")
    first_response = await create_provisional_match(
        async_client, x_api_key_header, data
    )
    assert first_response.status_code == 201
    first_content = first_response.json()
    first_content.pop("public_id")
    assert data == first_content
    second_response = await create_provisional_match(
        async_client, x_api_key_header, data
    )
    assert second_response.status_code == 409
    second_content = second_response.json()
    response_detail = second_content.get("detail")
    expected_detail = NotUniqueException("provisional match").detail

    assert (
        response_detail == expected_detail
    ), f"Expected '{expected_detail}' but got '{response_detail}'"


async def test_read_provisional_match_by_match_public_id(
    async_client: AsyncClient, x_api_key_header: dict[str, str], session: AsyncSession
) -> None:
    data = set_provisional_match_data(0, 8, "2024-11-25")
    prov_match_created = await generate_provisional_match(session, data)
    response = await async_client.get(
        f"{settings.API_V1_STR}/provisional-matches/",
        headers=x_api_key_header,
        params={"public_id": prov_match_created["public_id"]},
    )
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 1
    prov_match_read = content["data"][0]
    prov_match_created.pop("id")
    assert prov_match_read == prov_match_created


async def test_read_provisional_match_by_unique_attributes(
    async_client: AsyncClient, x_api_key_header: dict[str, str], session: AsyncSession
) -> None:
    data = set_provisional_match_data(0, 8, "2024-11-25")
    prov_match_created = await generate_provisional_match(session, data)
    response = await async_client.get(
        f"{settings.API_V1_STR}/provisional-matches/",
        headers=x_api_key_header,
        params={
            "court_id": prov_match_created["court_id"],
            "time": prov_match_created["time"],
            "date": prov_match_created["date"],
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 1
    prov_match_read = content["data"][0]
    prov_match_created.pop("id")
    assert prov_match_read == prov_match_created


async def test_read_multiple_provisional_match(
    async_client: AsyncClient, x_api_key_header: dict[str, str], session: AsyncSession
) -> None:
    provisional_matches_in = [
        set_provisional_match_data(0, 8, "2024-11-25"),
        set_provisional_match_data(1, 8, "2024-11-25"),
        set_provisional_match_data(5, 9, "2024-11-25"),
        set_provisional_match_data(0, 12, "2024-11-25"),
        set_provisional_match_data(4, 8, "2024-01-05"),
    ]
    for provisional_match_in in provisional_matches_in:
        await generate_provisional_match(session, provisional_match_in)
    response = await async_client.get(
        f"{settings.API_V1_STR}/provisional-matches/",
        headers=x_api_key_header,
        params={"time": provisional_matches_in[0].get("time")},
    )
    assert response.status_code == 200
    content = response.json()
    [item.pop("public_id") for item in content["data"]]
    assert content["count"] == 3
    assert provisional_matches_in[0] in content["data"]
    assert provisional_matches_in[1] in content["data"]
    assert provisional_matches_in[4] in content["data"]
