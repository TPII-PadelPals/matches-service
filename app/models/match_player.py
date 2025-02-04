from typing import Self
from uuid import UUID

from sqlalchemy import UniqueConstraint
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


class MatchPlayerUpdate(MatchPlayerBase):
    pass


class MatchPlayer(MatchPlayerBase, MatchPlayerInmmutable, table=True):
    id: int = Field(default=None, primary_key=True)

    __tablename__ = "matches_players"
    __table_args__ = (
        UniqueConstraint(
            "match_public_id",
            "user_public_id",
            name="uq_match_player",
        ),
    )


class MatchPlayerPublic(MatchPlayerBase, MatchPlayerInmmutable):
    @classmethod
    def from_private(cls, match_player: MatchPlayer) -> Self:
        data = match_player.model_dump()
        return cls(**data)


class MatchPlayerListPublic(SQLModel):
    data: list[MatchPlayerPublic]
    count: int


class MatchPlayerFilter(SQLModel):
    match_public_id: UUID | None = None
    user_public_id: UUID | None = None
    reserve: str | None = None
