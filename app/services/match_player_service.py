from typing import Any
from uuid import UUID

from app.models.match_extended import MatchExtended
from app.models.match_player import (
    MatchPlayer,
    MatchPlayerCreate,
    MatchPlayerPay,
    MatchPlayerUpdate,
    ReserveStatus,
)
from app.repository.match_player_repository import MatchPlayerRepository
from app.services.match_service import MatchService
from app.services.payment_service import PaymentsService
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

    async def update_match_player(
        self,
        session: SessionDep,
        match_public_id: UUID,
        user_public_id: UUID,
        match_player_in: MatchPlayerUpdate,
    ) -> MatchPlayerPay:
        pay_url = None
        if match_player_in.is_inside():
            await self._validate_accept_match_player(
                session, match_public_id, user_public_id
            )
            match_player_extended = await self.get_match_player_extended(
                session, match_public_id, user_public_id
            )
            payment = await PaymentsService().create_payment(match_player_extended)
            pay_url = payment.pay_url

        match_player = await self._update_match_player(
            session, match_public_id, user_public_id, match_player_in
        )

        await self._update_match_similars(session, match_public_id)

        return MatchPlayerPay.from_match_player(match_player, pay_url)

    async def _update_match_player(
        self,
        session: SessionDep,
        match_public_id: UUID,
        user_public_id: UUID,
        match_player_in: MatchPlayerUpdate,
    ) -> MatchPlayer:
        repo_match_player = MatchPlayerRepository(session)
        match_player = await repo_match_player.update_match_player(
            match_player_in,
            match_public_id=match_public_id,
            user_public_id=user_public_id,
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
        assigned_players = await self.get_match_players(
            session, match_public_id=match_public_id, reserve=ReserveStatus.ASSIGNED
        )
        inside_players = await self.get_match_players(
            session, match_public_id=match_public_id, reserve=ReserveStatus.INSIDE
        )

        n_missing_players = (
            self.MAX_MATCH_PLAYERS - len(assigned_players) - len(inside_players)
        )

        next_assign_players = []
        if n_missing_players > 0:
            next_assign_players = await self.get_match_players(
                session,
                order_by=[("distance", True)],
                limit=n_missing_players,
                match_public_id=match_public_id,
                reserve=ReserveStatus.SIMILAR,
            )

        for player in next_assign_players:
            await self._update_match_player(
                session,
                match_public_id,
                player.user_public_id,
                MatchPlayerUpdate(reserve=ReserveStatus.ASSIGNED),
            )
