from pydantic import MongoDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .base import env_file


class MongoSettings(BaseSettings):
    username: str
    password: str
    database: str
    host: str

    model_config = SettingsConfigDict(env_prefix="MONGO_", env_file=env_file, extra="allow")

    @computed_field
    def dsn(self) -> MongoDsn:
        return MongoDsn.build(
            scheme="mongodb",
            username=self.username,
            password=self.password,
            host=self.host,
        )
