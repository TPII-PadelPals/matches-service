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
        self, match_player_in: MatchPlayerCreate, should_commit: bool = True
    ) -> MatchPlayer:
        return await self.create_record(MatchPlayer, match_player_in, should_commit)

    async def create_match_players(
        self, match_players_in: list[MatchPlayerCreate], should_commit: bool = True
    ) -> list[MatchPlayer]:
        return await self.create_records(MatchPlayer, match_players_in, should_commit)

    async def get_matches_players(
        self,
        filters: list[MatchPlayerFilter],
        orders: list[tuple[str, str]] | None = None,
        limit: int | None = None,
    ) -> list[MatchPlayer]:
        return await self.get_records(MatchPlayer, filters, orders, limit)

    async def get_match_player(
        self, match_public_id: UUID, user_public_id: UUID
    ) -> MatchPlayer:
        return await self.get_record(
            MatchPlayer,
            MatchPlayerFilter,
            {"match_public_id": match_public_id, "user_public_id": user_public_id},
        )

    async def update_match_player(
        self,
        match_public_id: UUID,
        user_public_id: UUID,
        match_player_in: MatchPlayerUpdate,
        should_commit: bool = True,
    ) -> MatchPlayer:
        return await self.update_record(
            MatchPlayer,
            MatchPlayerFilter,
            {"match_public_id": match_public_id, "user_public_id": user_public_id},
            match_player_in,
            should_commit,
        )
