import uuid
from collections.abc import Sequence

from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.item import Item, ItemCreate, ItemUpdate
from app.utilities.exceptions import NotEnoughPermissionsException, NotFoundException


class ItemsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_items(
        self, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> tuple[Sequence[Item], int]:
        count_statement = (
            select(func.count()).select_from(Item).where(Item.owner_id == user_id)
        )
        count = (await self.session.exec(count_statement)).one()
        statement = (
            select(Item).where(Item.owner_id == user_id).offset(skip).limit(limit)
        )
        items = (await self.session.exec(statement)).all()
        return items, count

    async def get_item(self, user_id: uuid.UUID, id: uuid.UUID) -> Item:
        item = await self.session.get(Item, id)
        if not item:
            raise NotFoundException(item="Item")
        if item.owner_id != user_id:
            raise NotEnoughPermissionsException()
        return item

    async def create_item(self, user_id: uuid.UUID, item_in: ItemCreate) -> Item:
        item = Item.model_validate(item_in, update={"owner_id": user_id})
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def update_item(
        self, user_id: uuid.UUID, id: uuid.UUID, item_in: ItemUpdate
    ) -> Item:
        item = await self.session.get(Item, id)
        if not item:
            raise NotFoundException(item="Item")
        if item.owner_id != user_id:
            raise NotEnoughPermissionsException()
        update_dict = item_in.model_dump(exclude_unset=True)
        item.sqlmodel_update(update_dict)
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def delete_item(self, user_id: uuid.UUID, id: uuid.UUID) -> None:
        item = await self.session.get(Item, id)
        if not item:
            raise NotFoundException(item="Item")
        if item.owner_id != user_id:
            raise NotEnoughPermissionsException()
        await self.session.delete(item)
        await self.session.commit()
