from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel import SQLModel

from app.core.config import settings
from app.models import Item, Match, MatchPlayer  # noqa: F401


def get_async_engine(
    engine_url: str = str(settings.SQLALCHEMY_DATABASE_URI),
) -> AsyncEngine:
    return create_async_engine(engine_url)


async def init_db(engine_url: str = str(settings.SQLALCHEMY_DATABASE_URI)) -> None:
    async with get_async_engine(engine_url).begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def restart_db(engine_url: str = str(settings.SQLALCHEMY_DATABASE_URI)) -> None:
    async with get_async_engine(engine_url).begin() as conn:
        await conn.exec_driver_sql("DROP SCHEMA public CASCADE;")
        await conn.exec_driver_sql("CREATE SCHEMA public;")
