from typing import Any
from uuid import UUID

from fastapi import APIRouter, status

from app.models.match_player import (
    MatchPlayerCreate,
    MatchPlayerCreatePublic,
    MatchPlayerListPublic,
    MatchPlayerPayPublic,
    MatchPlayerPublic,
    MatchPlayerUpdate,
)
from app.services.match_player_service import MatchPlayerService
from app.services.match_player_update_service import MatchPlayerUpdateService
from app.utilities.dependencies import SessionDep
from app.utilities.messages import PATCH_MATCHES_PLAYERS

router = APIRouter()

match_player_service = MatchPlayerService()


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
) -> MatchPlayerPublic:
    """
    Create new match player.
    """
    match_player_create = MatchPlayerCreate.from_public(
        match_public_id, match_player_in
    )
    match_player = await match_player_service.create_match_player(
        session, match_player_create
    )
    match_player_public = MatchPlayerPublic.from_private(match_player)
    return match_player_public


@router.post(
    "/bulk/",
    response_model=list[MatchPlayerPublic],
    status_code=status.HTTP_201_CREATED,
)
async def create_matches(
    *,
    session: SessionDep,
    match_public_id: UUID,
    match_players_in: list[MatchPlayerCreatePublic],
) -> list[MatchPlayerPublic]:
    """
    Create new matches.
    """
    match_players_create = [
        MatchPlayerCreate.from_public(match_public_id, match_player_in)
        for match_player_in in match_players_in
    ]
    match_players = await match_player_service.create_match_players(
        session, match_players_create
    )
    match_players_public = [
        MatchPlayerPublic.from_private(match_player) for match_player in match_players
    ]
    return match_players_public


@router.get(
    "/",
    response_model=MatchPlayerListPublic,
    status_code=status.HTTP_200_OK,
)
async def get_match_players(
    *, session: SessionDep, match_public_id: UUID
) -> MatchPlayerListPublic:
    """
    Get match player.
    """
    match_players = await match_player_service.get_match_players(
        session, match_public_id=match_public_id
    )
    match_players_public = MatchPlayerListPublic.from_private(match_players)
    return match_players_public


@router.get(
    "/{user_public_id}",
    response_model=MatchPlayerPublic,
    status_code=status.HTTP_200_OK,
)
async def get_match_player(
    *, session: SessionDep, match_public_id: UUID, user_public_id: UUID
) -> MatchPlayerPublic:
    """
    Get match player.
    """
    match_player = await match_player_service.get_match_player(
        session, match_public_id, user_public_id
    )
    match_player_public = MatchPlayerPublic.from_private(match_player)
    return match_player_public


@router.patch(
    "/{user_public_id}/",
    response_model=MatchPlayerPayPublic,
    responses={**PATCH_MATCHES_PLAYERS},  # type: ignore[dict-item]
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
    match_player = await MatchPlayerUpdateService().update_match_player(
        session, match_public_id, user_public_id, match_player_in
    )
    return match_player
