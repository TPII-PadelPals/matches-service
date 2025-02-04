from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.models.match_player import (
    MatchPlayer,
    MatchPlayerCreate,
    MatchPlayerFilter,
    MatchPlayerUpdate,
)
from app.repository.base_repository import BaseRepository
from app.utilities.exceptions import NotFoundException, NotUniqueException


class MatchPlayerRepository(BaseRepository):
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
        return await self.filter_records(MatchPlayer, filters)

    async def read_match_player(
        self, match_public_id: UUID, user_public_id: UUID
    ) -> MatchPlayer:
        filters = [
            MatchPlayerFilter(
                match_public_id=match_public_id, user_public_id=user_public_id
            )
        ]
        result = await self.read_matches_players(filters)
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
