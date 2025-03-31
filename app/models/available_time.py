import datetime
import uuid

from sqlmodel import Field, SQLModel


class AvailableTime(SQLModel):
    business_public_id: uuid.UUID = Field()
    court_public_id: str = Field()
    latitude: float = Field()
    longitude: float = Field()
    date: datetime.date = Field()
    time: int = Field()
    is_reserved: bool = Field()
