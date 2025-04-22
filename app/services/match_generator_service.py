from typing import ClassVar
from uuid import UUID

from app.models.available_time import AvailableTime
from app.models.match import MatchCreate
from app.models.match_extended import MatchExtended
from app.models.match_generation import MatchGenerationCreate
from app.models.match_player import MatchPlayer, MatchPlayerCreate, ReserveStatus
from app.models.player import Player, PlayerFilters
from app.services.business_service import BusinessService
from app.services.match_extended_service import MatchExtendedService
from app.services.match_player_service import MatchPlayerService
from app.services.match_service import MatchService
from app.services.players_service import PlayersService
from app.utilities.dependencies import SessionDep
from app.utilities.exceptions import NotUniqueException


class MatchGeneratorService:
    MIN_SIM_PLAYERS: ClassVar[int] = 3
    FACTOR_SIM_PLAYERS: ClassVar[int] = 4
    N_SIM_PLAYERS: ClassVar[int] = MIN_SIM_PLAYERS * FACTOR_SIM_PLAYERS

    def _choose_priority_player(self, players: list[Player]) -> Player:
        # TODO: Choose priority player base on last played match w.r.t. today.
        return players[0]

    async def _choose_match_players(
        self, avail_time: AvailableTime
    ) -> tuple[Player | None, list[Player]]:
        players_filters = PlayerFilters.from_available_time(avail_time)
        avail_players = await PlayersService().get_players_by_filters(players_filters)

        if not len(avail_players) > 0:
            return None, []

        assigned_player = self._choose_priority_player(avail_players)

        # Por qué se asigna un user_public_id aca?
        # Porque al filtro si le ponés el user_public_id te trae todos menos el del filtro.
        players_filters.user_public_id = assigned_player.user_public_id
        players_filters.n_players = self.N_SIM_PLAYERS
        similar_players = await PlayersService().get_players_by_filters(players_filters)
        return assigned_player, similar_players

    async def _generate_match_players(
        self,
        session: SessionDep,
        match_public_id: UUID,
        assigned_player: Player,
        similar_players: list[Player],
    ) -> list[MatchPlayer]:
        match_players = []
        for player in [assigned_player] + similar_players:
            reserve_status = ReserveStatus.SIMILAR
            if player.user_public_id == assigned_player.user_public_id:
                reserve_status = ReserveStatus.ASSIGNED

            match_player_create = MatchPlayerCreate(
                user_public_id=player.user_public_id,
                match_public_id=match_public_id,
                reserve=reserve_status,
            )
            match_player = await MatchPlayerService().create_match_player(
                session, match_player_create, should_commit=False
            )
            match_players.append(match_player)
        return match_players

    async def _generate_match(
        self, session: SessionDep, avail_time: AvailableTime
    ) -> MatchExtended | None:
        match_create = MatchCreate.from_available_time(avail_time)
        match_service = MatchService()

        assigned_player, similar_players = await self._choose_match_players(avail_time)
        if not assigned_player or len(similar_players) == 0:
            return None

        match = await match_service.create_match(
            session, match_create, should_commit=False
        )
        match_public_id = match.public_id

        match_players = await self._generate_match_players(
            session,
            match_public_id,
            assigned_player,
            similar_players,
        )

        return MatchExtended(match, match_players)

    async def generate_matches(
        self, session: SessionDep, match_gen_create: MatchGenerationCreate
    ) -> list[MatchExtended]:
        matches_public_ids = []

        avail_times = await BusinessService().get_available_times(
            **match_gen_create.model_dump()
        )
        for avail_time in avail_times:
            try:
                match_extended = await self._generate_match(session, avail_time)
                if not match_extended:
                    continue
                await session.commit()
            except NotUniqueException:
                await session.rollback()
                continue
            matches_public_ids.append(match_extended.match.public_id)

        matches_extended = [
            await MatchExtendedService().get_match(session, match_public_id)
            for match_public_id in matches_public_ids
        ]

        return matches_extended
