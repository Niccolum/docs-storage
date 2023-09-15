
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from backend.core.settings import get_settings


async def setup_mongo() -> None:
    settings = get_settings()

    client = AsyncIOMotorClient(str(settings.mongo.dsn))
    await init_beanie(
        database=client.db_name,
        document_models=[
            "backend.storage.mongo_schemas.file_meta.FileMeta",  # pyright: ignore reportUnknownArgumentType
        ],
    )
