import datetime as dt
import pathlib
from collections.abc import Generator

from odmantic import Field, Index, Model
from odmantic.query import desc

from backend.storage.constants import SupportedFileTypes


class FileMeta(Model):
    path: pathlib.Path
    filename: str = Field(index=True)
    type_: SupportedFileTypes
    created_date: dt.datetime = Field(default_factory=dt.datetime.utcnow)

    class Config:
        collection = "files"
        parse_doc_with_default_factories = True

        @staticmethod
        def indexes() -> Generator[Index, None, None]:
            yield Index(desc(FileMeta.created_date),  name="latest_date_index")
