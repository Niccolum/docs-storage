import io
from typing import BinaryIO

from PIL import Image

from backend.storage.constants import PDF_THUMBNAIL, THUMBNAIL_SIZE, SupportedFileTypes


def get_thumbnail(*, file_type: SupportedFileTypes, file_: BinaryIO | None = None) -> io.BytesIO:
    output_file = io.BytesIO()

    if file_type == SupportedFileTypes.PDF:
        with PDF_THUMBNAIL.open("rb") as f:
            output_file = io.BytesIO(f.read())

    elif file_type in [SupportedFileTypes.JPEG, SupportedFileTypes.JPG, SupportedFileTypes.PNG] and file_:
        image = Image.open(file_)
        image.thumbnail(THUMBNAIL_SIZE)
        image.save(output_file, format="PNG")

        _ = file_.seek(0)
    else:
        raise ValueError("Invalid file type")

    _ = output_file.seek(0)
    return output_file
