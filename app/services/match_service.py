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
    async def create_match(
        self, session: SessionDep, match_in: MatchCreate, should_commit: bool = True
    ) -> Match:
        repo_match = MatchRepository(session)
        return await repo_match.create_match(match_in, should_commit)

    async def create_matches(
        self, session: SessionDep, matches_in: list[MatchCreate]
    ) -> list[Match]:
        repo_match = MatchRepository(session)
        return await repo_match.create_matches(matches_in)

    async def get_match(
        self,
        session: SessionDep,
        public_id: UUID,
    ) -> Match:
        repo_match = MatchRepository(session)
        return await repo_match.get_match(public_id=public_id)

    async def get_matches(
        self, session: SessionDep, prov_match_opt: MatchFilters = Depends()
    ) -> list[Match]:
        repo_match = MatchRepository(session)
        filters = prov_match_opt.model_dump(exclude_unset=True, exclude_none=True)
        return await repo_match.get_matches(**filters)

    async def update_match(
        self,
        session: SessionDep,
        public_id: UUID,
        match_in: MatchUpdate,
    ) -> Match:
        repo_match = MatchRepository(session)
        return await repo_match.update_match(match_in, public_id=public_id)

    async def is_match_create_valid(
        self, session: SessionDep, match_in: MatchCreate
    ) -> bool:
        filters = match_in.model_dump()
        filters["status"] = None
        match_filter = MatchFilters(**filters)
        list = await self.get_matches(session, match_filter)
        return len(list) == 0
