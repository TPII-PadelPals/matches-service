from fastapi import APIRouter, Depends, HTTPException, status

from app.models.provisional_match import (
    ProvisionalMatchCreate,
    ProvisionalMatchFilters,
    ProvisionalMatchPublic,
)
from app.repository.provisional_match_repository import ProvisionalMatchRepository
from app.utilities.dependencies import SessionDep

router = APIRouter()


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
    try:
        repo = ProvisionalMatchRepository(session)
        provisional_match = await repo.create_provisional_match(provisional_match_in)
        return provisional_match
    except Exception:
        raise HTTPException(
            status_code=500, detail="No se ha podido ingresar la partida"
        )


@router.post(
    "/bulk",
    response_model=list[ProvisionalMatchPublic],
    status_code=status.HTTP_201_CREATED,
)
async def create_provisional_matches(
    *, session: SessionDep, provisional_matches_in: list[ProvisionalMatchCreate]
) -> any:
    """
    Create new provisional matches.
    """
    try:
        repo = ProvisionalMatchRepository(session)
        provisional_match = await repo.create_provisional_matches(
            provisional_matches_in
        )
        return provisional_match
    except Exception:
        raise HTTPException(
            status_code=500, detail="No se han podido ingresar las partidas"
        )


@router.get("/", status_code=status.HTTP_200_OK)
async def get_provisional_match(
    session: SessionDep, prov_match_opt: ProvisionalMatchFilters = Depends()
):
    repo_provisional_match = ProvisionalMatchRepository(session)
    alternative_prov_match_opt = prov_match_opt.rotate_players_ids()
    info_to_filter = [prov_match_opt, alternative_prov_match_opt]
    matches = await repo_provisional_match.get_provisional_matches(info_to_filter)
    return matches
