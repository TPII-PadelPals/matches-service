from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.models.match_player import (
    MatchPlayer,
    MatchPlayerCreate,
    MatchPlayerFilter,
    MatchPlayerUpdate,
)
from app.repository.base_repository import BaseRepository
from app.utilities.exceptions import NotUniqueException


class MatchPlayerRepository(BaseRepository):
    def _handle_commit_exceptions(self, err: IntegrityError) -> None:
        if "uq_match_player" in str(err.orig):
            raise NotUniqueException("MatchPlayer")
        else:
            raise err

    async def create_match_player(
        self, match_player_in: MatchPlayerCreate
    ) -> MatchPlayer:
        return await self.create_record(MatchPlayer, match_player_in)

    async def create_match_players(
        self, match_players_in: list[MatchPlayerCreate]
    ) -> list[MatchPlayer]:
        return await self.create_records(MatchPlayer, match_players_in)

    async def read_matches_players(
        self, filters: list[MatchPlayerFilter]
    ) -> list[MatchPlayer]:
        return await self.read_records(MatchPlayer, filters)

    async def read_match_player(
        self, match_public_id: UUID, user_public_id: UUID
    ) -> MatchPlayer:
        return await self.read_record(
            MatchPlayer,
            MatchPlayerFilter,
            {"match_public_id": match_public_id, "user_public_id": user_public_id},
        )

    async def update_match_player(
        self,
        match_public_id: UUID,
        user_public_id: UUID,
        match_player_in: MatchPlayerUpdate,
    ) -> MatchPlayer:
        return await self.update_record(
            MatchPlayer,
            MatchPlayerFilter,
            {"match_public_id": match_public_id, "user_public_id": user_public_id},
            match_player_in,
        )
