from uuid import UUID

from fastapi import APIRouter, status

from app.models.match_player import (
    MatchPlayerCreate,
    MatchPlayerCreatePublic,
    MatchPlayerListPublic,
    MatchPlayerPublic,
    MatchPlayerUpdate,
)
from app.services.match_service import MatchService
from app.utilities.dependencies import SessionDep

router = APIRouter()

matches_service = MatchService()


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
    match_player = await matches_service.create_match_player(
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
    match_players = await matches_service.create_match_players(
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
async def read_match_players(
    *, session: SessionDep, match_public_id: UUID
) -> MatchPlayerListPublic:
    """
    Read match player.
    """
    match_players = await matches_service.read_match_players(session, match_public_id)
    match_players_public = MatchPlayerListPublic(
        data=[
            MatchPlayerPublic.from_private(match_player)
            for match_player in match_players
        ],
        count=len(match_players),
    )
    return match_players_public


@router.get(
    "/{user_public_id}",
    response_model=MatchPlayerPublic,
    status_code=status.HTTP_200_OK,
)
async def read_match_player(
    *, session: SessionDep, match_public_id: UUID, user_public_id: UUID
) -> MatchPlayerPublic:
    """
    Read match player.
    """
    match_player = await matches_service.read_match_player(
        session, match_public_id, user_public_id
    )
    match_player_public = MatchPlayerPublic.from_private(match_player)
    return match_player_public


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
) -> MatchPlayerPublic:
    """
    Update match player.
    """
    match_player = await matches_service.update_match_player(
        session, match_public_id, user_public_id, match_player_in
    )
    match_player_public = MatchPlayerPublic.from_private(match_player)
    return match_player_public
