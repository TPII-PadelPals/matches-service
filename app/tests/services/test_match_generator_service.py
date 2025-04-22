import uuid
from typing import Any

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.match_generation import MatchGenerationCreate
from app.services.business_service import BusinessService
from app.services.match_generator_service import MatchGeneratorService
from app.tests.utils.utils import (
    get_mock_get_available_times,
    initial_apply_mocks_for_generate_matches,
)


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

    _ = initial_apply_mocks_for_generate_matches(
        monkeypatch,
        business_public_id,
        court_public_id,
        court_name,
        date,
        times,
        times,
        latitude,
        longitude,
        n_similar_players,
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

    _ = initial_apply_mocks_for_generate_matches(
        monkeypatch,
        business_public_id,
        court_public_id,
        court_name,
        date,
        times,
        new_times,
        latitude,
        longitude,
        n_similar_players,
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
    mock_get_available_times_new = get_mock_get_available_times(
        business_public_id,
        court_public_id,
        court_name,
        date,
        new_times,
        latitude,
        longitude,
    )
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
