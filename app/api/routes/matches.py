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
