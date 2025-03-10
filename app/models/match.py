import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel

from app.models.match_player import MatchPlayer, MatchPlayerPublic


class MatchStatus(str, Enum):
    provisional = "Provisional"
    reserved = "Reserved"
    cancelled = "Cancelled"


class MatchBase(SQLModel):
    court_id: int | None = Field(default=None)
    time: int | None = Field(default=None)
    date: datetime.date | None = Field(default=None)
    status: str | None = Field(default=MatchStatus.provisional)


class MatchInmutable(SQLModel):
    public_id: UUID | None = Field(default_factory=uuid4, unique=True)


class MatchCreate(MatchBase):
    pass


class MatchUpdate(MatchBase):
    status: str | None = Field(default=None)


class Match(MatchBase, MatchInmutable, table=True):
    id: int = Field(default=None, primary_key=True)

    __tablename__ = "matches"
    __table_args__ = (
        UniqueConstraint(
            "court_id",
            "time",
            "date",
            name="uq_match_constraints",
        ),
    )

    @classmethod
    def name(cls) -> str:
        return "Match"


class MatchPublic(MatchBase, MatchInmutable):
    @classmethod
    def from_private(cls, match: Match) -> "MatchPublic":
        data = match.model_dump()
        return cls(**data)


class MatchListPublic(SQLModel):
    data: list[MatchPublic]
    count: int

    @classmethod
    def from_private(cls, match_list: list[Match]) -> "MatchListPublic":
        data = []
        for match in match_list:
            data.append(MatchPublic.from_private(match))
        count = len(match_list)
        return cls(data=data, count=count)


class MatchFilters(MatchBase, MatchInmutable):
    id: int | None = None
    public_id: UUID | None = None
    court_id: int | None = None
    time: int | None = None
    date: datetime.date | None = None
    status: str | None = None


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
