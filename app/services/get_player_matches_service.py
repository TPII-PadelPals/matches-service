import uuid

from app.models.match import Match
from app.models.match_player import MatchPlayer
from app.services.match_player_service import MatchPlayerService
from app.services.match_service import MatchService
from app.utilities.dependencies import SessionDep


class GetPlayerMatchesService:
    async def get_player_matches(
        self, session: SessionDep, player_id: uuid.UUID
    ) -> list[tuple[MatchPlayer, Match]]:
        player_matches: list[
            MatchPlayer
        ] = await MatchPlayerService().get_player_matches(session, player_id)
        if not player_matches:
            return []
        result = []
        match_service = MatchService()
        for player_match in player_matches:
            match_id = player_match.match_public_id
            if match_id is None:
                continue
            match_for_player_match: Match = await match_service.get_match(
                session, match_id
            )
            result.append((player_match, match_for_player_match))
        return result
