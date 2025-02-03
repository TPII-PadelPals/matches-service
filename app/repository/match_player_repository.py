from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.match_player import (
    MatchPlayer,
    MatchPlayerCreate,
)
from app.utilities.exceptions import NotUniqueException


class MatchPlayerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _commit_with_exception_handling(self) -> None:
        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            if "uq_match_player" in str(e.orig):
                raise NotUniqueException("Couple (match, player)")
            else:
                raise e

    async def create_match_player(
        self, match_player_in: MatchPlayerCreate
    ) -> MatchPlayer:
        match_player = MatchPlayer.model_validate(match_player_in)
        self.session.add(match_player)
        await self._commit_with_exception_handling()
        await self.session.refresh(match_player)
        return match_player

    async def create_match_players(
        self, match_players_in: list[MatchPlayerCreate]
    ) -> list[MatchPlayer]:
        match_players = [
            MatchPlayer.model_validate(match_player)
            for match_player in match_players_in
        ]
        self.session.add_all(match_players)
        await self._commit_with_exception_handling()
        for match_player in match_players:
            await self.session.refresh(match_player)
        return match_players
