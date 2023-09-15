from pydantic_settings import BaseSettings

from backend.core.constants import __version__


class CommonSettings(BaseSettings):
    app_name: str = "docs"
    description: str = "Docs microservice"
    version: str = __version__
    app_port: int
