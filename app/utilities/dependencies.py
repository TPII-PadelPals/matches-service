from collections.abc import AsyncGenerator
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, Query
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.core.db import get_async_engine
from app.utilities.exceptions import (
    NotAuthorizedException,
    NotEnoughPermissionsException,
)


async def get_token_header(x_api_key: Annotated[str, Header()]) -> None:
    if x_api_key != settings.API_KEY:
        raise NotAuthorizedException()


async def get_user_id_param(user_id: Annotated[UUID, Query()]) -> None:
    if not user_id:
        raise NotEnoughPermissionsException()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async_session = sessionmaker(
        bind=get_async_engine(),
        class_=AsyncSession,
        expire_on_commit=False,  # type: ignore[call-overload]
    )
    async with async_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_db)]
