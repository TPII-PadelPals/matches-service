import datetime
import uuid
from typing import Any

from httpx import AsyncClient, Response
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import test_settings
from app.models.provisional_match import ProvisionalMatchCreate
from app.services.provisional_match_service import ProvisionalMatchService


def set_provisional_match_data(court_id: int, time: int, date: str) -> dict[str, Any]:
    return {
        "user_public_id_1": str(uuid.uuid4()),
        "user_public_id_2": str(uuid.uuid4()),
        "court_id": court_id,
        "time": time,
        "date": date,
    }


async def create_provisional_match(
    async_client: AsyncClient, x_api_key_header: dict[str, Any], data: dict[str, Any]
) -> Response:
    return await async_client.post(
        f"{test_settings.API_V1_STR}/provisional-matches/",
        headers=x_api_key_header,
        json=data,
    )


async def generate_provisional_match(
    session: AsyncSession, provisional_match_in: dict[str, Any]
) -> None:
    provisional_match_generated = ProvisionalMatchCreate(
        user_public_id_1=provisional_match_in["user_public_id_1"],
        user_public_id_2=provisional_match_in["user_public_id_2"],
        court_id=provisional_match_in["court_id"],
        time=provisional_match_in["time"],
        date=datetime.date.fromisoformat(provisional_match_in["date"]),
    )
    service = ProvisionalMatchService()
    _ = await service.create_match(session, provisional_match_generated)
