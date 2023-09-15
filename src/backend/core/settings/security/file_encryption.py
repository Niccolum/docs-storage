from pydantic import Field
from pydantic_settings import BaseSettings


class FileEncryptionSettings(BaseSettings):
    aes_key: bytes = Field(min_length=32, max_length=32)
