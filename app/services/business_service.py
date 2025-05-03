import uuid
from datetime import date
from typing import Any

from app.core.config import settings
from app.models.available_time import AvailableTime
from app.models.court import Court

from .base_service import BaseService


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

    async def get_courts(self, business_public_id: uuid.UUID) -> list[Court]:
        content = await self.get("/api/v1/padel-courts/")
        data = content["data"]
        business_data = []
        for datum in data:
            if datum["business_public_id"] == str(business_public_id):
                business_data.append(datum)

        courts = []
        for datum in business_data:
            avail_time = Court(
                business_public_id=datum["business_public_id"],
                court_public_id=datum["court_public_id"],
                court_name=datum["name"],
                price_per_hour=datum["price_per_hour"],
            )
            courts.append(avail_time)
        return courts

    async def get_available_times(
        self, business_public_id: uuid.UUID, court_name: str, date: date
    ) -> list[AvailableTime]:
        "Get available times from business service"
        params: dict[str, Any] = {
            "business_id": business_public_id,
            "court_name": court_name,
            "date": date,
        }
        content = await self.get(
            f"/api/v1/businesses/{business_public_id}/padel-courts/{court_name}/available-matches/",
            params=params,
        )
        data = content["data"]
        avail_times = []
        for datum in data:
            avail_time = AvailableTime(
                business_public_id=datum["business_public_id"],
                court_public_id=datum["court_public_id"],
                court_name=datum["court_name"],
                latitude=datum["latitude"],
                longitude=datum["longitude"],
                date=datum["date"],
                time=datum["initial_hour"],
                is_reserved=datum["reserve"],
            )
            avail_times.append(avail_time)
        return avail_times
