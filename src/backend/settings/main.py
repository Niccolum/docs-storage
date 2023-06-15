from functools import lru_cache
from typing import Any

from pydantic import (
    AnyHttpUrl,  # pyright: ignore reportUnknownVariableType
    validator,
)

from backend.settings.base import SettingsConfigMixin

from .common import CommonSettings
from .security import WebSecureSettings


class Settings(CommonSettings):
    security: WebSecureSettings = WebSecureSettings()

    @validator("security", pre=True)
    @classmethod
    def cors_allow_origins_builder(cls, security_settings: WebSecureSettings, values: dict[str, Any]) -> dict[str, Any]:
        result: list[AnyHttpUrl] = []
        port = values["app_port"]
        scheme = "https" if security_settings.https else "http"

        for raw_host in security_settings.cors_hosts:
            host_url = AnyHttpUrl(host=raw_host, port=port, scheme=scheme)
            values.append(host_url)

        security_settings.cors_allow_origins = result
        return security_settings

    class Config(SettingsConfigMixin):
        env_prefix = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
