from typing import Any

from sqlalchemy.exc import IntegrityError

from app.models.match import (
    Match,
    MatchCreate,
    MatchUpdate,
)
from app.repository.base_repository import BaseRepository
from app.utilities.exceptions import NotUniqueException


class MatchRepository(BaseRepository):
    def _handle_commit_exceptions(self, err: IntegrityError) -> None:
        if "uq_match_constraints" in str(err.orig):
            raise NotUniqueException("Match")
        else:
            raise err

    async def create_match(
        self, match_in: MatchCreate, should_commit: bool = True
    ) -> Match:
        return await self.create_record(Match, match_in, should_commit)

    async def create_matches(
        self, matches_in: list[MatchCreate], should_commit: bool = True
    ) -> list[Match]:
        return await self.create_records(Match, matches_in, should_commit)

    async def get_matches(self, **filters: Any) -> list[Match]:
        return await self.get_records(Match, **filters)

    async def get_match(self, **filters: Any) -> Match:
        return await self.get_record(Match, **filters)

    async def update_match(
        self, match_in: MatchUpdate, should_commit: bool = True, **filters: Any
    ) -> Match:
        return await self.update_record(Match, match_in, should_commit, **filters)
