import datetime
import uuid

from sqlmodel import Field, SQLModel


class MatchGenerationCreate(SQLModel):
    business_public_id: uuid.UUID = Field()
    date: datetime.date = Field()


class MatchGenerationCreateExtended(MatchGenerationCreate):
    court_name: str = Field()
