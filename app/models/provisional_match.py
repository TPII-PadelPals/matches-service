import datetime
import uuid

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


# Shared properties
class ProvisionalMatchBase(SQLModel):
    user_public_id_1: uuid.UUID = Field()
    user_public_id_2: uuid.UUID = Field()
    court_id: int = Field()
    time: int = Field()
    date: datetime.date = Field()


# Properties to receive on Provisional Match creation
class ProvisionalMatchCreate(ProvisionalMatchBase):
    pass


# Database model, database table inferred from class name
class ProvisionalMatch(ProvisionalMatchBase, table=True):
    id: int = Field(default=None, primary_key=True)

    __tablename__ = "provisional_matches"
    __table_args__ = (
        UniqueConstraint(
            "player_id_1",
            "player_id_2",
            "court_id",
            "time",
            "date",
            name="uq_match_constraints",
        ),
    )


# Properties to return via API, id is always required
class ProvisionalMatchPublic(ProvisionalMatchBase):
    pass


class ProvisionalMatchesPublic(SQLModel):
    data: list[ProvisionalMatchPublic]
    count: int


class ProvisionalMatchFilters(ProvisionalMatchBase):
    id: int | None = None
    player_id_1: str | None = None
    player_id_2: str | None = None
    court_id: int | None = None
    court_name: str | None = None
    time: int | None = None
    date: datetime.date | None = None

    def rotate_players_ids(self):
        result = ProvisionalMatchFilters(
            id=self.id,
            player_id_1=self.player_id_2,
            player_id_2=self.player_id_1,
            court_id=self.court_id,
            court_name=self.court_name,
            time=self.time,
            date=self.date,
        )
        return result
