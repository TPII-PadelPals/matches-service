from typing import Any

from fastapi import APIRouter, status

from app.services.items_service import ItemsService

router = APIRouter()


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
)
async def call_items_service() -> Any:
    """
    Retrieve service items.
    """
    service = ItemsService()
    response = await service.get_items()
    return response
