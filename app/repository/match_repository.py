from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.models.match import (
    Match,
    MatchCreate,
    MatchFilters,
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

    async def create_match(self, match_in: MatchCreate) -> Match:
        return await self.create_record(Match, match_in)

    async def create_matches(self, matches_in: list[MatchCreate]) -> list[Match]:
        return await self.create_records(Match, matches_in)

    async def get_matches(self, filters: list[MatchFilters]) -> list[Match]:
        return await self.get_records(Match, filters)

    async def get_match(self, public_id: UUID) -> Match:
        return await self.get_record(Match, MatchFilters, {"public_id": public_id})

    async def update_match(
        self,
        public_id: UUID,
        match_in: MatchUpdate,
    ) -> Match:
        return await self.update_record(
            Match, MatchFilters, {"public_id": public_id}, match_in
        )
