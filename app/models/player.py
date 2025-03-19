from uuid import UUID

from sqlmodel import Field, SQLModel


class Player(SQLModel):
    user_public_id: UUID = Field()
    telegram_id: int | None = Field(default=None)
    search_range_km: int | None = Field(default=None)
    address: str | None = Field(default=None)
    latitude: float | None = Field(default=None)
    longitude: float | None = Field(default=None)
    time_availability: int | None = Field(default=None)
