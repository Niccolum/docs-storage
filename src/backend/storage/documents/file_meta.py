import datetime as dt
from typing import Annotated, ClassVar

import pymongo
from beanie import Document, Indexed  # pyright: ignore reportUnknownVariableType
from beanie.odm.custom_types.bson.binary import BsonBinary
from pydantic import Field
from pymongo import IndexModel

from backend.storage.constants import SupportedFileTypes
from backend.storage.typing_ import FileName, FilePath


class FileMetaDocument(Document):
    path: FilePath
    filename: Annotated[FileName, Indexed()]
    type_: SupportedFileTypes
    icon: BsonBinary | None
    nonce: bytes | None = None
    created_date: Annotated[
        dt.datetime,
        Indexed(dt.datetime, pymongo.DESCENDING),
    ] = Field(default_factory=dt.datetime.utcnow)

    class Settings:
        name = "files"
        validate_on_save = True

        indexes: ClassVar[list[IndexModel]] = [
            IndexModel(
                keys=[("path", pymongo.ASCENDING), ("filename", pymongo.ASCENDING)],
                name="unique file path",
                unique=False,
            ),
        ]
