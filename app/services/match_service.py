from uuid import UUID

from fastapi import Depends

from app.models.match import (
    Match,
    MatchCreate,
    MatchFilters,
    MatchUpdate,
)
from app.models.match_player import (
    MatchPlayer,
    MatchPlayerCreate,
    MatchPlayerFilter,
    MatchPlayerUpdate,
)
from app.repository.match_player_repository import MatchPlayerRepository
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

    async def get_filter_match(
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
        return await repo.read_matches_players(
            [MatchPlayerFilter(match_public_id=match_public_id)]
        )

    async def read_player_matches(
        self,
        session: SessionDep,
        user_public_id: UUID,
    ) -> list[MatchPlayer]:
        repo = MatchPlayerRepository(session)
        return await repo.read_matches_players(
            [MatchPlayerFilter(user_public_id=user_public_id)]
        )

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
