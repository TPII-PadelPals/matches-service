from uuid import UUID

from fastapi import Depends

from app.models.match import (
    Match,
    MatchCreate,
    MatchFilters,
    MatchUpdate,
)
from app.repository.match_repository import MatchRepository
from app.utilities.dependencies import SessionDep


class MatchService:
    async def create_match(self, session: SessionDep, match_in: MatchCreate) -> Match:
        repo = MatchRepository(session)
        return await repo.create_match(match_in)

    async def create_matches(
        self, session: SessionDep, matches_in: list[MatchCreate]
    ) -> list[Match]:
        repo = MatchRepository(session)
        return await repo.create_matches(matches_in)

    async def read_match(
        self,
        session: SessionDep,
        public_id: UUID,
    ) -> Match:
        repo = MatchRepository(session)
        return await repo.read_match(public_id)

    async def read_matches(
        self, session: SessionDep, prov_match_opt: MatchFilters = Depends()
    ) -> list[Match]:
        repo_match = MatchRepository(session)
        info_to_filter = [prov_match_opt]
        return await repo_match.read_matches(info_to_filter)

    async def update_match(
        self,
        session: SessionDep,
        public_id: UUID,
        match_in: MatchUpdate,
    ) -> Match:
        repo = MatchRepository(session)
        return await repo.update_match(public_id, match_in)
