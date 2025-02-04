from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.models.provisional_match import (
    ProvisionalMatch,
    ProvisionalMatchCreate,
    ProvisionalMatchFilters,
    ProvisionalMatchUpdate,
)
from app.repository.base_repository import BaseRepository
from app.utilities.exceptions import NotFoundException, NotUniqueException


class ProvisionalMatchRepository(BaseRepository):
    async def _commit_with_exception_handling(self) -> None:
        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            if "uq_match_constraints" in str(e.orig):
                raise NotUniqueException("provisional match")
            else:
                raise e

    async def create_provisional_match(
        self, provisional_match_in: ProvisionalMatchCreate
    ) -> ProvisionalMatch:
        provisional_match = ProvisionalMatch.model_validate(provisional_match_in)
        self.session.add(provisional_match)
        await self._commit_with_exception_handling()
        await self.session.refresh(provisional_match)
        return provisional_match

    async def create_provisional_matches(
        self, provisional_matches_in: list[ProvisionalMatchCreate]
    ) -> list[ProvisionalMatch]:
        provisional_matches = [
            ProvisionalMatch.model_validate(match) for match in provisional_matches_in
        ]
        self.session.add_all(provisional_matches)
        await self._commit_with_exception_handling()
        for match in provisional_matches:
            await self.session.refresh(match)
        return provisional_matches

    async def read_matches(
        self, filters: list[ProvisionalMatchFilters]
    ) -> list[ProvisionalMatch]:
        return await self.filter_records(ProvisionalMatch, filters)

    async def read_match(self, public_id: UUID) -> ProvisionalMatch:
        filters = [ProvisionalMatchFilters(public_id=public_id)]
        result = await self.read_matches(filters)
        match = result[0] if result else None
        if match is None:
            raise NotFoundException(str(match))
        return match

    async def update_match(
        self,
        public_id: UUID,
        match_in: ProvisionalMatchUpdate,
    ) -> ProvisionalMatch:
        match = await self.read_match(public_id)
        update_dict = match_in.model_dump(exclude_none=True)
        match.sqlmodel_update(update_dict)
        self.session.add(match)
        await self._commit_with_exception_handling()
        await self.session.refresh(match)
        return match
