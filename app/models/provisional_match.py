import datetime
from typing import Self
from uuid import UUID, uuid4

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class ProvisionalMatchBase(SQLModel):
    court_id: int | None = Field(default=None)
    time: int | None = Field(default=None)
    date: datetime.date | None = Field(default=None)
    status: str | None = Field(default=None)


class ProvisionalMatchInmutable(SQLModel):
    public_id: UUID | None = Field(default_factory=uuid4, unique=True)


class ProvisionalMatchCreate(ProvisionalMatchBase):
    status: str | None = Field(default="provisional")


class ProvisionalMatchUpdate(ProvisionalMatchBase):
    pass


class ProvisionalMatch(ProvisionalMatchBase, ProvisionalMatchInmutable, table=True):
    id: int = Field(default=None, primary_key=True)

    __tablename__ = "provisional_matches"
    __table_args__ = (
        UniqueConstraint(
            "court_id",
            "time",
            "date",
            name="uq_match_constraints",
        ),
    )


# Properties to return via API, id is always required
class ProvisionalMatchPublic(ProvisionalMatchBase, ProvisionalMatchInmutable):
    @classmethod
    def from_private(cls, match: ProvisionalMatch) -> Self:
        data = match.model_dump()
        return cls(**data)


class ProvisionalMatchListPublic(SQLModel):
    data: list[ProvisionalMatchPublic]
    count: int


class ProvisionalMatchFilters(ProvisionalMatchBase, ProvisionalMatchInmutable):
    id: int | None = None
    public_id: UUID | None = None
    court_id: int | None = None
    time: int | None = None
    date: datetime.date | None = None
    status: str | None = None
