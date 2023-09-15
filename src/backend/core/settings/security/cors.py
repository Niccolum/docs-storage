from typing import ClassVar

from pydantic_settings import BaseSettings


class CorsSettings(BaseSettings):
    cors_allow_credentials: bool = True
    cors_allow_methods: ClassVar[list[str]] = ["*"]
    cors_allow_headers: ClassVar[list[str]] = ["*"]

    cors_hosts: ClassVar[list[str]] = []
