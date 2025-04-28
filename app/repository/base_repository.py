from typing import TypeVar
from uuid import UUID

from sqlalchemy import asc, desc
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

    async def _commit_refresh_or_flush(
        self, should_commit: bool, records: list[M]
    ) -> None:
        try:
            if should_commit:
                await self.session.commit()
                for record in records:
                    await self.session.refresh(record)
            else:
                await self.session.flush()
        except IntegrityError as e:
            await self.session.rollback()
            self._handle_commit_exceptions(e)

    async def create_record(
        self, model: type[M], record_create: C, should_commit: bool = True
    ) -> M:
        record = model.model_validate(record_create)
        self.session.add(record)
        await self._commit_refresh_or_flush(should_commit, [record])
        return record

    async def create_records(
        self, model: type[M], records_create: list[C], should_commit: bool = True
    ) -> list[M]:
        records = [model.model_validate(record) for record in records_create]
        self.session.add_all(records)
        await self._commit_refresh_or_flush(should_commit, records)
        return records

    async def get_records(
        self,
        model: type[M],
        filters: list[F],
        order_by: list[tuple[str, bool]] | None = None,
        limit: int | None = None,
    ) -> list[M]:
        """
        order_by: List of tuples(M.attribute, is_ascending)
        to order the result.
        limit: Max number of records to get.
        """
        # Filters
        or_conditions = []
        for filter in filters:
            and_conditions = [
                getattr(model, attr) == value
                for attr, value in vars(filter).items()
                if value is not None
            ]
            or_conditions.append(and_(*and_conditions))
        query = select(model).where(or_(*or_conditions))

        # Order
        if order_by is None:
            order_by = []
        for attr, is_ascending in order_by:
            column = getattr(model, attr, None)
            order_func = asc if is_ascending else desc
            if column:
                query = query.order_by(order_func(column))

        # Limit
        if limit is not None:
            query = query.limit(limit)

        result = await self.session.exec(query)  # type: ignore
        return list(result.scalars().all())

    async def get_record(
        self, model: type[M], model_filter: type[F], ids: dict[str, UUID]
    ) -> M:
        filters = [model_filter(**ids)]
        result = await self.get_records(model, filters)
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
        should_commit: bool = True,
    ) -> M:
        record = await self.get_record(model, model_filter, ids)
        update_dict = record_update.model_dump(exclude_none=True)
        record.sqlmodel_update(update_dict)
        self.session.add(record)
        await self._commit_refresh_or_flush(should_commit, [record])
        return record
