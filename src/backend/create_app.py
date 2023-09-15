import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.core.api.router import api_router
from backend.core.logging_config import logging_setup
from backend.core.middlewares import set_middlewares
from backend.core.settings import get_settings
from backend.storage.events import setup_mongo

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await setup_mongo()
    yield

def create_app() -> FastAPI:
    logging_setup()
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        description=settings.description,
        version=settings.version,
        externalDocs={
            "description": "See more docs about project",
            "url": "http://example.com",
        },
        redoc_url=None,
        lifespan=lifespan,
    )
    set_middlewares(app, settings)
    app.include_router(api_router)
    return app
