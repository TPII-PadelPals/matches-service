from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.provisional_match import (
    ProvisionalMatch,
    ProvisionalMatchCreate,
    ProvisionalMatchFilters,
    ProvisionalMatchPublic,
)
from app.utilities.exceptions import NotUniqueException


class ProvisionalMatchRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

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

    async def get_provisional_matches(
        self, prov_match_filter: list[ProvisionalMatchFilters]
    ) -> list[ProvisionalMatchPublic]:
        conditions = []

        # Player filter conditions
        for match in prov_match_filter:
            match_conditions = []
            # Iterate through attributes and their values
            for attr, value in vars(match).items():
                if value is not None:
                    match_conditions.append(getattr(ProvisionalMatch, attr) == value)
            conditions.append(and_(*match_conditions))

        # Combine conditions with AND
        query = select(*ProvisionalMatch.__table__.columns).where(or_(*conditions))

        # Execute query
        # type: ignore
        matches = (await self.session.exec(query)).mappings().all()
        public_matches = [ProvisionalMatchPublic(**match) for match in matches]
        return public_matches
