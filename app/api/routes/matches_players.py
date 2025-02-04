from typing import Any
from uuid import UUID

from fastapi import APIRouter, status

from app.models.match_player import (
    MatchPlayerCreate,
    MatchPlayerCreatePublic,
    MatchPlayerPublic,
    MatchPlayerUpdate,
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


@router.post(
    "/bulk",
    response_model=list[MatchPlayerPublic],
    status_code=status.HTTP_201_CREATED,
)
async def create_provisional_matches(
    *,
    session: SessionDep,
    match_public_id: UUID,
    match_players_in: list[MatchPlayerCreatePublic],
) -> list[MatchPlayerPublic]:
    """
    Create new provisional matches.
    """
    match_players_create = [
        MatchPlayerCreate.from_public(match_public_id, match_player_in)
        for match_player_in in match_players_in
    ]
    match_players = await matches_service.create_match_players(
        session, match_players_create
    )
    match_players_public = [
        MatchPlayerPublic.from_private(match_player) for match_player in match_players
    ]
    return match_players_public


@router.patch(
    "/{user_public_id}/",
    response_model=MatchPlayerPublic,
    status_code=status.HTTP_200_OK,
)
async def update_match_player(
    *,
    session: SessionDep,
    match_public_id: UUID,
    user_public_id: UUID,
    match_player_in: MatchPlayerUpdate,
) -> Any:
    """
    Update match player.
    """
    return await matches_service.update_match_player(
        session, match_public_id, user_public_id, match_player_in
    )
