import datetime
import uuid

from sqlmodel import Field, SQLModel


class MatchGenerationCreate(SQLModel):
    business_public_id: uuid.UUID = Field()
    court_name: str = Field()
    date: datetime.date = Field()
