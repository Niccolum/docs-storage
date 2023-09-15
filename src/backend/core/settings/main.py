from functools import lru_cache

from pydantic_settings import SettingsConfigDict

from .base import env_file
from .common import CommonSettings
from .mongo import MongoSettings
from .security import WebSecureSettings


class Settings(CommonSettings):
    security: WebSecureSettings = WebSecureSettings()  # pyright: ignore reportGeneralTypeIssues
    mongo: MongoSettings = MongoSettings() # pyright: ignore reportGeneralTypeIssues

    model_config = SettingsConfigDict(env_prefix="", env_file=env_file, extra="allow")


@lru_cache
def get_settings() -> Settings:
    return Settings()  # pyright: ignore reportGeneralTypeIssues
