import uuid

from app.models.match import Match
from app.models.match_extended import MatchExtended
from app.models.match_player import MatchPlayer
from app.services.match_player_service import MatchPlayerService
from app.services.match_service import MatchService
from app.utilities.dependencies import SessionDep


class GetPlayerMatchesService:
    async def get_player_matches(
        self, session: SessionDep, player_id: uuid.UUID
    ) -> list[MatchExtended]:
        # ) -> MatchesExtendedListPublic:
        match_player_service = MatchPlayerService()
        player_matches: list[
            MatchPlayer
        ] = await match_player_service.get_player_matches(session, player_id)
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
            list_of_players = await match_player_service.get_match_players(
                session, match_id
            )
            if list_of_players is None:
                continue
            # result.append((match_for_player_match, list_of_players))
            result.append(MatchExtended(match_for_player_match, list_of_players))
        # return MatchesExtendedListPublic.from_private(result)
        return result
