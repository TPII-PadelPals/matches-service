import uuid

from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.tests.utils.items import create_random_item


async def test_create_item(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    user_id = uuid.uuid4()
    data = {"title": "itemTitle", "description": "itemDescription"}
    response = await async_client.post(
        f"{settings.API_V1_STR}/items/",
        headers=x_api_key_header,
        json=data,
        params={"user_id": str(user_id)},
    )
    assert response.status_code == 201
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert "id" in content
    assert "owner_id" in content


async def test_read_item(
    async_client: AsyncClient, x_api_key_header: dict[str, str], session: AsyncSession
) -> None:
    user_id = uuid.uuid4()
    item = await create_random_item(user_id, session)
    response = await async_client.get(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=x_api_key_header,
        params={"user_id": str(user_id)},
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == item.title
    assert content["description"] == item.description
    assert content["id"] == str(item.id)
    assert content["owner_id"] == str(item.owner_id)


async def test_read_item_not_found(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    user_id = uuid.uuid4()
    response = await async_client.get(
        f"{settings.API_V1_STR}/items/{uuid.uuid4()}",
        headers=x_api_key_header,
        params={"user_id": str(user_id)},
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Item not found"


async def test_read_item_not_authorized(
    async_client: AsyncClient, session: AsyncSession
) -> None:
    user_id = uuid.uuid4()
    item = await create_random_item(user_id, session)
    response = await async_client.get(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers={"x-api-key": "wrong-key"},
        params={"user_id": str(user_id)},
    )
    assert response.status_code == 401
    content = response.json()
    assert content["detail"] == "Not Authorized"


async def test_read_item_not_enough_permissions(
    async_client: AsyncClient, x_api_key_header: dict[str, str], session: AsyncSession
) -> None:
    user_id = uuid.uuid4()
    item = await create_random_item(user_id, session)
    response = await async_client.get(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=x_api_key_header,
        params={"user_id": str(uuid.uuid4())},
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"


async def test_read_item_not_owner(
    async_client: AsyncClient, x_api_key_header: dict[str, str], session: AsyncSession
) -> None:
    user_id = uuid.uuid4()
    item = await create_random_item(user_id, session)
    user_id_2 = uuid.uuid4()
    response = await async_client.get(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=x_api_key_header,
        params={"user_id": str(user_id_2)},
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"


async def test_read_items(
    async_client: AsyncClient, x_api_key_header: dict[str, str], session: AsyncSession
) -> None:
    user_id = uuid.uuid4()
    await create_random_item(user_id, session)
    await create_random_item(user_id, session)
    response = await async_client.get(
        f"{settings.API_V1_STR}/items/",
        headers=x_api_key_header,
        params={"user_id": str(user_id)},
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["data"]) >= 2
    assert content["count"] >= 2


async def test_update_item(
    async_client: AsyncClient, x_api_key_header: dict[str, str], session: AsyncSession
) -> None:
    user_id = uuid.uuid4()
    item = await create_random_item(user_id, session)
    data = {"title": "Updated title", "description": "Updated description"}
    response = await async_client.put(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=x_api_key_header,
        json=data,
        params={"user_id": str(user_id)},
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert content["id"] == str(item.id)
    assert content["owner_id"] == str(item.owner_id)


async def test_update_item_not_found(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    user_id = uuid.uuid4()
    data = {"title": "Updated title", "description": "Updated description"}
    response = await async_client.put(
        f"{settings.API_V1_STR}/items/{uuid.uuid4()}",
        headers=x_api_key_header,
        json=data,
        params={"user_id": str(user_id)},
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Item not found"


async def test_update_item_not_enough_permissions(
    async_client: AsyncClient, x_api_key_header: dict[str, str], session: AsyncSession
) -> None:
    user_id = uuid.uuid4()
    item = await create_random_item(user_id, session)
    data = {"title": "Updated title", "description": "Updated description"}
    response = await async_client.put(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=x_api_key_header,
        json=data,
        params={"user_id": str(uuid.uuid4())},
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"


async def test_update_item_not_owner(
    async_client: AsyncClient, x_api_key_header: dict[str, str], session: AsyncSession
) -> None:
    user_id = uuid.uuid4()
    item = await create_random_item(user_id, session)
    user_id_2 = uuid.uuid4()
    data = {"title": "Updated title", "description": "Updated description"}
    response = await async_client.put(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=x_api_key_header,
        json=data,
        params={"user_id": str(user_id_2)},
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"


async def test_delete_item(
    async_client: AsyncClient, x_api_key_header: dict[str, str], session: AsyncSession
) -> None:
    user_id = uuid.uuid4()
    item = await create_random_item(user_id, session)
    response = await async_client.delete(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=x_api_key_header,
        params={"user_id": str(user_id)},
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "Item deleted successfully"


async def test_delete_item_not_found(
    async_client: AsyncClient, x_api_key_header: dict[str, str]
) -> None:
    user_id = uuid.uuid4()
    response = await async_client.delete(
        f"{settings.API_V1_STR}/items/{uuid.uuid4()}",
        headers=x_api_key_header,
        params={"user_id": str(user_id)},
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Item not found"


async def test_delete_item_not_enough_permissions(
    async_client: AsyncClient, x_api_key_header: dict[str, str], session: AsyncSession
) -> None:
    user_id = uuid.uuid4()
    item = await create_random_item(user_id, session)
    response = await async_client.delete(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=x_api_key_header,
        params={"user_id": str(uuid.uuid4())},
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"


async def test_delete_item_not_owner(
    async_client: AsyncClient, x_api_key_header: dict[str, str], session: AsyncSession
) -> None:
    user_id = uuid.uuid4()
    item = await create_random_item(user_id, session)
    user_id_2 = uuid.uuid4()
    response = await async_client.delete(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=x_api_key_header,
        params={"user_id": str(user_id_2)},
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"
