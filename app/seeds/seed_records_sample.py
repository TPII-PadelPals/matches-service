import uuid
from typing import Any

from app.models.item import Item

RECORDS: list[Any] = [
    Item(
        title=f"Item {i} title",
        description=f"Item {i} description",
        owner_id=uuid.uuid4(),
    )
    for i in range(10)
]
