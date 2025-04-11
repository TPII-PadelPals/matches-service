import datetime
import uuid
from typing import Any

from app.services.business_service import (
    BusinessService,
)


async def test_get_matches_for_business_court_and_date(monkeypatch: Any) -> None:
    business_public_id = uuid.uuid4()
    court_public_id = uuid.uuid4()
    court_name = "1"
    latitude = -27.4249569
    longitude = -57.3342325
    date = datetime.date(2025, 3, 3)
    times = [8, 9, 10]

    expected_avail_times: dict[str, Any] = {"data": []}
    for time in times:
        expected_avail_times["data"].append(
            {
                "business_public_id": business_public_id,
                "court_public_id": court_public_id,
                "court_name": court_name,
                "latitude": latitude,
                "longitude": longitude,
                "date": date,
                "initial_hour": time,
                "reserve": False,
            }
        )

    async def mock_get(self: Any, url: str, params: Any) -> Any:  # noqa: ARG001
        assert (
            url
            == f"/api/v1/businesses/{business_public_id}/padel-courts/{court_name}/available-matches/"
        )
        return expected_avail_times

    monkeypatch.setattr(BusinessService, "get", mock_get)

    avail_times = await BusinessService().get_available_times(
        business_public_id, court_name, date
    )

    for avail_time in avail_times:
        assert avail_time.business_public_id == business_public_id
        assert avail_time.court_public_id == court_public_id
        assert avail_time.court_name == court_name
        assert avail_time.latitude == latitude
        assert avail_time.longitude == longitude
        assert avail_time.date == date
        assert avail_time.time in times
        assert not avail_time.is_reserved
