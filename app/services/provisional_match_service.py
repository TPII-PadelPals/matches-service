from app.models.provisional_match import ProvisionalMatch, ProvisionalMatchCreate
from app.repository.provisional_match_repository import ProvisionalMatchRepository
from app.utilities.dependencies import SessionDep


class ProvisionalMatchService:
    async def create_match(
            self, session: SessionDep, provisional_match_in: ProvisionalMatchCreate
    ) -> ProvisionalMatch:
        repo = ProvisionalMatchRepository(session)
        new_match = await repo.create_provisional_match(provisional_match_in)
        return new_match