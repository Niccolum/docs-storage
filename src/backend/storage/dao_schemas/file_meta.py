import datetime as dt
import io

from bson.binary import Binary
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
)

from backend.storage.constants import SupportedFileTypes
from backend.storage.typing_ import FileName, FilePath


class FileMetaDAOSchema(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    path: FilePath
    filename: FileName
    type_: SupportedFileTypes
    icon: io.BytesIO | None = None
    nonce: bytes
    created_date: dt.datetime = Field(default_factory=dt.datetime.utcnow)
    updated_date: dt.datetime | None = None

    @field_validator("type_")
    @classmethod
    def check_type_(cls, v: SupportedFileTypes) -> SupportedFileTypes:
        if v == SupportedFileTypes.DIR:
            msg = "Unsupported type_. Use DirMetaDAOSchema instead"
            raise ValueError(msg)
        return v

    @field_serializer("icon")
    def serialize_icon(self, icon: io.BytesIO | None) -> bytes | None:
        return icon.read() if icon else None

    @field_validator("icon", mode="before")
    @classmethod
    def validate_icon(cls, icon: Binary | bytes | io.BytesIO | None) -> io.BytesIO | None:
        return io.BytesIO(icon) if isinstance(icon, (Binary, bytes)) else icon


class DirMetaDAOSchema(BaseModel):
    path: FilePath
    filename: FileName
    type_: SupportedFileTypes
    icon: None = None
    created_date: dt.datetime = Field(default_factory=dt.datetime.utcnow)
    updated_date: dt.datetime | None = None

    @field_validator("type_")
    @classmethod
    def check_type_(cls, v: SupportedFileTypes) -> SupportedFileTypes:
        if v != SupportedFileTypes.DIR:
            msg = "Unsupported type_. Use FileMetaDAOSchema instead"
            raise ValueError(msg)
        return v
