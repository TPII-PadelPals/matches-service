from typing import TypeVar

from sqlalchemy.future import select
from sqlalchemy.sql.expression import and_, or_
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

M = TypeVar("M", bound=SQLModel)
F = TypeVar("F", bound=SQLModel)


class BaseRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def filter_records(self, model: type[M], filters: list[F]) -> list[M]:
        or_conditions = []

        for filter in filters:
            and_conditions = [
                getattr(model, attr) == value
                for attr, value in vars(filter).items()
                if value is not None
            ]
            or_conditions.append(and_(*and_conditions))

        query = select(model).where(or_(*or_conditions))
        result = await self.session.exec(query)  # type: ignore
        return list(result.scalars().all())
