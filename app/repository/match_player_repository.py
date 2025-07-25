from typing import Any

from sqlalchemy.exc import IntegrityError

from app.models.match_player import (
    MatchPlayer,
    MatchPlayerCreate,
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
        order_by: list[tuple[str, bool]] | None = None,
        limit: int | None = None,
        **filters: Any,
    ) -> list[MatchPlayer]:
        """
        order_by: List of tuples(Player.attribute, is_ascending)
        to order the result.
        limit: Max number of players to get.
        """
        return await self.get_records(MatchPlayer, order_by, limit, **filters)

    async def get_match_player(self, **filters: Any) -> MatchPlayer:
        return await self.get_record(MatchPlayer, **filters)

    async def update_match_player(
        self,
        match_player_in: MatchPlayerUpdate,
        should_commit: bool = True,
        **filters: Any,
    ) -> MatchPlayer:
        return await self.update_record(
            MatchPlayer, match_player_in, should_commit, **filters
        )

    async def delete_match_players(
        self, should_commit: bool = True, **filters: Any
    ) -> None:
        await self.delete_records(MatchPlayer, should_commit, **filters)
