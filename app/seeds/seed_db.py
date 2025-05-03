import asyncio

from sqlmodel.ext.asyncio.session import AsyncSession

import app.core.db as db
from app.seeds.seed_config import RECORDS


async def seed_db() -> None:
    print("Restarting DB ...", end=" ")
    await db.restart_db()
    print("Ok")

    print("Initing DB ...", end=" ")
    await db.init_db()
    print("Ok")

    print("Loading Seed ...", end=" ")
    if RECORDS:
        engine = db.get_async_engine()
        async with AsyncSession(engine, expire_on_commit=True) as _session:
            _session.add_all(RECORDS)
            await _session.commit()
        print("Ok")
    else:
        print("Empty")


if __name__ == "__main__":
    asyncio.run(seed_db())
