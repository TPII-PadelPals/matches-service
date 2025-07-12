from typing import Any
from uuid import UUID

from app.models.match_extended import MatchExtended
from app.models.match_player import (
    MatchPlayer,
    MatchPlayerCreate,
)
from app.repository.match_player_repository import MatchPlayerRepository
from app.services.match_service import MatchService
from app.utilities.dependencies import SessionDep


class MatchPlayerService:
    async def create_match_player(
        self,
        session: SessionDep,
        match_player_in: MatchPlayerCreate,
        should_commit: bool = True,
    ) -> MatchPlayer:
        repo_match_player = MatchPlayerRepository(session)
        return await repo_match_player.create_match_player(
            match_player_in, should_commit
        )

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
        return await repo_match_player.get_match_player(
            match_public_id=match_public_id, user_public_id=user_public_id
        )

    async def get_match_player_extended(
        self, session: SessionDep, match_public_id: UUID, user_public_id: UUID
    ) -> MatchExtended:
        match = await MatchService().get_match(session, match_public_id)
        match_player = await self.get_match_players(
            session, match_public_id=match_public_id, user_public_id=user_public_id
        )
        return MatchExtended(match, match_player)

    async def get_match_players(
        self,
        session: SessionDep,
        order_by: list[tuple[str, bool]] | None = None,
        limit: int | None = None,
        **filters: Any,
    ) -> list[MatchPlayer]:
        """
        order_by: List of tuples(Player.attribute, is_ascending)
        to order the result.
        limit: Max number of players to get.
        """
        repo_match_player = MatchPlayerRepository(session)
        return await repo_match_player.get_matches_players(order_by, limit, **filters)

    async def get_player_matches(
        self,
        session: SessionDep,
        user_public_id: UUID,
    ) -> list[MatchPlayer]:
        repo_match_player = MatchPlayerRepository(session)
        return await repo_match_player.get_matches_players(
            user_public_id=user_public_id
        )

    async def delete_match_players(
        self, session: SessionDep, should_commit: bool = True, **filters: Any
    ) -> None:
        repo_match_player = MatchPlayerRepository(session)
        await repo_match_player.delete_match_players(should_commit, **filters)
