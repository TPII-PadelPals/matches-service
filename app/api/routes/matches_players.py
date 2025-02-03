from typing import Any
from uuid import UUID

from fastapi import APIRouter, status

from app.models.match_player import (
    MatchPlayerCreate,
    MatchPlayerCreatePublic,
    MatchPlayerPublic,
)
from app.services.provisional_match_service import ProvisionalMatchService
from app.utilities.dependencies import SessionDep

router = APIRouter()

matches_service = ProvisionalMatchService()


@router.post(
    "/",
    response_model=MatchPlayerPublic,
    status_code=status.HTTP_201_CREATED,
)
async def create_match_player(
    *,
    session: SessionDep,
    match_public_id: UUID,
    match_player_in: MatchPlayerCreatePublic,
) -> Any:
    """
    Create new match player.
    """
    match_player_create = MatchPlayerCreate.from_public(
        match_public_id, match_player_in
    )
    return await matches_service.create_match_player(session, match_player_create)
