from functools import lru_cache

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from backend.core.settings import get_settings


async def setup_mongo() -> None:
    client = get_mongo_client()
    await init_beanie(
        database=client.db_name,
        document_models=[
            "backend.storage.documents.file_meta.FileMetaDocument",
        ],
    )


async def teardown_mongo() -> None:
    client = get_mongo_client()
    client.close()
    get_mongo_client.cache_clear()


@lru_cache
def get_mongo_client() -> AsyncIOMotorClient:
    settings = get_settings()

    return AsyncIOMotorClient(str(settings.mongo.dsn), tz_aware=True)
