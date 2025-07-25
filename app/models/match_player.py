from enum import Enum
from uuid import UUID

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class ReserveStatus(str, Enum):
    ASSIGNED = "assigned"
    SIMILAR = "similar"
    PROVISIONAL = "Provisional"
    INSIDE = "inside"
    REJECTED = "Rejected"
    OUTSIDE = "outside"


class MatchPlayerBase(SQLModel):
    reserve: str | None = Field(default=ReserveStatus.PROVISIONAL)


class MatchPlayerMatchPublicID(SQLModel):
    match_public_id: UUID | None = Field(
        foreign_key="matches.public_id", ondelete="CASCADE"
    )


class MatchPlayerInmmutable(SQLModel):
    user_public_id: UUID = Field()
    distance: float = Field()


class MatchPlayerInmmutableExtended(MatchPlayerInmmutable, MatchPlayerMatchPublicID):
    pass


class MatchPlayerCreatePublic(MatchPlayerBase, MatchPlayerInmmutable):
    pass


class MatchPlayerCreate(MatchPlayerBase, MatchPlayerInmmutableExtended):
    @classmethod
    def from_public(
        cls, match_public_id: UUID, match_player_public_in: MatchPlayerCreatePublic
    ) -> "MatchPlayerCreate":
        data = match_player_public_in.model_dump()
        data["match_public_id"] = match_public_id
        return cls(**data)


class MatchPlayerUpdate(MatchPlayerBase):
    def is_inside(self) -> bool:
        return self.reserve == ReserveStatus.INSIDE


class MatchPlayer(MatchPlayerBase, MatchPlayerInmmutableExtended, table=True):
    id: int = Field(default=None, primary_key=True)

    __tablename__ = "matches_players"
    __table_args__ = (
        UniqueConstraint(
            "match_public_id",
            "user_public_id",
            name="uq_match_player",
        ),
    )

    @classmethod
    def name(cls) -> str:
        return "MatchPlayer"

    def is_assigned(self) -> bool:
        return self.reserve == ReserveStatus.ASSIGNED


class MatchPlayerPublic(MatchPlayerBase, MatchPlayerInmmutableExtended):
    @classmethod
    def from_private(cls, match_player: MatchPlayer) -> "MatchPlayerPublic":
        data = match_player.model_dump()
        return cls(**data)

    def get_assigned_players_uuids(self) -> UUID | None:
        if self.reserve == ReserveStatus.ASSIGNED:
            return self.user_public_id
        return None


class MatchPlayerListPublic(SQLModel):
    data: list[MatchPlayerPublic]
    count: int

    @classmethod
    def from_private(
        cls, match_player_list: list[MatchPlayer]
    ) -> "MatchPlayerListPublic":
        data = []
        for match_player in match_player_list:
            data.append(MatchPlayerPublic.from_private(match_player))
        count = len(match_player_list)
        return cls(data=data, count=count)


class Pay(SQLModel):
    pay_url: str | None = Field()


class MatchPlayerPay(MatchPlayer, Pay):
    @classmethod
    def from_match_player(
        cls, match_player: MatchPlayer, pay_url: str | None
    ) -> "MatchPlayerPay":
        data = match_player.model_dump()
        return cls(pay_url=pay_url, **data)


class MatchPlayerPayPublic(MatchPlayerBase, MatchPlayerInmmutableExtended, Pay):
    pass


class MatchPlayerFilter(SQLModel):
    match_public_id: UUID | None = None
    user_public_id: UUID | None = None
    reserve: str | None = None
