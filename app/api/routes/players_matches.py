from uuid import UUID

from fastapi import APIRouter, status

from app.models.match_extended import MatchesExtendedListPublic
from app.services.get_player_matches_service import GetPlayerMatchesService
from app.services.match_player_service import MatchPlayerService
from app.utilities.dependencies import SessionDep

router = APIRouter()

match_player_service = MatchPlayerService()


@router.get(
    "/",
    response_model=MatchesExtendedListPublic,
    status_code=status.HTTP_200_OK,
)
async def get_player_matches(
    *, session: SessionDep, user_public_id: UUID
) -> MatchesExtendedListPublic:
    """
    Get player matches.
    """
    aux_service = GetPlayerMatchesService()
    match_info = await aux_service.get_player_matches(session, user_public_id)
    match_players_public = MatchesExtendedListPublic.from_private(match_info)
    return match_players_public
