import datetime
from typing import Any

from httpx import AsyncClient, Response
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import test_settings
from app.models.match import MatchCreate
from app.services.match_service import MatchService


def serialize_match_data(court_id: int, time: int, date: str) -> dict[str, Any]:
    return {
        "court_id": court_id,
        "time": time,
        "date": date,
    }


async def create_match(
    async_client: AsyncClient, x_api_key_header: dict[str, Any], data: dict[str, Any]
) -> Response:
    return await async_client.post(
        f"{test_settings.API_V1_STR}/matches/",
        headers=x_api_key_header,
        json=data,
    )


async def generate_match(
    session: AsyncSession, match_in: dict[str, Any]
) -> dict[str, Any]:
    match_generated = MatchCreate(
        court_id=match_in["court_id"],
        time=match_in["time"],
        date=datetime.date.fromisoformat(match_in["date"]),
    )
    service = MatchService()
    prov_match = await service.create_match(session, match_generated)
    return prov_match.model_dump(mode="json")
