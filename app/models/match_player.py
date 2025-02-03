from typing import Self
from uuid import UUID

from sqlmodel import Field, SQLModel


class MatchPlayerBase(SQLModel):
    reserve: str | None = Field(default="provisional")


class MatchPlayerMatchPublicID(SQLModel):
    match_public_id: UUID | None = Field()


class MatchPlayerUserPublicID(SQLModel):
    user_public_id: UUID | None = Field()


class MatchPlayerCreatePublic(MatchPlayerBase, MatchPlayerUserPublicID):
    pass


class MatchPlayerInmmutable(MatchPlayerMatchPublicID, MatchPlayerUserPublicID):
    pass


class MatchPlayerCreate(MatchPlayerBase, MatchPlayerInmmutable):
    @classmethod
    def from_public(
        cls, match_public_id: UUID, match_player_public_in: MatchPlayerCreatePublic
    ) -> Self:
        data = match_player_public_in.model_dump()
        data["match_public_id"] = match_public_id
        return cls(**data)


class MatchPlayer(MatchPlayerBase, MatchPlayerInmmutable, table=True):
    id: int = Field(default=None, primary_key=True)

    __tablename__ = "matches_players"


class MatchPlayerPublic(MatchPlayerBase, MatchPlayerInmmutable):
    pass
