import enum
import pathlib


class SupportedFileTypes(str, enum.Enum):
    DIR = "dir"
    JPEG = "jpeg"
    JPG = "jpg"
    PNG = "png"
    PDF = "pdf"


THUMBNAIL_SIZE = (128, 128)
STATIC_DIR = pathlib.Path(__file__).parent / "static"
PDF_THUMBNAIL = STATIC_DIR / "pdf-icon-128.png"
