from pydantic import BaseSettings

from backend.settings.base import __version__


class CommonSettings(BaseSettings):
    app_name: str = "docs"
    description: str = "Docs microservice"
    version: str = __version__
    app_port: int = 8080
