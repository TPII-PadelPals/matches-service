import datetime
import uuid
from typing import Any

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.available_time import AvailableTime
from app.models.match_generation import MatchGenerationCreate
from app.models.player import Player
from app.services.business_service import BusinessService
from app.services.match_generator_service import MatchGeneratorService
from app.services.players_service import PlayersService
from app.tests.utils.utils import get_mock_get_players_by_filters


async def test_generate_matches_twice_for_the_same_day_and_same_times(
    session: AsyncSession, monkeypatch: Any
) -> None:
    # Test ctes
    business_public_id = str(uuid.uuid4())
    court_public_id = str(uuid.uuid4())
    court_name = "1"
    date = "2025-03-19"
    times = [8, 9, 10]
    latitude = 0.0
    longitude = 0.0
    n_similar_players = 6

    # Mock BusinessService
    avail_times = [
        AvailableTime(
            business_public_id=business_public_id,
            court_public_id=court_public_id,
            court_name=court_name,
            latitude=latitude,
            longitude=longitude,
            date=date,
            time=time,
            is_reserved=False,
        )
        for time in times
    ]

    async def mock_get_available_times(
        self: Any,  # noqa: ARG001
        business_public_id: uuid.UUID,  # noqa: ARG001
        court_name: str,  # noqa: ARG001
        date: datetime.date,  # noqa: ARG001
    ) -> Any:
        return avail_times

    monkeypatch.setattr(
        BusinessService, "get_available_times", mock_get_available_times
    )

    # Mock PlayersService
    mock_get_players_by_filters, assigned_players = get_mock_get_players_by_filters(
        times, n_similar_players
    )
    monkeypatch.setattr(
        PlayersService, "get_players_by_filters", mock_get_players_by_filters
    )

    # Mock MatchGeneratorService
    def mock_choose_priority_player(
        self: Any,  # noqa: ARG001
        players: list[Player],  # noqa: ARG001
    ) -> Player:
        time_availability = players[0].time_availability
        return assigned_players[time_availability]["assigned"]  # type: ignore

    monkeypatch.setattr(
        MatchGeneratorService, "_choose_priority_player", mock_choose_priority_player
    )

    # Main request
    data = {
        "business_public_id": business_public_id,
        "court_name": court_name,
        "date": date,
    }
    match_gen_create = MatchGenerationCreate(**data)
    service = MatchGeneratorService()

    response = await service.generate_matches(session, match_gen_create)

    assert response is not None
    # TEST
    response_for_new_generate = await service.generate_matches(
        session, match_gen_create
    )
    # ASSERT
    assert response_for_new_generate is not None


async def test_generate_matches_for_the_same_with_new_times_twice(
    session: AsyncSession, monkeypatch: Any
) -> None:
    # Test ctes
    business_public_id = str(uuid.uuid4())
    court_public_id = str(uuid.uuid4())
    court_name = "1"
    date = "2025-03-19"
    times = [11, 7, 8, 9, 10]
    latitude = 0.0
    longitude = 0.0
    n_similar_players = 6

    # add times
    new_times = [6, 7, 8, 9, 10, 11, 12, 13, 14]
    # Mock BusinessService
    avail_times = [
        AvailableTime(
            business_public_id=business_public_id,
            court_public_id=court_public_id,
            court_name=court_name,
            latitude=latitude,
            longitude=longitude,
            date=date,
            time=time,
            is_reserved=False,
        )
        for time in times
    ]

    async def mock_get_available_times(
        self: Any,  # noqa: ARG001
        business_public_id: uuid.UUID,  # noqa: ARG001
        court_name: str,  # noqa: ARG001
        date: datetime.date,  # noqa: ARG001
    ) -> Any:
        return avail_times

    monkeypatch.setattr(
        BusinessService, "get_available_times", mock_get_available_times
    )

    # Mock PlayersService
    mock_get_players_by_filters, assigned_players = get_mock_get_players_by_filters(
        new_times, n_similar_players
    )
    monkeypatch.setattr(
        PlayersService, "get_players_by_filters", mock_get_players_by_filters
    )

    # Mock MatchGeneratorService
    def mock_choose_priority_player(
        self: Any,  # noqa: ARG001
        players: list[Player],  # noqa: ARG001
    ) -> Player:
        time_availability = players[0].time_availability
        return assigned_players[time_availability]["assigned"]  # type: ignore

    monkeypatch.setattr(
        MatchGeneratorService, "_choose_priority_player", mock_choose_priority_player
    )

    # Main request
    service = MatchGeneratorService()
    data = {
        "business_public_id": business_public_id,
        "court_name": court_name,
        "date": date,
    }
    match_gen_create = MatchGenerationCreate(**data)
    response = await service.generate_matches(session, match_gen_create)

    assert len(response) == 5

    # Mock BusinessService
    new_avail_times = [
        AvailableTime(
            business_public_id=business_public_id,
            court_public_id=court_public_id,
            court_name=court_name,
            latitude=latitude,
            longitude=longitude,
            date=date,
            time=time,
            is_reserved=False,
        )
        for time in new_times
    ]

    async def mock_get_available_times_new(
        self: Any,  # noqa: ARG001
        business_public_id: uuid.UUID,  # noqa: ARG001
        court_name: str,  # noqa: ARG001
        date: datetime.date,  # noqa: ARG001
    ) -> Any:
        return new_avail_times

    monkeypatch.setattr(
        BusinessService, "get_available_times", mock_get_available_times_new
    )

    match_gen_create_new = MatchGenerationCreate(**data)
    response_for_new_generate = await service.generate_matches(
        session, match_gen_create_new
    )

    assert len(response_for_new_generate) == 4
    # TEST

    response_for_new_generate_double = await service.generate_matches(
        session, match_gen_create_new
    )
    # ASSERT
    assert len(response_for_new_generate_double) == 0
