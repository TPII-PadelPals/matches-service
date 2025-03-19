from uuid import UUID

from sqlmodel import Field, SQLModel

from app.models.available_time import AvailableTime


class Player(SQLModel):
    user_public_id: UUID = Field()
    telegram_id: int | None = Field(default=None)
    search_range_km: int | None = Field(default=None)
    address: str | None = Field(default=None)
    latitude: float | None = Field(default=None)
    longitude: float | None = Field(default=None)
    time_availability: int | None = Field(default=None)


class PlayerFilters(SQLModel):
    latitude: float | None = Field(default=None)
    longitude: float | None = Field(default=None)
    time_availability: int | None = Field(default=None)
    available_days: list[int] | None = Field(default=None)
    user_public_id: UUID | None = Field(default=None)
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
