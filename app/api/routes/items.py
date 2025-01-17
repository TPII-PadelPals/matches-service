import uuid
from typing import Any

from fastapi import APIRouter, Depends, status

from app.models.item import ItemCreate, ItemPublic, ItemsPublic, ItemUpdate
from app.models.message import Message
from app.repository.items_repository import ItemsRepository
from app.utilities.dependencies import SessionDep, get_user_id_param
from app.utilities.messages import ITEM_RESPONSES, NOT_ENOUGH_PERMISSIONS

router = APIRouter()


@router.get(
    "/",
    response_model=ItemsPublic,
    status_code=status.HTTP_200_OK,
    responses={**NOT_ENOUGH_PERMISSIONS},  # type: ignore[dict-item]
    dependencies=[Depends(get_user_id_param)],
)
async def read_items(
    session: SessionDep, user_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve items.
    """
    repo = ItemsRepository(session)
    items, count = await repo.get_items(user_id, skip, limit)
    return ItemsPublic(data=items, count=count)


@router.get(
    "/{id}",
    response_model=ItemPublic,
    status_code=status.HTTP_200_OK,
    responses={**ITEM_RESPONSES},  # type: ignore[dict-item]
    dependencies=[Depends(get_user_id_param)],
)
async def read_item(session: SessionDep, user_id: uuid.UUID, id: uuid.UUID) -> Any:
    """
    Get item by ID.
    """
    repo = ItemsRepository(session)
    item = await repo.get_item(user_id, id)
    return item


@router.post(
    "/",
    response_model=ItemPublic,
    status_code=status.HTTP_201_CREATED,
    responses={**NOT_ENOUGH_PERMISSIONS},  # type: ignore[dict-item]
    dependencies=[Depends(get_user_id_param)],
)
async def create_item(
    *, session: SessionDep, user_id: uuid.UUID, item_in: ItemCreate
) -> Any:
    """
    Create new item.
    """
    repo = ItemsRepository(session)
    item = await repo.create_item(user_id, item_in)
    return item


@router.put(
    "/{id}",
    response_model=ItemPublic,
    status_code=status.HTTP_200_OK,
    responses={**ITEM_RESPONSES},  # type: ignore[dict-item]
    dependencies=[Depends(get_user_id_param)],
)
async def update_item(
    *,
    session: SessionDep,
    user_id: uuid.UUID,
    id: uuid.UUID,
    item_in: ItemUpdate,
) -> Any:
    """
    Update an item.
    """
    repo = ItemsRepository(session)
    item = await repo.update_item(user_id, id, item_in)
    return item


@router.delete(
    "/{id}",
    status_code=status.HTTP_200_OK,
    responses={**ITEM_RESPONSES},  # type: ignore[dict-item]
    dependencies=[Depends(get_user_id_param)],
)
async def delete_item(
    session: SessionDep, user_id: uuid.UUID, id: uuid.UUID
) -> Message:
    """
    Delete an item.
    """
    repo = ItemsRepository(session)
    await repo.delete_item(user_id, id)
    return Message(message="Item deleted successfully")
