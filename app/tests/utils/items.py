import uuid

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.item import Item, ItemCreate
from app.tests.utils.utils import random_lower_string


async def create_random_item(user_id: uuid.UUID, db: AsyncSession) -> Item:
    assert user_id is not None
    title = random_lower_string()
    description = random_lower_string()
    item_in = ItemCreate(title=title, description=description)
    db_item = Item.model_validate(item_in, update={"owner_id": user_id})
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item
