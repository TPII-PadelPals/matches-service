from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.routing import APIRoute

from app.api.main import api_router
from app.core.config import settings
from app.core.db import init_db
from app.utilities.dependencies import get_token_header


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


@asynccontextmanager
async def lifespan(_: FastAPI):  # type:ignore[no-untyped-def]
    # await restart_db()
    await init_db()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    dependencies=[Depends(get_token_header)],
    lifespan=lifespan,
)

# Register routes
app.include_router(api_router, prefix=settings.API_V1_STR)
