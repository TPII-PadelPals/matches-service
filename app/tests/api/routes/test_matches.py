import uuid
from datetime import datetime
from typing import Any

from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings, test_settings
from app.models.available_time import AvailableTime
from app.models.match import MatchStatus
from app.models.match_player import ReserveStatus
from app.models.player import Player, PlayerFilters
from app.services.business_service import BusinessService
from app.services.match_generator_service import MatchGeneratorService
from app.services.players_service import PlayersService
from app.tests.utils.matches import (
    create_match,
    generate_match,
    serialize_match_data,
)
from app.utilities.exceptions import NotUniqueException


async def test_create_match(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    data = serialize_match_data(court_id="0", time=8, date="2024-11-25")
    response = await create_match(async_client, x_api_key_header, data)
    assert response.status_code == 201
    content = response.json()
    public_id = content.pop("public_id")
    assert len(public_id) == len(str(uuid.uuid4()))
    assert content["status"] == MatchStatus.provisional
    content.pop("status")
    assert content == data


async def test_create_multiple_matches_returns_all(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    data = [
        serialize_match_data(court_id="0", time=8, date="2024-11-25"),
        serialize_match_data(court_id="1", time=8, date="2024-11-25"),
        serialize_match_data(court_id="1", time=9, date="2024-11-25"),
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
    assert len(content) == 3
    assert all(item in content for item in data)


async def test_create_matches_on_multiple_raises_not_unique_exception(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    data = serialize_match_data(court_id="0", time=8, date="2024-11-25")
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
    data = serialize_match_data(court_id="0", time=8, date="2024-11-25")
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
    data = serialize_match_data(court_id="0", time=8, date="2024-11-25")
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
    data = serialize_match_data(court_id="0", time=8, date="2024-11-25")
    prov_match_created = await generate_match(session, data)
    response = await async_client.get(
        f"{settings.API_V1_STR}/matches/",
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
    prov_match_get = content["data"][0]
    prov_match_created.pop("id")
    assert prov_match_get == prov_match_created


async def test_get_multiple_match(
    async_client: AsyncClient, x_api_key_header: dict[str, str], session: AsyncSession
) -> None:
    matches_in = [
        serialize_match_data(court_id="0", time=8, date="2024-11-25"),
        serialize_match_data(court_id="1", time=8, date="2024-11-25"),
        serialize_match_data(court_id="5", time=9, date="2024-11-25"),
        serialize_match_data(court_id="0", time=12, date="2024-11-25"),
        serialize_match_data(court_id="4", time=8, date="2024-01-05"),
    ]
    for match_in in matches_in:
        await generate_match(session, match_in)
    response = await async_client.get(
        f"{settings.API_V1_STR}/matches/",
        headers=x_api_key_header,
        params={"time": matches_in[0].get("time")},
    )
    assert response.status_code == 200
    content = response.json()
    for item in content["data"]:
        item.pop("public_id")
        item.pop("status")
    assert content["count"] == 3
    assert matches_in[0] in content["data"]
    assert matches_in[1] in content["data"]
    assert matches_in[4] in content["data"]


async def test_update_match_status_to_reserved(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    data = serialize_match_data(court_id="0", time=8, date="2024-11-25")
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


async def test_generate_matches_given_one_avail_time(
    async_client: AsyncClient, x_api_key_header: dict[str, str], monkeypatch: Any
) -> None:
    # Test ctes
    business_public_id = 1000
    court_public_id = "1"
    date = "2025-03-19"
    time = 9
    latitude = 0.0
    longitude = 0.0
    assigned_user_public_id = uuid.uuid4()
    n_similar_players = 6

    # Mock BusinessService
    avail_times = [
        AvailableTime(
            business_public_id=business_public_id,
            court_public_id=court_public_id,
            latitude=latitude,
            longitude=longitude,
            date=date,
            time=time,
            is_reserved=False,
        )
    ]

    async def mock_get_available_times(
        self: Any,  # noqa: ARG001
        business_public_id: int,  # noqa: ARG001
        court_public_id: str,  # noqa: ARG001
        date: datetime,  # noqa: ARG001
    ) -> Any:
        return avail_times

    monkeypatch.setattr(
        BusinessService, "get_available_times", mock_get_available_times
    )

    # Mock PlayersService
    assigned_player = Player(user_public_id=assigned_user_public_id)
    similar_players = [
        Player(user_public_id=uuid.uuid4()) for _ in range(n_similar_players)
    ]
    similar_players_user_public_ids = [
        str(player.user_public_id) for player in similar_players
    ]
    avail_players = [assigned_player] + similar_players

    async def mock_get_players_by_filters(
        self: Any,  # noqa: ARG001
        player_filters: PlayerFilters,  # noqa: ARG001
    ) -> Any:
        if player_filters.user_public_id == assigned_user_public_id:
            return similar_players
        return avail_players

    monkeypatch.setattr(
        PlayersService, "get_players_by_filters", mock_get_players_by_filters
    )

    # Mock MatchGeneratorService
    def mock_choose_priority_player(
        self: Any,  # noqa: ARG001
        players: list[Player],  # noqa: ARG001
    ) -> Player:
        return assigned_player

    monkeypatch.setattr(
        MatchGeneratorService, "_choose_priority_player", mock_choose_priority_player
    )

    # Main request
    data = {
        "business_public_id": business_public_id,
        "court_public_id": court_public_id,
        "date": date,
    }
    response = await async_client.post(
        f"{test_settings.API_V1_STR}/matches/generation",
        headers=x_api_key_header,
        json=data,
    )

    # Assertions
    assert response.status_code == 201

    matches_list = response.json()
    matches = matches_list["data"]
    assert len(matches) == 1

    match_extended = matches[0]
    # TODO: In Match, add business_public_id
    # assert match_extended["business_public_id"] == business_public_id
    # TODO: In Match, rename court_id to court_public_id
    assert match_extended["court_id"] == court_public_id
    assert match_extended["date"] == date
    assert match_extended["time"] == time

    match_players = match_extended["match_players"]
    match_assigned_players = [
        player
        for player in match_players
        if player["reserve"] == ReserveStatus.Assigned
    ]
    assert len(match_assigned_players) == 1

    match_assigned_player = match_assigned_players[0]
    assert match_assigned_player["user_public_id"] == str(
        assigned_player.user_public_id
    )

    match_similar_players_user_public_ids = [
        player["user_public_id"]
        for player in match_players
        if player["reserve"] == ReserveStatus.Similar
    ]
    assert set(match_similar_players_user_public_ids) == set(
        similar_players_user_public_ids
    )
