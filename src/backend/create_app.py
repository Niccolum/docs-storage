import logging

from fastapi import FastAPI

from backend.api.router import api_router
from backend.middlewares import set_middlewares
from backend.settings.base import get_settings
from backend.settings.log import logging_setup

logger = logging.getLogger(__name__)


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
    )
    set_middlewares(app, settings)
    app.include_router(api_router)
    return app
