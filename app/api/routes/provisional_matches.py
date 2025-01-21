from fastapi import APIRouter, Depends, status

from app.models.provisional_match import (
    ProvisionalMatchCreate,
    ProvisionalMatchFilters,
    ProvisionalMatchPublic,
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
) -> any:
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
) -> list:
    """
    Create new provisional matches.
    """
    return await provisional_match_service.create_matches(
        session, provisional_matches_in
    )


@router.get("/", status_code=status.HTTP_200_OK)
async def get_provisional_match(
    session: SessionDep, prov_match_filters: ProvisionalMatchFilters = Depends()
) -> list[ProvisionalMatchPublic]:
    """
    Get provisional matches, that match the filters.
    :param session: database.
    :param prov_match_filters: filters (optional None for no filter).
    :return: list of matches that match the given filter.
    """
    return await provisional_match_service.get_filter_match(session, prov_match_filters)
