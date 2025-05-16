from collections.abc import Callable
from typing import Any

from sqlalchemy.exc import IntegrityError

from app.utilities.dependencies import SessionDep


def handle_commit_exceptions(err: IntegrityError) -> None:
    raise err


async def commit_refresh_or_flush(
    session: SessionDep,
    should_commit: bool,
    records: list[Any] | None = None,
    handle_commit_exceptions: Callable[
        [IntegrityError], None
    ] = handle_commit_exceptions,
) -> None:
    if records is None:
        records = []
    try:
        if should_commit:
            await session.commit()
            for record in records:
                await session.refresh(record)
        else:
            await session.flush()
    except IntegrityError as e:
        await session.rollback()
        handle_commit_exceptions(e)
