import uuid

from sqlmodel import SQLModel

from app.models.match import Match, MatchBase, MatchInmutable
from app.models.match_player import MatchPlayer, MatchPlayerPublic


class MatchExtendedPublic(MatchBase, MatchInmutable):
    match_players: list[MatchPlayerPublic]

    def get_list_player_assigned(self) -> list[uuid.UUID]:
        result = []
        for match_player in self.match_players:
            list_public_id_player_assigned_in_match = (
                match_player.get_user_public_id_of_player_assigned()
            )
            if not list_public_id_player_assigned_in_match:
                continue
            result.append(list_public_id_player_assigned_in_match)
        return result


class MatchExtended:
    def __init__(self, match: Match, match_players_list: list[MatchPlayer]):
        self.match = match
        self.match_players = match_players_list

    def to_public(self) -> MatchExtendedPublic:
        data = self.match.model_dump()
        data["match_players"] = [
            MatchPlayerPublic.from_private(x) for x in self.match_players
        ]
        return MatchExtendedPublic(**data)


class MatchesExtendedListPublic(SQLModel):
    data: list[MatchExtendedPublic]
    count: int

    @classmethod
    def from_private(cls, all_info: list[MatchExtended]) -> "MatchesExtendedListPublic":
        data = []
        for match_extend in all_info:
            match_extend_public = match_extend.to_public()
            data.append(match_extend_public)
        data = data
        count = len(data)
        return cls(data=data, count=count)

    def get_list_player_assigned(self) -> list[uuid.UUID]:
        result = []
        for match_extended in self.data:
            list_player_assigned_in_match = match_extended.get_list_player_assigned()
            result += list_player_assigned_in_match
        return result
