from uuid import UUID

from app.models.match_player import (
    MatchPlayer,
    MatchPlayerCreate,
    MatchPlayerFilter,
    MatchPlayerUpdate,
)
from app.repository.match_player_repository import MatchPlayerRepository
from app.utilities.dependencies import SessionDep


class MatchPlayerService:
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

    async def get_match_player(
        self,
        session: SessionDep,
        match_public_id: UUID,
        user_public_id: UUID,
    ) -> MatchPlayer:
        repo = MatchPlayerRepository(session)
        return await repo.get_match_player(match_public_id, user_public_id)

    async def get_match_players(
        self,
        session: SessionDep,
        match_public_id: UUID,
    ) -> list[MatchPlayer]:
        repo = MatchPlayerRepository(session)
        return await repo.get_matches_players(
            [MatchPlayerFilter(match_public_id=match_public_id)]
        )

    async def get_player_matches(
        self,
        session: SessionDep,
        user_public_id: UUID,
    ) -> list[MatchPlayer]:
        repo = MatchPlayerRepository(session)
        return await repo.get_matches_players(
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
