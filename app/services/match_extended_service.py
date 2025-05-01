import uuid

from app.models.match import Match
from app.models.match_extended import MatchExtended
from app.models.match_player import MatchPlayer
from app.services.match_player_service import MatchPlayerService
from app.services.match_service import MatchService
from app.utilities.dependencies import SessionDep


class MatchExtendedService:
    async def get_match(
        self, session: SessionDep, match_public_id: uuid.UUID
    ) -> MatchExtended:
        match = await MatchService().get_match(session, match_public_id)
        match_players = await MatchPlayerService().get_match_players(
            session, match_public_id
        )
        return MatchExtended(match, match_players)

    async def get_player_matches(
        self, session: SessionDep, player_id: uuid.UUID
    ) -> list[MatchExtended]:
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
            match: Match = await match_service.get_match(session, match_id)
            match_players = await match_player_service.get_match_players(
                session, match_id
            )
            if match_players is None:
                continue
            result.append(MatchExtended(match, match_players))
        return result
