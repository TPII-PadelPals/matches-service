from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.models.provisional_match import (
    ProvisionalMatch,
    ProvisionalMatchCreate,
    ProvisionalMatchFilters,
    ProvisionalMatchListPublic,
    ProvisionalMatchPublic,
    ProvisionalMatchUpdate,
)
from app.services.provisional_match_service import ProvisionalMatchService
from app.utilities.dependencies import SessionDep

router = APIRouter()

provisional_match_service = ProvisionalMatchService()


@router.post(
    "/",
    response_model=ProvisionalMatchPublic,
    status_code=status.HTTP_201_CREATED,
)
async def create_provisional_match(
    *, session: SessionDep, provisional_match_in: ProvisionalMatchCreate
) -> Any:
    """
    Create new provisional match.
    """
    return await provisional_match_service.create_match(session, provisional_match_in)


@router.post(
    "/bulk",
    response_model=list[ProvisionalMatchPublic],
    status_code=status.HTTP_201_CREATED,
)
async def create_provisional_matches(
    *, session: SessionDep, provisional_matches_in: list[ProvisionalMatchCreate]
) -> list[ProvisionalMatch]:
    """
    Create new provisional matches.
    """
    return await provisional_match_service.create_matches(
        session, provisional_matches_in
    )


@router.get("/", status_code=status.HTTP_200_OK)
async def get_provisional_match(
    session: SessionDep, prov_match_filters: ProvisionalMatchFilters = Depends()
) -> ProvisionalMatchListPublic:
    """
    Get provisional matches, that match the filters.
    :param session: database.
    :param prov_match_filters: filters (optional None for no filter).
    :return: list of matches that match the given filter.
    """
    matches = await provisional_match_service.get_filter_match(
        session, prov_match_filters
    )
    matches_public = ProvisionalMatchListPublic(
        data=[ProvisionalMatchPublic.from_private(match) for match in matches],
        count=len(matches),
    )
    return matches_public


@router.patch(
    "/{public_id}",
    response_model=ProvisionalMatchPublic,
    status_code=status.HTTP_200_OK,
)
async def update_provisional_match(
    *,
    session: SessionDep,
    public_id: UUID,
    provisional_match_in: ProvisionalMatchUpdate,
) -> Any:
    """
    Update provisional match.
    """
    return await provisional_match_service.update_match(
        session, public_id, provisional_match_in
    )
