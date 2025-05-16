import uuid
from datetime import date
from operator import itemgetter
from typing import Any

from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import test_settings
from app.models.available_time import AvailableTime
from app.models.match import MatchCreate
from app.models.match_extended import MatchExtended
from app.models.match_player import MatchPlayerCreate, ReserveStatus
from app.models.payment import Payment
from app.models.player import Player, PlayerFilters
from app.services.business_service import BusinessService
from app.services.match_player_service import MatchPlayerService
from app.services.match_service import MatchService
from app.services.payment_service import PaymentsService
from app.services.players_service import PlayersService


async def test_add_one_player_to_match_reserve_is_provisional(
    async_client: AsyncClient, session: AsyncSession, x_api_key_header: dict[str, str]
) -> None:
    # Create match
    match = await MatchService().create_match(
        session,
        MatchCreate(
            business_public_id=uuid.uuid4(),
            court_public_id=uuid.uuid4(),
            court_name="0",
            date="2024-11-25",
            time=8,
        ),
    )

    # Add player to match
    data = {"user_public_id": str(uuid.uuid4()), "distance": 0.0}
    response = await async_client.post(
        f"{test_settings.API_V1_STR}/matches/{match.public_id}/players/",
        headers=x_api_key_header,
        json=data,
    )
    assert response.status_code == 201
    content = response.json()
    assert content["match_public_id"] == str(match.public_id)
    assert content["user_public_id"] == data["user_public_id"]
    assert content["distance"] == data["distance"]
    assert content["reserve"] == ReserveStatus.PROVISIONAL


async def test_add_same_player_to_match_raises_exception(
    async_client: AsyncClient, session: AsyncSession, x_api_key_header: dict[str, str]
) -> None:
    # Create match
    match = await MatchService().create_match(
        session,
        MatchCreate(
            business_public_id=uuid.uuid4(),
            court_public_id=uuid.uuid4(),
            court_name="0",
            date="2024-11-25",
            time=8,
        ),
    )
    # Add player to match
    data = {"user_public_id": str(uuid.uuid4()), "distance": 0.0}
    for _ in range(2):
        response = await async_client.post(
            f"{test_settings.API_V1_STR}/matches/{match.public_id}/players/",
            headers=x_api_key_header,
            json=data,
        )
    assert response.status_code == 409
    content = response.json()
    assert content["detail"] == "MatchPlayer already exists."


async def test_add_many_players_to_match(
    async_client: AsyncClient, session: AsyncSession, x_api_key_header: dict[str, str]
) -> None:
    # Create match
    match = await MatchService().create_match(
        session,
        MatchCreate(
            business_public_id=uuid.uuid4(),
            court_public_id=uuid.uuid4(),
            court_name="0",
            date="2024-11-25",
            time=8,
        ),
    )

    # Add players to match
    n_players = 4
    data = [
        {"user_public_id": str(uuid.uuid4()), "distance": 0.0} for _ in range(n_players)
    ]
    response = await async_client.post(
        f"{test_settings.API_V1_STR}/matches/{match.public_id}/players/bulk/",
        headers=x_api_key_header,
        json=data,
    )
    assert response.status_code == 201
    content = response.json()
    for value in data:
        value["match_public_id"] = match.public_id
        value["reserve"] = ReserveStatus.PROVISIONAL
    all(match_player in data for match_player in content)


async def test_get_one_match_player(
    async_client: AsyncClient, session: AsyncSession, x_api_key_header: dict[str, str]
) -> None:
    # Create match
    match = await MatchService().create_match(
        session,
        MatchCreate(
            business_public_id=uuid.uuid4(),
            court_public_id=uuid.uuid4(),
            court_name="0",
            date="2024-11-25",
            time=8,
        ),
    )

    # Add player to match
    user_public_id = str(uuid.uuid4())
    data = {"user_public_id": user_public_id, "distance": 0.0}
    await async_client.post(
        f"{test_settings.API_V1_STR}/matches/{match.public_id}/players/",
        headers=x_api_key_header,
        json=data,
    )
    response = await async_client.get(
        f"{test_settings.API_V1_STR}/matches/{match.public_id}/players/{user_public_id}",
        headers=x_api_key_header,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["match_public_id"] == str(match.public_id)
    assert content["user_public_id"] == user_public_id
    assert content["reserve"] == ReserveStatus.PROVISIONAL


async def test_get_match_players_returns_all_players_associated_to_match(
    async_client: AsyncClient, session: AsyncSession, x_api_key_header: dict[str, str]
) -> None:
    # Create match
    match = await MatchService().create_match(
        session,
        MatchCreate(
            business_public_id=uuid.uuid4(),
            court_public_id=uuid.uuid4(),
            court_name="0",
            date="2024-11-25",
            time=8,
        ),
    )

    # Add players to match
    n_players = 4
    user_public_ids = [str(uuid.uuid4()) for _ in range(n_players)]
    data = [
        {"user_public_id": user_public_id, "distance": 0.0}
        for user_public_id in user_public_ids
    ]
    await async_client.post(
        f"{test_settings.API_V1_STR}/matches/{match.public_id}/players/bulk/",
        headers=x_api_key_header,
        json=data,
    )
    response = await async_client.get(
        f"{test_settings.API_V1_STR}/matches/{match.public_id}/players/",
        headers=x_api_key_header,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["count"] == n_players
    for match_player in content["data"]:
        assert match_player["match_public_id"] == str(match.public_id)
        assert match_player["user_public_id"] in user_public_ids
        assert match_player["reserve"] == ReserveStatus.PROVISIONAL


async def test_update_one_player_reserve_to_inside_creates_payment(
    async_client: AsyncClient,
    session: AsyncSession,
    x_api_key_header: dict[str, str],
    monkeypatch: Any,
) -> None:
    # PRE
    # Create match
    match = await MatchService().create_match(
        session,
        MatchCreate(
            business_public_id=uuid.uuid4(),
            court_public_id=uuid.uuid4(),
            court_name="0",
            date="2024-11-25",
            time=8,
        ),
    )
    user_public_id = str(uuid.uuid4())
    pay_url = "https://www.mercadopago.com/mla/checkout/start?pref_id=123456"

    async def mock_create_payment(
        self: Any,  # noqa: ARG001
        match_extended: MatchExtended,  # noqa: ARG001
    ) -> Payment:
        return Payment(
            public_id=uuid.uuid4(),
            match_public_id=uuid.uuid4(),
            user_public_id=user_public_id,
            pay_url=pay_url,
        )

    monkeypatch.setattr(PaymentsService, "create_payment", mock_create_payment)

    # Create player ASSIGNED
    await MatchPlayerService().create_match_player(
        session,
        MatchPlayerCreate(
            match_public_id=match.public_id,
            user_public_id=user_public_id,
            distance=0.0,
            reserve=ReserveStatus.ASSIGNED,
        ),
    )

    # Action
    # Update player ASSIGNED -> INSIDE
    response = await async_client.patch(
        f"{test_settings.API_V1_STR}/matches/{match.public_id}/players/{user_public_id}/",
        headers=x_api_key_header,
        json={"reserve": ReserveStatus.INSIDE},
    )

    # POST
    assert response.status_code == 200
    content = response.json()
    assert content["match_public_id"] == str(match.public_id)
    assert content["user_public_id"] == user_public_id
    assert content["reserve"] == ReserveStatus.INSIDE
    assert content["pay_url"] == pay_url


async def test_update_one_player_raises_exception_when_match_player_not_exists(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    match_public_id = str(uuid.uuid4())
    user_public_id = str(uuid.uuid4())
    data = {"reserve": ReserveStatus.INSIDE}

    response = await async_client.patch(
        f"{test_settings.API_V1_STR}/matches/{match_public_id}/players/{user_public_id}/",
        headers=x_api_key_header,
        json=data,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "MatchPlayer not found."


async def test_one_player_reserve_to_inside(
    async_client: AsyncClient,
    session: AsyncSession,
    x_api_key_header: dict[str, str],
    monkeypatch: Any,
) -> None:
    # PRE
    # Create match
    match = await MatchService().create_match(
        session,
        MatchCreate(
            business_public_id=uuid.uuid4(),
            court_public_id=uuid.uuid4(),
            court_name="0",
            date="2024-11-25",
            time=8,
        ),
    )
    user_public_id = str(uuid.uuid4())
    pay_url = "https://www.mercadopago.com/mla/checkout/start?pref_id=123456"

    async def mock_create_payment(
        _self: Any, _match_extended: MatchExtended
    ) -> Payment:
        return Payment(
            public_id=uuid.uuid4(),
            match_public_id=uuid.uuid4(),
            user_public_id=user_public_id,
            pay_url=pay_url,
        )

    monkeypatch.setattr(PaymentsService, "create_payment", mock_create_payment)

    # Add player to match
    await MatchPlayerService().create_match_player(
        session,
        MatchPlayerCreate(
            match_public_id=match.public_id,
            user_public_id=user_public_id,
            distance=0.0,
            reserve=ReserveStatus.ASSIGNED,
        ),
    )

    # Action
    # Update player ASSIGNED -> INSIDE
    response = await async_client.patch(
        f"{test_settings.API_V1_STR}/matches/{match.public_id}/players/{user_public_id}/",
        headers=x_api_key_header,
        json={"reserve": ReserveStatus.INSIDE},
    )

    # POST
    assert response.status_code == 200
    content = response.json()
    assert content["match_public_id"] == str(match.public_id)
    assert content["user_public_id"] == user_public_id
    assert content["reserve"] == ReserveStatus.INSIDE
    assert content["pay_url"] == pay_url


async def test_one_player_reserve_to_accept_not_assigned_is_rejected(
    async_client: AsyncClient, session: AsyncSession, x_api_key_header: dict[str, str]
) -> None:
    # PRE
    # Create match
    match = await MatchService().create_match(
        session,
        MatchCreate(
            business_public_id=uuid.uuid4(),
            court_public_id=uuid.uuid4(),
            court_name="0",
            date="2024-11-25",
            time=8,
        ),
    )

    # Create player INSIDE
    inside_uuid = str(uuid.uuid4())
    await MatchPlayerService().create_match_player(
        session,
        MatchPlayerCreate(
            match_public_id=match.public_id,
            user_public_id=inside_uuid,
            distance=0.0,
            reserve=ReserveStatus.INSIDE,
        ),
    )

    # ACTION
    # Update match player
    response = await async_client.patch(
        f"{test_settings.API_V1_STR}/matches/{match.public_id}/players/{inside_uuid}/",
        headers=x_api_key_header,
        json={"reserve": ReserveStatus.INSIDE},
    )

    # POST
    assert response.status_code == 401


async def test_one_player_reserve_to_accept_not_provisional_is_rejected(
    async_client: AsyncClient, session: AsyncSession, x_api_key_header: dict[str, str]
) -> None:
    # Create match
    match = await MatchService().create_match(
        session,
        MatchCreate(
            business_public_id=uuid.uuid4(),
            court_public_id=uuid.uuid4(),
            court_name="0",
            date="2024-11-25",
            time=8,
        ),
    )
    # Add player to match
    outside_uuid = str(uuid.uuid4())
    await MatchPlayerService().create_match_player(
        session,
        MatchPlayerCreate(
            match_public_id=match.public_id,
            user_public_id=outside_uuid,
            distance=0.0,
            reserve=ReserveStatus.OUTSIDE,
        ),
    )

    # Update match player
    response = await async_client.patch(
        f"{test_settings.API_V1_STR}/matches/{match.public_id}/players/{outside_uuid}/",
        headers=x_api_key_header,
        json={"reserve": ReserveStatus.INSIDE},
    )
    assert response.status_code == 401


async def test_only_one_player_inside_then_only_one_similar_is_assigned(
    async_client: AsyncClient,
    session: AsyncSession,
    x_api_key_header: dict[str, str],
    monkeypatch: Any,
) -> None:
    match = await MatchService().create_match(
        session,
        MatchCreate(
            business_public_id=uuid.uuid4(),
            court_public_id=uuid.uuid4(),
            court_name="Cancha 1",
            date="2025-04-05",
            time=8,
        ),
    )

    # === PRE ===
    # Create one player ASSIGNED
    assigned_uuid = uuid.uuid4()
    await MatchPlayerService().create_match_player(
        session,
        MatchPlayerCreate(
            match_public_id=match.public_id,
            user_public_id=assigned_uuid,
            distance=0.0,
            reserve=ReserveStatus.ASSIGNED,
        ),
    )

    async def mock_create_payment(
        _self: Any, _match_extended: MatchExtended
    ) -> Payment:
        return Payment(
            public_id=uuid.uuid4(),
            match_public_id=uuid.uuid4(),
            user_public_id=assigned_uuid,
            pay_url="https://www.mercadopago.com/mla/checkout/start?pref_id=123456",
        )

    monkeypatch.setattr(PaymentsService, "create_payment", mock_create_payment)

    # Create one player SIMILAR
    similar_uuid = uuid.uuid4()
    await MatchPlayerService().create_match_player(
        session,
        MatchPlayerCreate(
            match_public_id=match.public_id,
            user_public_id=similar_uuid,
            distance=0.0,
            reserve=ReserveStatus.SIMILAR,
        ),
    )

    # === Action ===
    # Update player ASSIGNED -> INSIDE
    await async_client.patch(
        f"{test_settings.API_V1_STR}/matches/{match.public_id}/players/{assigned_uuid}/",
        headers=x_api_key_header,
        json={"reserve": ReserveStatus.INSIDE},
    )

    # === POST ===
    # Verify player SIMILAR -> ASSIGNED
    similar_player = await MatchPlayerService().get_match_player(
        session, match.public_id, similar_uuid
    )
    assert similar_player.reserve == ReserveStatus.ASSIGNED


async def test_only_one_player_inside_then_only_three_similar_are_assigned(
    async_client: AsyncClient,
    session: AsyncSession,
    x_api_key_header: dict[str, str],
    monkeypatch: Any,
) -> None:
    match = await MatchService().create_match(
        session,
        MatchCreate(
            business_public_id=uuid.uuid4(),
            court_public_id=uuid.uuid4(),
            court_name="Cancha 1",
            date="2025-04-05",
            time=8,
        ),
    )
    # === PRE ===
    # Create one player ASSIGNED
    assigned_uuid = uuid.uuid4()
    await MatchPlayerService().create_match_player(
        session,
        MatchPlayerCreate(
            match_public_id=match.public_id,
            user_public_id=assigned_uuid,
            distance=0.0,
            reserve=ReserveStatus.ASSIGNED,
        ),
    )

    async def mock_create_payment(
        self: Any,  # noqa: ARG001
        match_extended: MatchExtended,  # noqa: ARG001
    ) -> Payment:
        return Payment(
            public_id=uuid.uuid4(),
            match_public_id=uuid.uuid4(),
            user_public_id=assigned_uuid,
            pay_url="https://www.mercadopago.com/mla/checkout/start?pref_id=123456",
        )

    monkeypatch.setattr(PaymentsService, "create_payment", mock_create_payment)

    # Create three players SIMILAR
    similar_uuids = [uuid.uuid4() for _ in range(3)]
    for similar_uuid in similar_uuids:
        await MatchPlayerService().create_match_player(
            session,
            MatchPlayerCreate(
                match_public_id=match.public_id,
                user_public_id=similar_uuid,
                distance=0.0,
                reserve=ReserveStatus.SIMILAR,
            ),
        )

    # === Action ===
    # Update player ASSIGNED -> INSIDE
    await async_client.patch(
        f"{test_settings.API_V1_STR}/matches/{match.public_id}/players/{assigned_uuid}/",
        headers=x_api_key_header,
        json={"reserve": ReserveStatus.INSIDE},
    )

    # === POST ===
    # Verify three players SIMILAR -> ASSIGNED
    for similar_uuid in similar_uuids:
        similar_player = await MatchPlayerService().get_match_player(
            session, match.public_id, similar_uuid
        )
        assert similar_player.reserve == ReserveStatus.ASSIGNED


async def test_four_players_inside_then_no_more_assigned(
    async_client: AsyncClient,
    session: AsyncSession,
    x_api_key_header: dict[str, str],
    monkeypatch: Any,
) -> None:
    match = await MatchService().create_match(
        session,
        MatchCreate(
            business_public_id=uuid.uuid4(),
            court_public_id=uuid.uuid4(),
            court_name="Cancha 1",
            date="2025-04-05",
            time=8,
        ),
    )
    # === PRE ===
    # Create three players INSIDE
    for _ in range(3):
        await MatchPlayerService().create_match_player(
            session,
            MatchPlayerCreate(
                match_public_id=match.public_id,
                user_public_id=uuid.uuid4(),
                distance=0.0,
                reserve=ReserveStatus.INSIDE,
            ),
        )

    # Create one player ASSIGNED
    assigned_uuid = uuid.uuid4()
    await MatchPlayerService().create_match_player(
        session,
        MatchPlayerCreate(
            match_public_id=match.public_id,
            user_public_id=assigned_uuid,
            distance=0.0,
            reserve=ReserveStatus.ASSIGNED,
        ),
    )

    async def mock_create_payment(
        self: Any,  # noqa: ARG001
        match_extended: MatchExtended,  # noqa: ARG001
    ) -> Payment:
        return Payment(
            public_id=uuid.uuid4(),
            match_public_id=uuid.uuid4(),
            user_public_id=assigned_uuid,
            pay_url="https://www.mercadopago.com/mla/checkout/start?pref_id=123456",
        )

    monkeypatch.setattr(PaymentsService, "create_payment", mock_create_payment)

    # Create three players SIMILAR
    similar_uuids = [uuid.uuid4() for _ in range(3)]
    for similar_uuid in similar_uuids:
        await MatchPlayerService().create_match_player(
            session,
            MatchPlayerCreate(
                match_public_id=match.public_id,
                user_public_id=similar_uuid,
                distance=0.0,
                reserve=ReserveStatus.SIMILAR,
            ),
        )

    # === Action ===
    # Update player ASSIGNED -> INSIDE
    await async_client.patch(
        f"{test_settings.API_V1_STR}/matches/{match.public_id}/players/{assigned_uuid}/",
        headers=x_api_key_header,
        json={"reserve": ReserveStatus.INSIDE},
    )

    # === POST ===
    # Verify three players SIMILAR
    for similar_uuid in similar_uuids:
        similar_player = await MatchPlayerService().get_match_player(
            session, match.public_id, similar_uuid
        )
        assert similar_player.reserve == ReserveStatus.SIMILAR


async def test_two_players_inside_two_players_assigned_then_no_more_assigned(
    async_client: AsyncClient,
    session: AsyncSession,
    x_api_key_header: dict[str, str],
    monkeypatch: Any,
) -> None:
    match = await MatchService().create_match(
        session,
        MatchCreate(
            business_public_id=uuid.uuid4(),
            court_public_id=uuid.uuid4(),
            court_name="Cancha 1",
            date="2025-04-05",
            time=8,
        ),
    )
    # === PRE ===
    # Create one player INSIDE
    await MatchPlayerService().create_match_player(
        session,
        MatchPlayerCreate(
            match_public_id=match.public_id,
            user_public_id=uuid.uuid4(),
            distance=0.0,
            reserve=ReserveStatus.INSIDE,
        ),
    )

    # Create three players ASSIGNED
    assigned_uuids = [uuid.uuid4() for _ in range(3)]
    for assigned_uuid in assigned_uuids:
        await MatchPlayerService().create_match_player(
            session,
            MatchPlayerCreate(
                match_public_id=match.public_id,
                user_public_id=assigned_uuid,
                distance=0.0,
                reserve=ReserveStatus.ASSIGNED,
            ),
        )

    async def mock_create_payment(
        self: Any,  # noqa: ARG001
        match_extended: MatchExtended,  # noqa: ARG001
    ) -> Payment:
        return Payment(
            public_id=uuid.uuid4(),
            match_public_id=uuid.uuid4(),
            user_public_id=assigned_uuid,
            pay_url="https://www.mercadopago.com/mla/checkout/start?pref_id=123456",
        )

    monkeypatch.setattr(PaymentsService, "create_payment", mock_create_payment)

    # Create three players SIMILAR
    similar_uuids = [uuid.uuid4() for _ in range(3)]
    for similar_uuid in similar_uuids:
        await MatchPlayerService().create_match_player(
            session,
            MatchPlayerCreate(
                match_public_id=match.public_id,
                user_public_id=similar_uuid,
                distance=0.0,
                reserve=ReserveStatus.SIMILAR,
            ),
        )

    # === Action ===
    # Update one player ASSIGNED -> INSIDE
    await async_client.patch(
        f"{test_settings.API_V1_STR}/matches/{match.public_id}/players/{assigned_uuids[0]}/",
        headers=x_api_key_header,
        json={"reserve": ReserveStatus.INSIDE},
    )

    # === POST ===
    # Verify three players SIMILAR
    for similar_uuid in similar_uuids:
        similar_player = await MatchPlayerService().get_match_player(
            session, match.public_id, similar_uuid
        )
        assert similar_player.reserve == ReserveStatus.SIMILAR


async def test_three_players_inside_two_players_similar_then_the_closest_one_is_assigned(
    async_client: AsyncClient,
    session: AsyncSession,
    x_api_key_header: dict[str, str],
    monkeypatch: Any,
) -> None:
    match = await MatchService().create_match(
        session,
        MatchCreate(
            business_public_id=uuid.uuid4(),
            court_public_id=uuid.uuid4(),
            court_name="Cancha 1",
            date="2025-04-05",
            time=8,
        ),
    )
    # === PRE ===
    # Create two players INSIDE
    inside_uuids = [uuid.uuid4() for _ in range(2)]
    for inside_uuid in inside_uuids:
        await MatchPlayerService().create_match_player(
            session,
            MatchPlayerCreate(
                match_public_id=match.public_id,
                user_public_id=inside_uuid,
                distance=0,
                reserve=ReserveStatus.INSIDE,
            ),
        )

    # Create one player ASSIGNED (future INSIDE)
    assigned_uuid = uuid.uuid4()
    await MatchPlayerService().create_match_player(
        session,
        MatchPlayerCreate(
            match_public_id=match.public_id,
            user_public_id=assigned_uuid,
            distance=0.0,
            reserve=ReserveStatus.ASSIGNED,
        ),
    )

    async def mock_create_payment(
        self: Any,  # noqa: ARG001
        match_extended: MatchExtended,  # noqa: ARG001
    ) -> Payment:
        return Payment(
            public_id=uuid.uuid4(),
            match_public_id=uuid.uuid4(),
            user_public_id=assigned_uuid,
            pay_url="https://www.mercadopago.com/mla/checkout/start?pref_id=123456",
        )

    monkeypatch.setattr(PaymentsService, "create_payment", mock_create_payment)

    # Create two players SIMILAR
    similar_uuids = [uuid.uuid4() for _ in range(2)]
    distances = list(range(2))
    for similar_uuid, distance in zip(similar_uuids, distances, strict=False):
        await MatchPlayerService().create_match_player(
            session,
            MatchPlayerCreate(
                match_public_id=match.public_id,
                user_public_id=similar_uuid,
                distance=distance,
                reserve=ReserveStatus.SIMILAR,
            ),
        )

    # === Action ===
    # Update player ASSIGNED -> INSIDE
    await async_client.patch(
        f"{test_settings.API_V1_STR}/matches/{match.public_id}/players/{assigned_uuid}/",
        headers=x_api_key_header,
        json={"reserve": ReserveStatus.INSIDE},
    )

    # === POST ===
    # Verify closest player SIMILAR -> ASSIGNED
    closest_idx, _ = min(enumerate(distances), key=itemgetter(1))
    closest_uuid = similar_uuids[closest_idx]
    similar_player = await MatchPlayerService().get_match_player(
        session, match.public_id, closest_uuid
    )
    assert similar_player.reserve == ReserveStatus.ASSIGNED

    # Verify not-closest player SIMILAR -> SIMILAR
    farthest_idx, _ = max(enumerate(distances), key=itemgetter(1))
    farthest_uuid = similar_uuids[farthest_idx]
    similar_player = await MatchPlayerService().get_match_player(
        session, match.public_id, farthest_uuid
    )
    assert similar_player.reserve == ReserveStatus.SIMILAR


async def test_only_one_player_inside_more_than_three_players_similar_then_the_closest_three_are_assigned(
    async_client: AsyncClient,
    session: AsyncSession,
    x_api_key_header: dict[str, str],
    monkeypatch: Any,
) -> None:
    match = await MatchService().create_match(
        session,
        MatchCreate(
            business_public_id=uuid.uuid4(),
            court_public_id=uuid.uuid4(),
            court_name="Cancha 1",
            date="2025-04-05",
            time=8,
        ),
    )
    # === PRE ===
    # Create one player ASSIGNED (future INSIDE)
    assigned_uuid = uuid.uuid4()
    await MatchPlayerService().create_match_player(
        session,
        MatchPlayerCreate(
            match_public_id=match.public_id,
            user_public_id=assigned_uuid,
            distance=0.0,
            reserve=ReserveStatus.ASSIGNED,
        ),
    )

    async def mock_create_payment(
        self: Any,  # noqa: ARG001
        match_extended: MatchExtended,  # noqa: ARG001
    ) -> Payment:
        return Payment(
            public_id=uuid.uuid4(),
            match_public_id=uuid.uuid4(),
            user_public_id=assigned_uuid,
            pay_url="https://www.mercadopago.com/mla/checkout/start?pref_id=123456",
        )

    monkeypatch.setattr(PaymentsService, "create_payment", mock_create_payment)

    # Create two players SIMILAR
    similar_uuids = [uuid.uuid4() for _ in range(6)]
    for distance, similar_uuid in enumerate(similar_uuids):
        await MatchPlayerService().create_match_player(
            session,
            MatchPlayerCreate(
                match_public_id=match.public_id,
                user_public_id=similar_uuid,
                distance=distance,
                reserve=ReserveStatus.SIMILAR,
            ),
        )

    # === Action ===
    # Update player ASSIGNED -> INSIDE
    await async_client.patch(
        f"{test_settings.API_V1_STR}/matches/{match.public_id}/players/{assigned_uuid}/",
        headers=x_api_key_header,
        json={"reserve": ReserveStatus.INSIDE},
    )

    # === POST ===
    # Verify closest player SIMILAR -> ASSIGNED
    max_closest_distance = -1e6
    for closest_uuid in similar_uuids[:3]:
        closest_player = await MatchPlayerService().get_match_player(
            session, match.public_id, closest_uuid
        )
        assert closest_player.reserve == ReserveStatus.ASSIGNED
        if closest_player.distance > max_closest_distance:
            max_closest_distance = closest_player.distance

    # Verify not-closest player SIMILAR -> SIMILAR
    min_farthest_distance = 1e6
    for farthest_uuid in similar_uuids[3:]:
        farthest_player = await MatchPlayerService().get_match_player(
            session, match.public_id, farthest_uuid
        )
        assert farthest_player.reserve == ReserveStatus.SIMILAR
        if farthest_player.distance < min_farthest_distance:
            min_farthest_distance = farthest_player.distance

    assert max_closest_distance <= min_farthest_distance


async def test_one_player_inside_one_player_reserve_to_outside(
    async_client: AsyncClient, session: AsyncSession, x_api_key_header: dict[str, str]
) -> None:
    # PRE
    # Create match
    match = await MatchService().create_match(
        session,
        MatchCreate(
            business_public_id=uuid.uuid4(),
            court_public_id=uuid.uuid4(),
            court_name="0",
            date="2024-11-25",
            time=8,
        ),
    )

    # Create player INSIDE
    await MatchPlayerService().create_match_player(
        session,
        MatchPlayerCreate(
            match_public_id=match.public_id,
            user_public_id=uuid.uuid4(),
            distance=0.0,
            reserve=ReserveStatus.INSIDE,
        ),
    )

    # Create player ASSIGNED
    user_public_id = uuid.uuid4()
    await MatchPlayerService().create_match_player(
        session,
        MatchPlayerCreate(
            match_public_id=match.public_id,
            user_public_id=user_public_id,
            distance=0.0,
            reserve=ReserveStatus.INSIDE,
        ),
    )

    # === ACTION ===
    # Update player ASSIGNED -> OUTSIDE
    response = await async_client.patch(
        f"{test_settings.API_V1_STR}/matches/{match.public_id}/players/{user_public_id}/",
        headers=x_api_key_header,
        json={"reserve": ReserveStatus.OUTSIDE},
    )

    # === POST ===
    assert response.status_code == 200
    content = response.json()
    assert content["match_public_id"] == str(match.public_id)
    assert content["user_public_id"] == str(user_public_id)
    assert content["reserve"] == ReserveStatus.OUTSIDE
    assert content["pay_url"] is None


async def test_first_assigned_player_outside_then_match_is_re_created_without_it(
    async_client: AsyncClient,
    session: AsyncSession,
    x_api_key_header: dict[str, str],
    monkeypatch: Any,
) -> None:
    match = await MatchService().create_match(
        session,
        MatchCreate(
            business_public_id=uuid.uuid4(),
            court_public_id=uuid.uuid4(),
            court_name="Cancha 1",
            date="2025-04-05",
            time=8,
        ),
    )
    match_public_id = match.public_id
    # === PRE ===
    # Create one player ASSIGNED (future OUTSIDE)
    orig_assigned_uuid = uuid.uuid4()
    await MatchPlayerService().create_match_player(
        session,
        MatchPlayerCreate(
            match_public_id=match_public_id,
            user_public_id=orig_assigned_uuid,
            distance=0.0,
            reserve=ReserveStatus.ASSIGNED,
        ),
    )

    # Create some players SIMILAR
    orig_similar_uuids = [uuid.uuid4() for _ in range(6)]
    for distance, similar_uuid in enumerate(orig_similar_uuids):
        await MatchPlayerService().create_match_player(
            session,
            MatchPlayerCreate(
                match_public_id=match_public_id,
                user_public_id=similar_uuid,
                distance=distance,
                reserve=ReserveStatus.SIMILAR,
            ),
        )

    # Prepare new player to be ASSIGNED
    new_assigned_player = Player(
        user_public_id=orig_similar_uuids[0],
        latitude=0.0,
        longitude=0.0,
        time_availability=1,
    )

    # Prepare some new player to be SIMILAR
    new_similar_players = []
    for orig_similar_uuid in orig_similar_uuids[1:]:
        new_similar_players.append(
            Player(
                user_public_id=orig_similar_uuid,
                latitude=0.0,
                longitude=0.0,
                time_availability=1,
            )
        )

    async def mock_get_players_by_filters(
        _self: Any,
        player_filters: PlayerFilters,
        _exclude_uuids: list[uuid.UUID] | None,
    ) -> list[Player]:
        if player_filters.user_public_id:
            return new_similar_players
        return [new_assigned_player] + new_similar_players

    monkeypatch.setattr(
        PlayersService, "get_players_by_filters", mock_get_players_by_filters
    )

    async def mock_get_available_time(
        _self: Any,
        business_public_id: uuid.UUID,
        court_name: str,
        date: date,
        time: int,
    ) -> AvailableTime:
        assert business_public_id == match.business_public_id
        assert court_name == match.court_name
        assert date == match.date
        assert time == match.time
        return AvailableTime(
            business_public_id=match.business_public_id,
            court_public_id=match.court_public_id,
            court_name=match.court_name,
            latitude=0.0,
            longitude=0.0,
            date=match.date,
            time=match.time,
            is_reserved=False,
        )

    monkeypatch.setattr(BusinessService, "get_available_time", mock_get_available_time)

    # === Action ===
    # Update player ASSIGNED -> OUTSIDE
    await async_client.patch(
        f"{test_settings.API_V1_STR}/matches/{match_public_id}/players/{orig_assigned_uuid}/",
        headers=x_api_key_header,
        json={"reserve": ReserveStatus.OUTSIDE},
    )

    # === POST ===
    # The re-generated match keeps same base data
    new_match = await MatchService().get_match(session, match_public_id)
    assert new_match.court_name == match.court_name
    assert new_match.court_public_id == match.court_public_id
    assert new_match.time == match.time
    assert new_match.date == match.date

    new_match_players = await MatchPlayerService().get_match_players(
        session, match_public_id=match_public_id
    )

    # Verify original player OUTSIDE
    new_outside_players_uuids = [
        player.user_public_id
        for player in new_match_players
        if player.reserve == ReserveStatus.OUTSIDE
    ]
    assert len(new_outside_players_uuids) == 1
    assert new_outside_players_uuids[0] == orig_assigned_uuid

    # Verify new ASSIGNED
    new_assigned_players_uuids = [
        player.user_public_id
        for player in new_match_players
        if player.reserve == ReserveStatus.ASSIGNED
    ]
    assert len(new_assigned_players_uuids) == 1
    assert new_assigned_player.user_public_id == new_assigned_player.user_public_id

    # Verify new SIMILAR exists only
    new_similar_players_uuids = [
        player.user_public_id
        for player in new_match_players
        if player.reserve == ReserveStatus.SIMILAR
    ]
    assert len(new_similar_players_uuids) == len(new_similar_players)
    for new_similar_player in new_similar_players:
        assert new_similar_player.user_public_id in new_similar_players_uuids
