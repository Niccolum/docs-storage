import io
from pathlib import Path
from typing import BinaryIO

from PIL import Image

from backend.storage.constants import PDF_THUMBNAIL, THUMBNAIL_SIZE, SupportedFileTypes


def get_thumbnail(*, name: str, file_: BinaryIO) -> io.BytesIO:
    raw_file_type = Path(name).suffix.lstrip(".").lower()
    file_type = SupportedFileTypes(raw_file_type)

    output_file = io.BytesIO()

    if file_type == SupportedFileTypes.PDF:
        with PDF_THUMBNAIL.open("rb") as f:
            output_file = io.BytesIO(f.read())

    elif file_type in [SupportedFileTypes.JPEG, SupportedFileTypes.JPG, SupportedFileTypes.PNG]:
        file_to_open = file_
        format_ = "PNG" if file_type == SupportedFileTypes.PNG else "JPEG"

        image = Image.open(file_to_open)
        image.thumbnail(THUMBNAIL_SIZE)
        image.save(output_file, format=format_)
    else:
        raise

    _ = output_file.seek(0)
    return output_file


if __name__ == "__main__":
    file_ = get_thumbnail(name="example.pdf", file_=io.BytesIO())

    output_path = PDF_THUMBNAIL.parent / "pdf-thumbnail.png"
    with output_path.open("wb") as f:
        _ = f.write(file_.getbuffer())
