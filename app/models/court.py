from uuid import UUID

from sqlmodel import Field, SQLModel


class Court(SQLModel):
    business_public_id: UUID = Field()
    court_public_id: UUID = Field()
    court_name: str = Field()
    price_per_hour: float = Field()
