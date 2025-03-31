from datetime import date
from typing import Any

from app.core.config import settings
from app.models.available_time import AvailableTime

from .base_service import BaseService

PROVISIONAL_LATITUDE = -27.4249569
PROVISIONAL_LONGITUDE = -57.3342325


class BusinessService(BaseService):
    def __init__(self) -> None:
        """Init the service."""
        super().__init__()
        self._set_base_url(
            is_http=True,
            host=settings.BUSINESS_SERVICE_HOST,
            port=settings.BUSINESS_SERVICE_PORT,
        )
        if settings.BUSINESS_SERVICE_API_KEY:
            self.set_base_headers({"x-api-key": settings.BUSINESS_SERVICE_API_KEY})

    async def get_available_times(
        self, business_public_id: int, court_public_id: str, date: date
    ) -> list[AvailableTime]:
        "Get available times from business service"
        params: dict[str, Any] = {
            "business_id": business_public_id,
            "court_name": court_public_id,
            "date": date,
        }
        content = await self.get(
            f"/api/v1/businesses/{business_public_id}/padel-courts/{court_public_id}/available-matches/",
            params=params,
        )
        data = content["data"]
        avail_times = []
        for datum in data:
            avail_time = AvailableTime(
                business_public_id=datum["business_id"],
                court_public_id=datum["court_name"],
                latitude=PROVISIONAL_LATITUDE,
                longitude=PROVISIONAL_LONGITUDE,
                # latitude=datum["latitude"],
                # longitude=datum["longitude"],
                date=datum["date"],
                time=datum["initial_hour"],
                is_reserved=datum["reserve"],
            )
            avail_times.append(avail_time)
        return avail_times
