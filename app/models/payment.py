from uuid import UUID

from sqlmodel import Field, SQLModel


class Payment(SQLModel):
    public_id: UUID = Field()
    match_public_id: UUID = Field()
    user_public_id: UUID = Field()
    pay_url: str = Field()
