from collections.abc import AsyncGenerator
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from pytest_asyncio import is_async_test
from sqlalchemy import delete
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import test_settings
from app.core.db import get_async_engine, init_db
from app.main import app
from app.models.item import Item
from app.models.match import Match
from app.tests.utils.utils import get_x_api_key_header
from app.utilities.dependencies import get_db


@pytest_asyncio.fixture(name="session")
async def db() -> AsyncGenerator[AsyncSession, None]:
    db_url = str(test_settings.SQLALCHEMY_DATABASE_URI)
    async with AsyncSession(get_async_engine(db_url)) as session:
        await init_db(db_url)
        yield session
        await session.exec(delete(Item))  # type: ignore[call-overload]
        await session.exec(delete(Match))  # type: ignore[call-overload]
        await session.commit()


@pytest_asyncio.fixture(name="async_client")
async def async_client(session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    def get_session_override() -> AsyncSession:
        return session

    app.dependency_overrides[get_db] = get_session_override
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
def x_api_key_header() -> dict[str, str]:
    """Fixture to provide an X-API-Key header."""
    return get_x_api_key_header()


def pytest_collection_modifyitems(items: Any) -> None:
    pytest_asyncio_tests = (item for item in items if is_async_test(item))
    session_scope_marker = pytest.mark.asyncio(loop_scope="session")
    for async_test in pytest_asyncio_tests:
        async_test.add_marker(session_scope_marker, append=False)
