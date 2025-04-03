import asyncio
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
from app.models.match_player import MatchPlayer
from app.tests.utils.utils import get_x_api_key_header
from app.utilities.dependencies import get_db

db_url = str(test_settings.SQLALCHEMY_DATABASE_URI)


@pytest_asyncio.fixture(name="session")
async def db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(
        get_async_engine(db_url), expire_on_commit=False
    ) as _session:
        try:
            await init_db(db_url)
            yield _session
            await _session.exec(delete(Item))  # type: ignore[call-overload]
            await _session.exec(delete(Match))  # type: ignore[call-overload]
            await _session.exec(delete(MatchPlayer))  # type: ignore[call-overload]
            await _session.commit()
        finally:
            await _session.close()


@pytest_asyncio.fixture(autouse=True)
async def override_dependency(session: AsyncSession) -> None:
    app.dependency_overrides[get_db] = lambda: session


@pytest_asyncio.fixture(name="async_client")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest_asyncio.fixture(scope="session")
def event_loop() -> Any:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
def x_api_key_header() -> dict[str, str]:
    """Fixture to provide an X-API-Key header."""
    return get_x_api_key_header()


def pytest_collection_modifyitems(items: Any) -> None:
    pytest_asyncio_tests = (item for item in items if is_async_test(item))
    session_scope_marker = pytest.mark.asyncio(loop_scope="session")
    for async_test in pytest_asyncio_tests:
        async_test.add_marker(session_scope_marker, append=False)
