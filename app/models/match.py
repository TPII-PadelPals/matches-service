import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class StatusEnum(str, Enum):
    provisional = "P"
    reserved = "R"
    cancelled = "C"


class MatchBase(SQLModel):
    court_id: int | None = Field(default=None)
    time: int | None = Field(default=None)
    date: datetime.date | None = Field(default=None)
    status: str | None = Field(default=None)


class MatchInmutable(SQLModel):
    public_id: UUID | None = Field(default_factory=uuid4, unique=True)


class MatchCreate(MatchBase):
    status: str | None = Field(default=StatusEnum.provisional)


class MatchUpdate(MatchBase):
    pass


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
    def name(self) -> str:
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
