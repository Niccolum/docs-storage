import filecmp
import io
import tempfile
from typing import BinaryIO, Callable

import pytest
from PIL import Image

from backend.storage.constants import PDF_THUMBNAIL, SupportedFileTypes
from backend.storage.icon import get_thumbnail


class TestGetThumbnail:
    def test_unsupported_file_type(self):
        with pytest.raises(ValueError, match="Invalid file type"):
            _ = get_thumbnail(file_type=SupportedFileTypes.DIR, file_=io.BytesIO())

    @pytest.mark.parametrize(
        "file_type",
        [
            SupportedFileTypes.JPEG,
            SupportedFileTypes.JPG,
            SupportedFileTypes.PNG,
        ],
    )
    def test_no_file_for_images(self, file_type: SupportedFileTypes):
        with pytest.raises(ValueError, match="Invalid file type"):
            _ = get_thumbnail(file_type=file_type)

    def test_pdf_success(self):
        file_type = SupportedFileTypes.PDF

        data = get_thumbnail(file_type=file_type)

        with tempfile.NamedTemporaryFile(buffering=0) as fp:
            _ = fp.write(data.read())

            img = Image.open(data)
            assert img.format == "PNG"

            assert filecmp.cmp(PDF_THUMBNAIL, fp.name, shallow=False)

    @pytest.mark.parametrize(
        ("file_type", "image_format"),
        [
            (SupportedFileTypes.JPEG, "JPEG"),
            (SupportedFileTypes.JPG, "JPEG"),
            (SupportedFileTypes.PNG, "PNG"),
        ],
    )
    def test_images_success(
        self,
        file_type: SupportedFileTypes,
        image_format: str,
        generate_image: Callable[[str], BinaryIO],
    ):
        file_ = generate_image(image_format)

        data = get_thumbnail(file_type=file_type, file_=file_)

        assert data.tell() == 0
        assert file_.tell() == 0

        img = Image.open(data)
        assert img.format == "PNG"
