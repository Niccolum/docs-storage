from pydantic import (
    BaseSettings,  # pyright: ignore reportUnknownVariableType
)

from backend.settings import __version__


class CommonSettings(BaseSettings):
    app_name: str = "docs"
    description: str = "Docs microservice"
    version: str = __version__
    raw_app_port: int = 8080
    raw_app_hosts: list[str] = []

    https: bool = False

    trusted_hosts: list[str]
    www_redirect: bool = False
