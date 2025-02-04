from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.models.match import (
    Match,
    MatchCreate,
    MatchFilters,
    MatchUpdate,
)
from app.repository.base_repository import BaseRepository
from app.utilities.exceptions import NotFoundException, NotUniqueException


class MatchRepository(BaseRepository):
    async def _commit_with_exception_handling(self) -> None:
        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            if "uq_match_constraints" in str(e.orig):
                raise NotUniqueException("match")
            else:
                raise e

    async def create_match(self, match_in: MatchCreate) -> Match:
        match = Match.model_validate(match_in)
        self.session.add(match)
        await self._commit_with_exception_handling()
        await self.session.refresh(match)
        return match

    async def create_matches(self, matches_in: list[MatchCreate]) -> list[Match]:
        matches = [Match.model_validate(match) for match in matches_in]
        self.session.add_all(matches)
        await self._commit_with_exception_handling()
        for match in matches:
            await self.session.refresh(match)
        return matches

    async def read_matches(self, filters: list[MatchFilters]) -> list[Match]:
        return await self.filter_records(Match, filters)

    async def read_match(self, public_id: UUID) -> Match:
        filters = [MatchFilters(public_id=public_id)]
        result = await self.read_matches(filters)
        match = result[0] if result else None
        if match is None:
            raise NotFoundException(str(match))
        return match

    async def update_match(
        self,
        public_id: UUID,
        match_in: MatchUpdate,
    ) -> Match:
        match = await self.read_match(public_id)
        update_dict = match_in.model_dump(exclude_none=True)
        match.sqlmodel_update(update_dict)
        self.session.add(match)
        await self._commit_with_exception_handling()
        await self.session.refresh(match)
        return match
