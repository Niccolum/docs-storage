from functools import lru_cache
from typing import Any

from pydantic import (
    AnyHttpUrl,
    BaseSettings,
    root_validator,  # pyright: ignore reportUnknownVariableType
)

from backend.settings import ENVIRONMENT, PROJECT_DIR

from .common import CommonSettings
from .security import WebSecureSettings


class Settings(CommonSettings, WebSecureSettings):
    @root_validator
    @classmethod
    def cors_allow_origins_builder(cls, values: dict[str, Any]) -> dict[str, Any]:
        result: list[AnyHttpUrl] = []
        port = values["raw_app_port"]
        scheme = "https" if values["https"] else "http"

        for raw_host in values["raw_app_hosts"]:
            host_url = AnyHttpUrl(url=f"{scheme}://{raw_host}:{port}", scheme=scheme)
            result.append(host_url)

        values["cors_allow_origins"] = result
        return values

    class Config(BaseSettings.Config):  # pyright: ignore reportIncompatibleVariableOverride
        env_prefix = ""
        env_file = [  # pyright: ignore reportUnknownVariableType
            PROJECT_DIR / "env" / ENVIRONMENT.value / "public.env",
            PROJECT_DIR / "env" / ENVIRONMENT.value / ".secret.env",
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()  # pyright: ignore reportGeneralTypeIssues
