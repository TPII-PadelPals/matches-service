from uuid import UUID

from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.match_player import (
    MatchPlayer,
    MatchPlayerCreate,
    MatchPlayerFilter,
    MatchPlayerUpdate,
)
from app.utilities.exceptions import NotFoundException, NotUniqueException


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

    async def read_matches_players(
        self, filters: list[MatchPlayerFilter]
    ) -> list[MatchPlayer]:
        or_conditions = []

        # Player filter conditions
        for filter in filters:
            and_conditions = []
            # Iterate through attributes and their values
            for attr, value in vars(filter).items():
                if value is not None:
                    and_conditions.append(getattr(MatchPlayer, attr) == value)
            # Combine conditions with AND
            or_conditions.append(and_(*and_conditions))

        # Combine conditions with OR
        query = select(MatchPlayer).where(or_(*or_conditions))

        # Execute query
        result = await self.session.exec(query)
        matches = result.all()
        return list(matches)

    async def read_match_player(
        self, match_public_id: UUID, user_public_id: UUID
    ) -> MatchPlayer:
        result = await self.read_matches_players(
            [
                MatchPlayerFilter(
                    match_public_id=match_public_id, user_public_id=user_public_id
                )
            ]
        )
        match_player = result[0] if result else None
        if match_player is None:
            raise NotFoundException("Couple (match, player)")
        return match_player

    async def update_match_player(
        self,
        match_public_id: UUID,
        user_public_id: UUID,
        match_player_in: MatchPlayerUpdate,
    ) -> MatchPlayer:
        match_player = await self.read_match_player(match_public_id, user_public_id)
        update_dict = match_player_in.model_dump()
        match_player.sqlmodel_update(update_dict)
        self.session.add(match_player)
        await self._commit_with_exception_handling()
        await self.session.refresh(match_player)
        return match_player
