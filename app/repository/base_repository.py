import warnings
from typing import Any, TypeVar

from sqlalchemy import asc, delete, desc, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.utilities.commit import commit_refresh_or_flush
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
        await commit_refresh_or_flush(
            self.session, should_commit, records, self._handle_commit_exceptions
        )

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
        order_by: list[tuple[str, bool]] | None = None,
        limit: int | None = None,
        **filters: Any,
    ) -> list[M]:
        """
        order_by: List of tuples(M.attribute, is_ascending)
        to order the result.
        limit: Max number of records to get.
        """
        query = select(model)

        # Filters
        for key, value in filters.items():
            attr = getattr(model, key)
            query = query.where(attr == value)

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

    async def get_record(self, model: type[M], **filters: Any) -> M:
        result = await self.get_records(model, **filters)
        if not result:
            raise NotFoundException(model.name())  # type: ignore
        return result[0]

    async def update_record(
        self,
        model: type[M],
        record_update: U,
        should_commit: bool = True,
        **filters: Any,
    ) -> M:
        record = await self.get_record(model, **filters)
        update_dict = record_update.model_dump(exclude_none=True)
        record.sqlmodel_update(update_dict)
        self.session.add(record)
        await self._commit_refresh_or_flush(should_commit, [record])
        return record

    async def delete_records(
        self, model: type[M], should_commit: bool = True, **filters: Any
    ) -> None:
        query = delete(model)

        for key, values in filters.items():
            attr = getattr(model, key)
            or_conditions = [attr == value for value in values]
            query = query.where(or_(False, *or_conditions))

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            await self.session.execute(query)

        await self._commit_refresh_or_flush(should_commit, [])
