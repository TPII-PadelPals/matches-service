from datetime import datetime

from app.models.match_extended import MatchExtended
from app.models.player import Player
from app.utilities.dependencies import SessionDep


class MatchGeneratorService:
    def _get_priority_player(self, players: list[Player]) -> Player:
        return players[0]

    async def generate_matches(
        self,
        session: SessionDep,
        business_public_id: int,
        court_public_id: str,
        date: datetime,
    ) -> list[MatchExtended]:
        return []
