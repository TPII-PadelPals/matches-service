from typing import ClassVar
from uuid import UUID

from sqlmodel import Field, SQLModel

from app.models.available_time import AvailableTime


class PlayerBase(SQLModel):
    latitude: float | None = Field(default=None)
    longitude: float | None = Field(default=None)
    time_availability: int | None = Field(default=None)


class PlayerImmutable(SQLModel):
    user_public_id: UUID | None = Field(default=None)


class Player(PlayerBase, PlayerImmutable):
    pass


class PlayerFilters(PlayerBase, PlayerImmutable):
    MORNING: ClassVar[int] = 1
    AFTERNOON: ClassVar[int] = 2
    EVENING: ClassVar[int] = 3

    available_days: list[int] | None = Field(default=None)
    n_players: int | None = Field(default=None)

    @staticmethod
    def to_time_availability(time: int) -> int:
        if time >= 6 and time <= 11:
            return PlayerFilters.MORNING
        elif time > 11 and time <= 17:
            return PlayerFilters.AFTERNOON
        elif time > 17 and time <= 24:
            return PlayerFilters.EVENING
        else:
            return 0

    @classmethod
    def from_available_time(cls, avail_time: AvailableTime) -> "PlayerFilters":
        available_days = None
        if avail_time.date:
            available_days = [avail_time.date.isoweekday()]
        return cls(
            time_availability=cls.to_time_availability(avail_time.time),
            available_days=available_days,
            **(avail_time.model_dump()),
        )
