from datetime import datetime

from sqlmodel import Field, SQLModel


class AvailableTime(SQLModel):
    business_public_id: int = Field()
    court_public_id: str = Field()
    latitude: float = Field()
    longitude: float = Field()
    date: datetime = Field()
    time: int = Field()
    is_reserved: bool = Field()
