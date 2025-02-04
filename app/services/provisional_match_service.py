from uuid import UUID

from fastapi import Depends

from app.models.match_player import MatchPlayer, MatchPlayerCreate, MatchPlayerUpdate
from app.models.provisional_match import (
    ProvisionalMatch,
    ProvisionalMatchCreate,
    ProvisionalMatchFilters,
)

# ProvisionalMatchPublic,
from app.repository.match_player_repository import MatchPlayerRepository
from app.repository.provisional_match_repository import ProvisionalMatchRepository
from app.utilities.dependencies import SessionDep


class ProvisionalMatchService:
    async def create_match(
        self, session: SessionDep, provisional_match_in: ProvisionalMatchCreate
    ) -> ProvisionalMatch:
        repo = ProvisionalMatchRepository(session)
        return await repo.create_provisional_match(provisional_match_in)

    async def create_matches(
        self, session: SessionDep, provisional_matches_in: list[ProvisionalMatchCreate]
    ) -> list[ProvisionalMatch]:
        repo = ProvisionalMatchRepository(session)
        return await repo.create_provisional_matches(provisional_matches_in)

    async def get_filter_match(
        self, session: SessionDep, prov_match_opt: ProvisionalMatchFilters = Depends()
    ) -> list[ProvisionalMatch]:
        repo_provisional_match = ProvisionalMatchRepository(session)
        info_to_filter = [prov_match_opt]
        return await repo_provisional_match.get_provisional_matches(info_to_filter)

    async def create_match_player(
        self, session: SessionDep, match_player_in: MatchPlayerCreate
    ) -> MatchPlayer:
        repo = MatchPlayerRepository(session)
        return await repo.create_match_player(match_player_in)

    async def create_match_players(
        self, session: SessionDep, match_players_in: list[MatchPlayerCreate]
    ) -> list[MatchPlayer]:
        repo = MatchPlayerRepository(session)
        return await repo.create_match_players(match_players_in)

    async def read_match_player(
        self,
        session: SessionDep,
        match_public_id: UUID,
        user_public_id: UUID,
    ) -> MatchPlayer:
        repo = MatchPlayerRepository(session)
        return await repo.read_match_player(match_public_id, user_public_id)

    async def read_match_players(
        self,
        session: SessionDep,
        match_public_id: UUID,
    ) -> list[MatchPlayer]:
        repo = MatchPlayerRepository(session)
        return await repo.read_match_players(match_public_id)

    async def read_player_matches(
        self,
        session: SessionDep,
        user_public_id: UUID,
    ) -> list[MatchPlayer]:
        repo = MatchPlayerRepository(session)
        return await repo.read_player_matches(user_public_id)

    async def update_match_player(
        self,
        session: SessionDep,
        match_public_id: UUID,
        user_public_id: UUID,
        match_player_in: MatchPlayerUpdate,
    ) -> MatchPlayer:
        repo = MatchPlayerRepository(session)
        return await repo.update_match_player(
            match_public_id, user_public_id, match_player_in
        )
