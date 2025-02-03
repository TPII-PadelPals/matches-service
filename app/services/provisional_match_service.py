from fastapi import Depends

from app.models.match_player import MatchPlayer, MatchPlayerCreate
from app.models.provisional_match import (
    ProvisionalMatch,
    ProvisionalMatchCreate,
    ProvisionalMatchFilters,
    ProvisionalMatchPublic,
)
from app.repository.match_player_repository import MatchPlayerRepository
from app.repository.provisional_match_repository import ProvisionalMatchRepository
from app.utilities.dependencies import SessionDep


class ProvisionalMatchService:
    async def create_match(
        self, session: SessionDep, provisional_match_in: ProvisionalMatchCreate
    ) -> ProvisionalMatch:
        repo = ProvisionalMatchRepository(session)
        return await repo.create_provisional_match(provisional_match_in)

    async def create_matches(
        self, session: SessionDep, provisional_matches_in: list[ProvisionalMatchCreate]
    ) -> list[ProvisionalMatch]:
        repo = ProvisionalMatchRepository(session)
        return await repo.create_provisional_matches(provisional_matches_in)

    async def get_filter_match(
        self, session: SessionDep, prov_match_opt: ProvisionalMatchFilters = Depends()
    ) -> list[ProvisionalMatchPublic]:
        repo_provisional_match = ProvisionalMatchRepository(session)
        alternative_prov_match_opt = prov_match_opt.rotate_players_ids()
        info_to_filter = [prov_match_opt, alternative_prov_match_opt]
        return await repo_provisional_match.get_provisional_matches(info_to_filter)

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
