from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.match_player import (
    MatchPlayer,
    MatchPlayerCreate,
)


class MatchPlayerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_match_player(
        self, match_player_in: MatchPlayerCreate
    ) -> MatchPlayer:
        match_player = MatchPlayer.model_validate(match_player_in)
        self.session.add(match_player)
        await self.session.commit()
        await self.session.refresh(match_player)
        return match_player
