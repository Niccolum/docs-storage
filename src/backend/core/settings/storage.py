import pathlib

from pydantic_settings import BaseSettings


class StorageSettings(BaseSettings):
    storage_path: pathlib.Path
