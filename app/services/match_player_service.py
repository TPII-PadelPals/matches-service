from uuid import UUID

from app.models.match_player import (
    MatchPlayer,
    MatchPlayerCreate,
    MatchPlayerFilter,
    MatchPlayerUpdate,
)
from app.repository.match_player_repository import MatchPlayerRepository
from app.utilities.dependencies import SessionDep
from app.utilities.exceptions import NotAuthorizedException


class MatchPlayerService:
    async def create_match_player(
        self, session: SessionDep, match_player_in: MatchPlayerCreate
    ) -> MatchPlayer:
        repo_match_player = MatchPlayerRepository(session)
        return await repo_match_player.create_match_player(match_player_in)

    async def create_match_players(
        self, session: SessionDep, match_players_in: list[MatchPlayerCreate]
    ) -> list[MatchPlayer]:
        repo_match_player = MatchPlayerRepository(session)
        return await repo_match_player.create_match_players(match_players_in)

    async def get_match_player(
        self,
        session: SessionDep,
        match_public_id: UUID,
        user_public_id: UUID,
    ) -> MatchPlayer:
        repo_match_player = MatchPlayerRepository(session)
        return await repo_match_player.get_match_player(match_public_id, user_public_id)

    async def get_match_players(
        self,
        session: SessionDep,
        match_public_id: UUID,
    ) -> list[MatchPlayer]:
        repo_match_player = MatchPlayerRepository(session)
        return await repo_match_player.get_matches_players(
            [MatchPlayerFilter(match_public_id=match_public_id)]
        )

    async def get_player_matches(
        self,
        session: SessionDep,
        user_public_id: UUID,
    ) -> list[MatchPlayer]:
        repo_match_player = MatchPlayerRepository(session)
        return await repo_match_player.get_matches_players(
            [MatchPlayerFilter(user_public_id=user_public_id)]
        )

    async def update_match_player(
        self,
        session: SessionDep,
        match_public_id: UUID,
        user_public_id: UUID,
        match_player_in: MatchPlayerUpdate,
    ) -> MatchPlayer:
        if match_player_in.is_inside():
            await self._validate_accept_match_player(
                session, match_public_id, user_public_id
            )
        repo_match_player = MatchPlayerRepository(session)
        return await repo_match_player.update_match_player(
            match_public_id, user_public_id, match_player_in
        )

    async def _validate_accept_match_player(
        self,
        session: SessionDep,
        match_public_id: UUID,
        user_public_id: UUID,
    ) -> None:
        match_player = await self.get_match_player(
            session, match_public_id, user_public_id
        )
        if not match_player.is_assigned():
            raise NotAuthorizedException()
