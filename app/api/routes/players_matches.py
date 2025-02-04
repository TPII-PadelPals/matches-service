from uuid import UUID

from fastapi import APIRouter, status

from app.models.match_player import MatchPlayerListPublic, MatchPlayerPublic
from app.services.match_player_service import MatchPlayerService
from app.utilities.dependencies import SessionDep

router = APIRouter()

mp_service = MatchPlayerService()


@router.get(
    "/",
    response_model=MatchPlayerListPublic,
    status_code=status.HTTP_200_OK,
)
async def read_player_matches(
    *, session: SessionDep, user_public_id: UUID
) -> MatchPlayerListPublic:
    """
    Read player matches.
    """
    match_players = await mp_service.read_player_matches(session, user_public_id)
    match_players_public = MatchPlayerListPublic(
        data=[
            MatchPlayerPublic.from_private(match_player)
            for match_player in match_players
        ],
        count=len(match_players),
    )
    return match_players_public
