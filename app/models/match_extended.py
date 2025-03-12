from app.models.match import MatchBase, MatchInmutable, Match
from app.models.match_player import MatchPlayerPublic, MatchPlayer
from sqlmodel import SQLModel


class MatchExtendedPublic(MatchBase, MatchInmutable):
    match_players: list[MatchPlayerPublic]

    @classmethod
    def from_private(
            cls, match: Match, match_players_private: list[MatchPlayer]
    ) -> "MatchExtendedPublic":
        data = match.model_dump()
        data["match_players"] = [
            MatchPlayerPublic.from_private(x) for x in match_players_private
        ]
        return cls(**data)


class MatchesExtendedListPublic(SQLModel):
    data: list[MatchExtendedPublic]
    count: int

    @classmethod
    def from_private(
            cls, all_info: list[tuple[Match, list[MatchPlayer]]]
    ) -> "MatchesExtendedListPublic":
        data = []
        for match, match_players in all_info:
            match_extend_public = MatchExtendedPublic.from_private(match, match_players)
            data.append(match_extend_public)
        data = data
        count = len(data)
        return cls(data=data, count=count)