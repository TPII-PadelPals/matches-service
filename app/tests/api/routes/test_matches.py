import uuid

from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings, test_settings
from app.models.match import MatchStatus
from app.tests.utils.matches import create_match, generate_match
from app.utilities.exceptions import NotUniqueException


async def test_create_match(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    data = {
        "business_public_id": "94353293-50ed-494c-adc9-e545f6a5b2b3",
        "court_name": "0",
        "date": "2024-11-25",
        "time": 8,
    }
    response = await create_match(async_client, x_api_key_header, data)
    assert response.status_code == 201
    content = response.json()
    public_id = content.pop("public_id")
    assert len(public_id) == len(str(uuid.uuid4()))
    assert content["status"] == MatchStatus.provisional
    content.pop("status")
    data["court_public_id"] = None
    assert content == data


async def test_create_multiple_matches_returns_all(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    business_public_id = "94353293-50ed-494c-adc9-e545f6a5b2b3"
    date = "2024-11-25"
    data = [
        {
            "business_public_id": business_public_id,
            "court_name": "0",
            "date": date,
            "time": 8,
        },
        {
            "business_public_id": business_public_id,
            "court_name": "1",
            "date": date,
            "time": 8,
        },
        {
            "business_public_id": business_public_id,
            "court_name": "1",
            "date": date,
            "time": 9,
        },
    ]
    response = await async_client.post(
        f"{settings.API_V1_STR}/matches/bulk",
        headers=x_api_key_header,
        json=data,
    )
    assert response.status_code == 201
    content = response.json()
    for item in content:
        item.pop("public_id")
        item.pop("status")
        item.pop("court_public_id")
    assert len(content) == 3
    assert all(item in content for item in data)


async def test_create_matches_on_multiple_raises_not_unique_exception(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    data = {
        "business_public_id": "94353293-50ed-494c-adc9-e545f6a5b2b3",
        "court_name": "0",
        "date": "2024-11-25",
        "time": 8,
    }
    data["court_public_id"] = str(uuid.uuid4())
    first_response = await create_match(async_client, x_api_key_header, data)
    assert first_response.status_code == 201
    first_content = first_response.json()
    first_content.pop("public_id")
    first_content.pop("status")
    assert data == first_content
    second_response = await create_match(async_client, x_api_key_header, data)
    assert second_response.status_code == 409
    second_content = second_response.json()
    response_detail = second_content.get("detail")
    expected_detail = NotUniqueException("Match").detail

    assert (
        response_detail == expected_detail
    ), f"Expected '{expected_detail}' but got '{response_detail}'"


async def test_get_match(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    data = {
        "business_public_id": "94353293-50ed-494c-adc9-e545f6a5b2b3",
        "court_name": "0",
        "date": "2024-11-25",
        "time": 8,
    }
    response = await create_match(async_client, x_api_key_header, data)
    prov_match_created = response.json()
    response = await async_client.get(
        f"{settings.API_V1_STR}/matches/{prov_match_created['public_id']}",
        headers=x_api_key_header,
    )
    assert response.status_code == 200
    prov_match_get = response.json()
    assert prov_match_get == prov_match_created


async def test_get_match_raises_exception_when_match_not_exists(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    response = await async_client.get(
        f"{settings.API_V1_STR}/matches/{str(uuid.uuid4())}", headers=x_api_key_header
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Match not found."


async def test_get_matches_by_match_public_id(
    async_client: AsyncClient, x_api_key_header: dict[str, str], session: AsyncSession
) -> None:
    data = {
        "business_public_id": "94353293-50ed-494c-adc9-e545f6a5b2b3",
        "court_name": "0",
        "date": "2024-11-25",
        "time": 8,
    }
    prov_match_created = await generate_match(session, data)
    response = await async_client.get(
        f"{settings.API_V1_STR}/matches/",
        headers=x_api_key_header,
        params={"public_id": prov_match_created["public_id"]},
    )
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 1
    prov_match_get = content["data"][0]
    prov_match_created.pop("id")
    assert prov_match_get == prov_match_created


async def test_get_matches_by_unique_attributes(
    async_client: AsyncClient, x_api_key_header: dict[str, str], session: AsyncSession
) -> None:
    data = {
        "business_public_id": "94353293-50ed-494c-adc9-e545f6a5b2b3",
        "court_name": "0",
        "date": "2024-11-25",
        "time": 8,
    }
    prov_match_created = await generate_match(session, data)
    response = await async_client.get(
        f"{settings.API_V1_STR}/matches/",
        headers=x_api_key_header,
        params={
            "court_name": prov_match_created["court_name"],
            "time": prov_match_created["time"],
            "date": prov_match_created["date"],
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 1
    prov_match_get = content["data"][0]
    prov_match_created.pop("id")
    assert prov_match_get == prov_match_created


async def test_get_multiple_match(
    async_client: AsyncClient, x_api_key_header: dict[str, str], session: AsyncSession
) -> None:
    business_public_id = "94353293-50ed-494c-adc9-e545f6a5b2b3"
    matches_in = [
        {
            "business_public_id": business_public_id,
            "court_name": "0",
            "date": "2024-11-25",
            "time": 8,
        },
        {
            "business_public_id": business_public_id,
            "court_name": "1",
            "date": "2024-11-25",
            "time": 8,
        },
        {
            "business_public_id": business_public_id,
            "court_name": "5",
            "date": "2024-11-25",
            "time": 9,
        },
        {
            "business_public_id": business_public_id,
            "court_name": "0",
            "date": "2024-11-25",
            "time": 12,
        },
        {
            "business_public_id": business_public_id,
            "court_name": "4",
            "date": "2024-11-25",
            "time": 8,
        },
    ]
    for match_in in matches_in:
        await generate_match(session, match_in)
    response = await async_client.get(
        f"{settings.API_V1_STR}/matches/",
        headers=x_api_key_header,
        params={"time": matches_in[0].get("time")},  # type: ignore
    )
    assert response.status_code == 200
    content = response.json()
    for item in content["data"]:
        item.pop("public_id")
        item.pop("status")
        item.pop("court_public_id")
    assert content["count"] == 3
    assert matches_in[0] in content["data"]
    assert matches_in[1] in content["data"]
    assert matches_in[4] in content["data"]


async def test_update_match_status_to_reserved(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    data = {
        "business_public_id": "94353293-50ed-494c-adc9-e545f6a5b2b3",
        "court_name": "0",
        "date": "2024-11-25",
        "time": 8,
    }
    response = await create_match(async_client, x_api_key_header, data)
    match_created = response.json()

    data = {"status": MatchStatus.reserved}
    response = await async_client.patch(
        f"{test_settings.API_V1_STR}/matches/{match_created['public_id']}",
        headers=x_api_key_header,
        json=data,
    )
    assert response.status_code == 200
    match_updated = response.json()
    assert match_updated["status"] == MatchStatus.reserved
    match_updated.pop("status")
    match_created.pop("status")
    assert match_updated == match_created
