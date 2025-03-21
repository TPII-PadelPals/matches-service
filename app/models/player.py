from uuid import UUID

from sqlmodel import Field, SQLModel

from app.models.available_time import AvailableTime


class PlayerBase(SQLModel):
    user_public_id: UUID | None = Field(default=None)
    latitude: float | None = Field(default=None)
    longitude: float | None = Field(default=None)
    time_availability: int | None = Field(default=None)


class Player(PlayerBase):
    pass


class PlayerFilters(PlayerBase):
    available_days: list[int] | None = Field(default=None)
    n_players: int | None = Field(default=None)

    @classmethod
    def from_available_time(cls, avail_time: AvailableTime) -> "PlayerFilters":
        available_days = None
        if avail_time.date:
            available_days = [avail_time.date.isoweekday()]
        return cls(
            time_availability=avail_time.time,
            available_days=available_days,
            **(avail_time.model_dump()),
        )
