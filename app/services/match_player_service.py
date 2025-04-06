from uuid import UUID

from app.models.match_player import (
    MatchPlayer,
    MatchPlayerCreate,
    MatchPlayerFilter,
    MatchPlayerUpdate,
    ReserveStatus,
)
from app.repository.match_player_repository import MatchPlayerRepository
from app.utilities.dependencies import SessionDep
from app.utilities.exceptions import NotAuthorizedException


class MatchPlayerService:
    MAX_MATCH_PLAYERS = 4

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
        return await repo_match_player.get_match_player(match_public_id, user_public_id)

    async def get_match_players(
        self,
        session: SessionDep,
        match_public_id: UUID,
        status: ReserveStatus | None = None,
    ) -> list[MatchPlayer]:
        repo_match_player = MatchPlayerRepository(session)
        match_player_filter = MatchPlayerFilter(match_public_id=match_public_id)
        if status:
            match_player_filter.reserve = status
        return await repo_match_player.get_matches_players([match_player_filter])

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

        match_player = await self._update_match_player(
            session, match_public_id, user_public_id, match_player_in
        )

        await self._update_match_similars(session, match_public_id)

        return match_player

    async def _update_match_player(
        self,
        session: SessionDep,
        match_public_id: UUID,
        user_public_id: UUID,
        match_player_in: MatchPlayerUpdate,
    ) -> MatchPlayer:
        repo_match_player = MatchPlayerRepository(session)
        match_player = await repo_match_player.update_match_player(
            match_public_id, user_public_id, match_player_in
        )
        return match_player

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

    async def _update_match_similars(
        self, session: SessionDep, match_public_id: UUID
    ) -> None:
        assigned_players = await MatchPlayerService().get_match_players(
            session, match_public_id, status=ReserveStatus.ASSIGNED
        )
        inside_players = await MatchPlayerService().get_match_players(
            session, match_public_id, status=ReserveStatus.INSIDE
        )

        n_missing_players = (
            self.MAX_MATCH_PLAYERS - len(assigned_players) - len(inside_players)
        )

        similar_players = await MatchPlayerService().get_match_players(
            session, match_public_id, status=ReserveStatus.SIMILAR
        )

        next_assign_players = similar_players[:n_missing_players]

        for player in next_assign_players:
            await MatchPlayerService()._update_match_player(
                session,
                match_public_id,
                player.user_public_id,
                MatchPlayerUpdate(reserve=ReserveStatus.ASSIGNED),
            )
