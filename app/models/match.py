import datetime
import uuid
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel

from app.models.available_time import AvailableTime


class MatchStatus(str, Enum):
    provisional = "Provisional"
    reserved = "Reserved"
    cancelled = "Cancelled"


class MatchBase(SQLModel):
    court_name: str | None = Field(default=None)
    court_public_id: uuid.UUID | None = Field(default=None)
    time: int | None = Field(default=None)
    date: datetime.date | None = Field(default=None)
    status: str | None = Field(default=MatchStatus.provisional)


class MatchInmutable(SQLModel):
    public_id: UUID = Field(default_factory=uuid4, unique=True)


class MatchCreate(MatchBase):
    @classmethod
    def from_available_time(cls, avail_time: AvailableTime) -> "MatchCreate":
        return cls(**(avail_time.model_dump()))


class MatchUpdate(MatchBase):
    status: str | None = Field(default=None)


class Match(MatchBase, MatchInmutable, table=True):
    id: int = Field(default=None, primary_key=True)

    __tablename__ = "matches"
    __table_args__ = (
        UniqueConstraint(
            "court_name",
            "court_public_id",
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


class MatchFilters(MatchBase):
    id: int | None = None
    public_id: UUID | None = None
    court_name: str | None = None
    court_public_id: uuid.UUID | None = None
    time: int | None = None
    date: datetime.date | None = None
    status: str | None = None
