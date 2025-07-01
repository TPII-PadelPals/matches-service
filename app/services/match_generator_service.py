from typing import ClassVar
from uuid import UUID

from app.models.available_time import AvailableTime
from app.models.match import MatchCreate
from app.models.match_extended import MatchExtended
from app.models.match_generation import (
    MatchGenerationCreate,
    MatchGenerationCreateExtended,
)
from app.models.match_player import MatchPlayer, MatchPlayerCreate, ReserveStatus
from app.models.player import Player, PlayerFilters
from app.services.business_service import BusinessService
from app.services.match_extended_service import MatchExtendedService
from app.services.match_player_service import MatchPlayerService
from app.services.match_service import MatchService
from app.services.players_service import PlayersService
from app.utilities.commit import commit_refresh_or_flush
from app.utilities.dependencies import SessionDep
from app.utilities.exceptions import NotUniqueException


class MatchGeneratorService:
    MIN_SIM_PLAYERS: ClassVar[int] = 1
    FACTOR_SIM_PLAYERS: ClassVar[int] = 4
    N_SIM_PLAYERS: ClassVar[int] = MIN_SIM_PLAYERS * FACTOR_SIM_PLAYERS

    async def get_matches(
        self, session: SessionDep, matches_public_ids: list[UUID]
    ) -> list[MatchExtended]:
        matches_extended = [
            await MatchExtendedService().get_match(session, match_public_id)
            for match_public_id in matches_public_ids
        ]

        return matches_extended

    def _choose_priority_player(self, players: list[Player]) -> Player:
        # TODO: Choose priority player base on last played match w.r.t. today.
        return players[0]

    async def _choose_match_players(
        self, avail_time: AvailableTime, exclude_uuids: list[UUID] | None = None
    ) -> tuple[Player | None, list[Player]]:
        if exclude_uuids is None:
            exclude_uuids = []

        players_filters = PlayerFilters.from_available_time(avail_time)
        avail_players = await PlayersService().get_players_by_filters(
            players_filters, exclude_uuids
        )

        if not len(avail_players) > 0:
            return None, []

        assigned_player = self._choose_priority_player(avail_players)

        players_filters.user_public_id = assigned_player.user_public_id
        players_filters.n_players = self.N_SIM_PLAYERS + len(exclude_uuids)
        similar_players = await PlayersService().get_players_by_filters(
            players_filters, exclude_uuids
        )
        return assigned_player, similar_players

    async def generate_match_players(
        self,
        session: SessionDep,
        match_public_id: UUID,
        avail_time: AvailableTime,
        should_commit: bool = True,
    ) -> list[MatchPlayer]:
        match_player_service = MatchPlayerService()

        old_similar_players = await match_player_service.get_match_players(
            session, match_public_id=match_public_id, reserve=ReserveStatus.SIMILAR
        )
        old_similar_uuids = [player.user_public_id for player in old_similar_players]
        await match_player_service.delete_match_players(
            session,
            should_commit=True,
            match_public_id=[match_public_id],
            user_public_id=old_similar_uuids,
        )

        outside_players = await match_player_service.get_match_players(
            session, match_public_id=match_public_id, reserve=ReserveStatus.OUTSIDE
        )
        outside_uuids = [player.user_public_id for player in outside_players]

        assigned_player, similar_players = await self._choose_match_players(
            avail_time, exclude_uuids=outside_uuids
        )
        if not assigned_player or len(similar_players) == 0:
            return []

        avail_players = [assigned_player] + similar_players
        match_players = []
        for distance, player in enumerate(avail_players):
            reserve_status = ReserveStatus.SIMILAR
            if player.user_public_id == assigned_player.user_public_id:
                reserve_status = ReserveStatus.ASSIGNED

            match_player_create = MatchPlayerCreate(
                user_public_id=player.user_public_id,
                match_public_id=match_public_id,
                distance=distance,
                reserve=reserve_status,
            )

            match_player = await MatchPlayerService().create_match_player(
                session, match_player_create, should_commit=False
            )
            match_players.append(match_player)

        await commit_refresh_or_flush(session, should_commit)

        return match_players

    async def generate_match(
        self, session: SessionDep, avail_time: AvailableTime, should_commit: bool = True
    ) -> MatchExtended:
        match_create = MatchCreate.from_available_time(avail_time)

        match = await MatchService().create_match(
            session, match_create, should_commit=False
        )

        match_players = await self.generate_match_players(
            session, match.public_id, avail_time, should_commit=False
        )

        await commit_refresh_or_flush(
            session, should_commit, records=[match] + match_players
        )

        return MatchExtended(match, match_players)

    async def generate_matches(
        self, session: SessionDep, match_gen_create: MatchGenerationCreateExtended
    ) -> list[UUID]:
        matches_public_ids = []

        avail_times = await BusinessService().get_available_times(
            **match_gen_create.model_dump()
        )
        for avail_time in avail_times:
            try:
                match_extended = await self.generate_match(
                    session, avail_time, should_commit=True
                )
            except NotUniqueException:
                continue
            matches_public_ids.append(match_extended.match.public_id)

        return matches_public_ids

    async def generate_matches_all(
        self, session: SessionDep, match_gen_create: MatchGenerationCreate
    ) -> list[UUID]:
        matches_public_ids = []

        courts = await BusinessService().get_courts(match_gen_create.business_public_id)

        for court in courts:
            match_gen_create_ext = MatchGenerationCreateExtended(
                court_name=court.court_name, **match_gen_create.model_dump()
            )
            _matches_public_ids = await self.generate_matches(
                session, match_gen_create_ext
            )
            matches_public_ids += _matches_public_ids

        return matches_public_ids
