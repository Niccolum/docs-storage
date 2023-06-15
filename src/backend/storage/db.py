from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from functools import cache
from typing import TYPE_CHECKING

from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine

from backend.core.settings import get_settings

if TYPE_CHECKING:
    from odmantic.session import AIOSession


async def get_session() -> AsyncGenerator["AIOSession", None]:
    engine = get_engine()

    async with engine.session() as session:
        yield session

get_session_context_manager = asynccontextmanager(get_session)


@cache
def get_engine() -> AIOEngine:
    settings = get_settings()

    client = AsyncIOMotorClient(settings.mongo.dsn)
    engine = AIOEngine(client=client, database=settings.mongo.database)
    return engine
