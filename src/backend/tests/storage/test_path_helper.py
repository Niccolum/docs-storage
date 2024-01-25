import pytest

from backend.storage.constants import SupportedFileTypes
from backend.storage.path_helper import get_file_type


class TestGetFileType:
    @pytest.mark.parametrize(("name", "exc_msg"), [
        ("no_extension", '"" is not a valid file type'),
        ("file.txt",  '"txt" is not a valid file type'),
        ("foo.dir", '"dir" is not a valid file type'),
    ])
    def test_unsupported_file_ext(self, name: str, exc_msg: str):
        with pytest.raises(ValueError, match=exc_msg):
            _ = get_file_type(name)

    @pytest.mark.parametrize(("name", "file_type"), [
        ("foo.jpeg", SupportedFileTypes.JPEG),
        ("foo.jpg", SupportedFileTypes.JPG),
        ("foo.png", SupportedFileTypes.PNG),
        ("foo.pdf", SupportedFileTypes.PDF),
        ("foo.ext.pdf", SupportedFileTypes.PDF),
    ])
    def test_success(self, name: str, file_type: SupportedFileTypes):
        assert get_file_type(name) == file_type
