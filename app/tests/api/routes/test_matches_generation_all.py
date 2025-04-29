import uuid
from typing import Any

from httpx import AsyncClient

from app.core.config import test_settings
from app.models.match_player import ReserveStatus
from app.models.player import PlayerFilters
from app.tests.utils.utils import (
    initial_apply_mocks_for_generate_matches,
)


async def test_generate_matches_given_business_and_date_creates_for_each_court(
    async_client: AsyncClient, x_api_key_header: dict[str, str], monkeypatch: Any
) -> None:
    n_courts = 3
    times = [8, 9, 10]
    test_data = {
        "business_public_id": str(uuid.uuid4()),
        "court_names": [f"Court {i}" for i in range(n_courts)],
        "court_public_ids": [str(uuid.uuid4()) for _ in range(n_courts)],
        "latitude": 0.0,
        "longitude": 0.0,
        "date": "2025-03-19",
        "times": times,
        "all_times": times,
        "is_reserved": False,
        "n_similar_players": 6,
    }

    assigned_players = initial_apply_mocks_for_generate_matches(
        monkeypatch, **test_data
    )

    data = {k: v for k, v in test_data.items() if k in ["business_public_id", "date"]}

    response = await async_client.post(
        f"{test_settings.API_V1_STR}/matches/generation/all",
        headers=x_api_key_header,
        json=data,
    )

    # Assertions
    assert response.status_code == 201

    matches_list = response.json()
    matches = matches_list["data"]
    assert len(matches) == (n_courts * len(times))

    for match_extended in matches:
        for k in ["court_public_id", "court_name"]:
            assert match_extended[k] in test_data[f"{k}s"]  # type: ignore
        assert match_extended["date"] == test_data["date"]
        time = match_extended["time"]
        time_avail = PlayerFilters.to_time_availability(time)
        assigned_player = assigned_players[time_avail]["assigned"]
        similar_players = assigned_players[time_avail]["similar"]
        similar_players_user_public_ids = [
            str(player.user_public_id) for player in similar_players
        ]

        # Should be one ASSIGNED player
        match_players = match_extended["match_players"]
        match_assigned_players = [
            player
            for player in match_players
            if player["reserve"] == ReserveStatus.ASSIGNED
        ]
        assert len(match_assigned_players) == 1
        match_assigned_player = match_assigned_players[0]
        assert match_assigned_player["user_public_id"] == str(
            assigned_player.user_public_id
        )

        # Should be N SIMILAR players
        match_similar_players_user_public_ids = [
            player["user_public_id"]
            for player in match_players
            if player["reserve"] == ReserveStatus.SIMILAR
        ]
        assert set(match_similar_players_user_public_ids) == set(
            similar_players_user_public_ids
        )
