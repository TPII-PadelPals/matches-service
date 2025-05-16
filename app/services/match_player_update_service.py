from uuid import UUID

from app.models.match_player import (
    MatchPlayer,
    MatchPlayerPay,
    MatchPlayerUpdate,
    ReserveStatus,
)
from app.repository.match_player_repository import MatchPlayerRepository
from app.services.business_service import BusinessService
from app.services.match_generator_service import MatchGeneratorService
from app.services.match_player_service import MatchPlayerService
from app.services.match_service import MatchService
from app.services.payment_service import PaymentsService
from app.utilities.dependencies import SessionDep
from app.utilities.exceptions import NotAuthorizedException


class MatchPlayerUpdateService:
    MAX_MATCH_PLAYERS = 4

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
            # Move to another function
            match_player_extended = (
                await MatchPlayerService().get_match_player_extended(
                    session, match_public_id, user_public_id
                )
            )
            payment = await PaymentsService().create_payment(match_player_extended)
            pay_url = payment.pay_url

        match_player = await self._update_match_player(
            session, match_public_id, user_public_id, match_player_in
        )

        await self._update_match_player_first(session, match_public_id)

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
        match_player = await MatchPlayerService().get_match_player(
            session, match_public_id, user_public_id
        )
        if not match_player.is_assigned():
            raise NotAuthorizedException()

    async def _update_match_player_first(
        self, session: SessionDep, match_public_id: UUID
    ) -> None:
        inside_players = await MatchPlayerService().get_match_players(
            session, match_public_id=match_public_id, reserve=ReserveStatus.INSIDE
        )

        if inside_players:
            return

        match = await MatchService().get_match(session, match_public_id)
        avail_time = await BusinessService().get_available_time(
            match.business_public_id,  # type: ignore
            match.court_name,  # type: ignore
            match.date,  # type: ignore
            match.time,  # type: ignore
        )
        if avail_time:
            await MatchGeneratorService()._generate_match_players(
                session, match_public_id, avail_time, should_commit=True
            )

    async def _update_match_similars(
        self, session: SessionDep, match_public_id: UUID
    ) -> None:
        inside_players = await MatchPlayerService().get_match_players(
            session, match_public_id=match_public_id, reserve=ReserveStatus.INSIDE
        )
        n_inside = len(inside_players)

        if n_inside <= 0:
            return

        assigned_players = await MatchPlayerService().get_match_players(
            session, match_public_id=match_public_id, reserve=ReserveStatus.ASSIGNED
        )
        n_assigned = len(assigned_players)

        n_missing_players = self.MAX_MATCH_PLAYERS - n_assigned - n_inside

        next_assign_players = []
        if n_missing_players > 0:
            next_assign_players = await MatchPlayerService().get_match_players(
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
