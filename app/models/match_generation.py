from datetime import datetime

from sqlmodel import Field, SQLModel


class MatchGenerationCreate(SQLModel):
    business_public_id: int = Field()
    court_public_id: str = Field()
    date: datetime = Field()
