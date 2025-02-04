from typing import TypeVar
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlalchemy.sql.expression import and_, or_
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.utilities.exceptions import NotFoundException

C = TypeVar("C", bound=SQLModel)
U = TypeVar("U", bound=SQLModel)
M = TypeVar("M", bound=SQLModel)
F = TypeVar("F", bound=SQLModel)


class BaseRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _handle_commit_exceptions(self, err: IntegrityError) -> None:
        raise err

    async def _commit_with_exception_handling(self) -> None:
        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            self._handle_commit_exceptions(e)

    async def create_record(self, model: type[M], record_create: C) -> M:
        record = model.model_validate(record_create)
        self.session.add(record)
        await self._commit_with_exception_handling()
        await self.session.refresh(record)
        return record

    async def create_records(self, model: type[M], records_create: list[C]) -> list[M]:
        records = [model.model_validate(record) for record in records_create]
        self.session.add_all(records)
        await self._commit_with_exception_handling()
        for record in records:
            await self.session.refresh(record)
        return records

    async def read_records(self, model: type[M], filters: list[F]) -> list[M]:
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

    async def read_record(
        self, model: type[M], model_filter: type[F], ids: dict[str, UUID]
    ) -> M:
        filters = [model_filter(**ids)]
        result = await self.read_records(model, filters)
        record = result[0] if result else None
        if record is None:
            raise NotFoundException(model.name())  # type: ignore
        return record

    async def update_record(
        self,
        model: type[M],
        model_filter: type[F],
        ids: dict[str, UUID],
        record_update: U,
    ) -> M:
        record = await self.read_record(model, model_filter, ids)
        update_dict = record_update.model_dump(exclude_none=True)
        record.sqlmodel_update(update_dict)
        self.session.add(record)
        await self._commit_with_exception_handling()
        await self.session.refresh(record)
        return record
