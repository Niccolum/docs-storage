

from pydantic import BaseSettings, MongoDsn
from pydantic_computed import Computed, computed

from .base import SettingsConfigMixin


class MongoSettings(BaseSettings):
    username: str
    password: str
    database: str
    host: str

    dsn: Computed[MongoDsn]

    @computed("dsn")
    @staticmethod
    def assemble_mongo_connection(username: str, password: str, host: str, **_: str) -> list[str]:
        return MongoDsn.build(
            scheme="mongodb",
            user=username,
            password=password,
            host=host,
        )

    class Config(SettingsConfigMixin):
        env_prefix = "MONGO_"
