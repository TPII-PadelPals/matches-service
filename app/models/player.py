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
    available_days: list[int] | None = Field(default=None)
    n_players: int | None = Field(default=None)

    @staticmethod
    def to_time_availability(time: int) -> int:
        if time >= 6 and time <= 11:
            return 1
        elif time > 11 and time <= 17:
            return 2
        elif time > 17 and time <= 24:
            return 3

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
