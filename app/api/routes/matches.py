from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.models.match import (
    Match,
    MatchCreate,
    MatchFilters,
    MatchListPublic,
    MatchPublic,
    MatchUpdate,
)
from app.models.match_extended import MatchesExtendedListPublic
from app.models.match_generation import (
    MatchGenerationCreate,
    MatchGenerationCreateExtended,
)
from app.services.bot_service import BotService
from app.services.match_generator_service import MatchGeneratorService
from app.services.match_service import MatchService
from app.utilities.dependencies import SessionDep

router = APIRouter()

match_service = MatchService()


@router.post(
    "/",
    response_model=MatchPublic,
    status_code=status.HTTP_201_CREATED,
)
async def create_match(*, session: SessionDep, match_in: MatchCreate) -> Any:
    """
    Create new match.
    """
    return await match_service.create_match(session, match_in)


@router.post(
    "/bulk",
    response_model=list[MatchPublic],
    status_code=status.HTTP_201_CREATED,
)
async def create_matches(
    *, session: SessionDep, matches_in: list[MatchCreate]
) -> list[Match]:
    """
    Create new matches.
    """
    return await match_service.create_matches(session, matches_in)


@router.post(
    "/generation",
    response_model=MatchesExtendedListPublic,
    status_code=status.HTTP_201_CREATED,
)
async def generate_matches(
    *, session: SessionDep, match_gen_create: MatchGenerationCreateExtended
) -> Any:
    """
    Generate matches given business, court and date
    """
    match_gen_service = MatchGeneratorService()
    matches_public_ids = await match_gen_service.generate_matches(
        session, match_gen_create
    )
    matches = await match_gen_service.get_matches(session, matches_public_ids)
    list_of_matches = MatchesExtendedListPublic.from_private(matches)
    message_service = BotService()
    await message_service.send_new_matches(list_of_matches.get_list_player_assigned())
    return list_of_matches


@router.post(
    "/generation/all",
    response_model=MatchesExtendedListPublic,
    status_code=status.HTTP_201_CREATED,
)
async def generate_matches_all(
    *, session: SessionDep, match_gen_create: MatchGenerationCreate
) -> Any:
    """
    Generate matches given business, court and date
    """
    match_gen_service = MatchGeneratorService()
    matches_public_ids = await match_gen_service.generate_matches_all(
        session, match_gen_create
    )
    matches = await match_gen_service.get_matches(session, matches_public_ids)
    list_of_matches = MatchesExtendedListPublic.from_private(matches)
    message_service = BotService()
    await message_service.send_new_matches(list_of_matches.get_list_player_assigned())
    return list_of_matches


@router.get("/{public_id}", status_code=status.HTTP_200_OK)
async def get_match(session: SessionDep, public_id: UUID) -> MatchPublic:
    """
    Get matches by public id.
    :param session: database.
    :return: list of matches that match the public id.
    """
    match = await match_service.get_match(session, public_id)
    match_public = MatchPublic.from_private(match)
    return match_public


@router.get("/", status_code=status.HTTP_200_OK)
async def get_matches(
    session: SessionDep, prov_match_filters: MatchFilters = Depends()
) -> MatchListPublic:
    """
    Get matches, that match the filters.
    :param session: database.
    :param prov_match_filters: filters (optional None for no filter).
    :return: list of matches that match the given filter.
    """
    matches = await match_service.get_matches(session, prov_match_filters)
    matches_public = MatchListPublic.from_private(matches)
    return matches_public


@router.patch(
    "/{public_id}",
    response_model=MatchPublic,
    status_code=status.HTTP_200_OK,
)
async def update_match(
    *,
    session: SessionDep,
    public_id: UUID,
    match_in: MatchUpdate,
) -> Any:
    """
    Update match.
    """
    return await match_service.update_match(session, public_id, match_in)
