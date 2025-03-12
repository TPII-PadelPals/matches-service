from typing import Any

from app.models.match import MatchBase, MatchInmutable, Match
from app.models.match_player import MatchPlayerPublic, MatchPlayer
from sqlmodel import SQLModel



class MatchExtendedPublic(MatchBase, MatchInmutable):
    match_players: list[MatchPlayerPublic]


class MatchExtended:
    def __init__(self, match: Match, match_players_list: list[MatchPlayer]):
        self.match = match
        self.match_players = match_players_list

    def generate_match_extend_public(self) -> MatchExtendedPublic:
        data = self.match.model_dump()
        data["match_players"] = [
            MatchPlayerPublic.from_private(x) for x in self.match_players
        ]
        return MatchExtendedPublic(**data)


class MatchesExtendedListPublic(SQLModel):
    data: list[MatchExtendedPublic]
    count: int

    @classmethod
    def from_private(
            cls, all_info: list[MatchExtended]
    ) -> "MatchesExtendedListPublic":
        data = []
        for match_extend in all_info:
            match_extend_public = match_extend.generate_match_extend_public()
            data.append(match_extend_public)
        data = data
        count = len(data)
        return cls(data=data, count=count)