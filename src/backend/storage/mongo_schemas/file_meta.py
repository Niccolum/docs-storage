import datetime as dt
import pathlib

import pymongo
from beanie import Document, Indexed  # pyright: ignore reportUnknownVariableType
from pydantic import Field

from backend.storage.constants import SupportedFileTypes


class FileMeta(Document):
    path: pathlib.Path
    filename: Indexed(str) # pyright: ignore reportUnknownVariableType
    type_: SupportedFileTypes
    icon: bytes
    created_date: Indexed(  # pyright: ignore reportUnknownVariableType
        dt.datetime, pymongo.DESCENDING) = Field(default_factory=dt.datetime.utcnow)

    class Settings:
        name = "files"
