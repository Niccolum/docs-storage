import datetime as dt
from typing import Annotated, Any, ClassVar

import pymongo
from beanie import (
    Document,
    Indexed,  # pyright: ignore reportUnknownVariableType
    Insert,
    Replace,
    SaveChanges,
    Update,
    before_event,
)
from beanie.odm.custom_types.bson.binary import BsonBinary
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
        dt.datetime | None,
        Indexed(index_type=pymongo.DESCENDING),
    ] = None
    updated_date: dt.datetime | None = None

    @before_event(Replace, SaveChanges, Update)
    def set_updated_date(self) -> None:
        self.updated_date = dt.datetime.now(tz=dt.timezone.utc).replace(microsecond=0)

    @before_event(Insert)
    def set_created_date(self) -> None:
        self.created_date = dt.datetime.now(tz=dt.timezone.utc).replace(microsecond=0)

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

        bson_encoders: ClassVar[dict[Any, Any]] = {
            dt.datetime: lambda x: x.isoformat(sep=" ", timespec="seconds") if x else None,
        }
