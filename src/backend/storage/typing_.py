from pathlib import Path
from typing import NotRequired, TypeAlias, TypedDict

FileName: TypeAlias = str
FilePath: TypeAlias = Path


class OptionalFileAttributes(TypedDict):
    filename: NotRequired[FileName]
    path: NotRequired[FilePath]
