from datetime import datetime
from typing import ClassVar

from app.models.match import MatchCreate
from app.models.match_extended import MatchExtended
from app.models.match_player import MatchPlayerCreate, ReserveStatus
from app.models.player import Player, PlayerFilters
from app.services.business_service import BusinessService
from app.services.match_extended_service import MatchExtendedService
from app.services.match_player_service import MatchPlayerService
from app.services.match_service import MatchService
from app.services.players_service import PlayersService
from app.utilities.dependencies import SessionDep


class MatchGeneratorService:
    MIN_SIM_PLAYERS: ClassVar[int] = 3
    FACTOR_SIM_PLAYERS: ClassVar[int] = 4
    N_SIM_PLAYERS: ClassVar[int] = MIN_SIM_PLAYERS * FACTOR_SIM_PLAYERS

    def _choose_priority_player(self, players: list[Player]) -> Player:
        # TODO: Choose priority player base on last played match w.r.t. today.
        return players[0]

    async def generate_matches(
        self,
        session: SessionDep,
        business_public_id: int,
        court_public_id: str,
        date: datetime,
    ) -> list[MatchExtended]:
        matches_extended = []

        avail_times = await BusinessService().get_available_times(
            business_public_id, court_public_id, date
        )
        for avail_time in avail_times:
            match_create = MatchCreate.from_available_time(avail_time)
            match = await MatchService().create_match(session, match_create)
            match_public_id = match.public_id

            players_filters = PlayerFilters.from_available_time(avail_time)
            avail_players = await PlayersService().get_players_by_filters(
                players_filters
            )

            assigned_player = self._choose_priority_player(avail_players)

            players_filters.user_public_id = assigned_player.user_public_id
            players_filters.n_players = self.N_SIM_PLAYERS
            similar_players = await PlayersService().get_players_by_filters(
                players_filters
            )

            # match_players = []

            for player in [assigned_player] + similar_players:
                reserve_status = ReserveStatus.Similar
                if player.user_public_id == assigned_player.user_public_id:
                    reserve_status = ReserveStatus.Assigned

                match_player_create = MatchPlayerCreate(
                    user_public_id=player.user_public_id,
                    match_public_id=match_public_id,
                    reserve=reserve_status,
                )
                await MatchPlayerService().create_match_player(
                    session, match_player_create
                )

                # match_players.append(match_player)

            match_extended = await MatchExtendedService().get_match(
                session, match_public_id
            )  # type: ignore
            matches_extended.append(match_extended)

        return matches_extended
