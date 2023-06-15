from inspect import getmembers, isclass

from backend.storage import mongo_schemas
from backend.storage.db import get_engine


async def init_mongo_models() -> None:
    engine = get_engine()
    models = dict(getmembers(mongo_schemas, isclass)).values()
    await engine.configure_database(models)
