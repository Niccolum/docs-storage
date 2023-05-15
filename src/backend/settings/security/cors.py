from pydantic import (
    AnyHttpUrl,  # pyright: ignore reportUnknownVariableType
    BaseSettings,
)


class CorsSettings(BaseSettings):
    cors_allow_origins: list[AnyHttpUrl] = []
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]
