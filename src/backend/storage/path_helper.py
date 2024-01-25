import pathlib

from backend.storage.constants import SupportedFileTypes


def get_file_type(name: str) -> SupportedFileTypes:
    raw_file_type = pathlib.Path(name).suffix.lstrip(".").lower()
    exc_msg = f'"{raw_file_type}" is not a valid file type'

    if raw_file_type == SupportedFileTypes.DIR.value:
        raise ValueError(exc_msg)
    try:
        return SupportedFileTypes(raw_file_type)
    except ValueError as exc:
        raise ValueError(exc_msg) from exc
