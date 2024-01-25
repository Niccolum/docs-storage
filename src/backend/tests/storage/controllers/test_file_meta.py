import io
import tempfile
from typing import TYPE_CHECKING, Awaitable, Callable, cast

import pytest
from PIL import UnidentifiedImageError

from backend.storage.constants import SupportedFileTypes
from backend.storage.documents.file_meta import FileMetaDocument
from backend.storage.encryption import encrypt
from backend.storage.typing_ import FileName, FilePath

if TYPE_CHECKING:
    from bson.binary import Binary

    from backend.storage.controllers.file_meta import FileMetaController


class TestCreateFile:
    async def test_incorrect_file_type(self, file_meta_controller_factory: Callable[..., "FileMetaController"]):
        controller = file_meta_controller_factory()

        with pytest.raises(ValueError, match='"bar" is not a valid file type'):
            await controller.create_file(
                filename=FileName("foo.bar"),
                path=FilePath("baz"),
                data=io.BytesIO(),
                replace=False,
            )

    async def test_unsupported_file_type(self, file_meta_controller_factory: Callable[..., "FileMetaController"]):
        controller = file_meta_controller_factory()

        with pytest.raises(ValueError, match='"dir" is not a valid file type'):
            await controller.create_file(
                filename=FileName("foo.dir"),
                path=FilePath("baz"),
                data=io.BytesIO(),
                replace=False,
            )

    @pytest.mark.parametrize(
        "filename",
        [
            FileName("foo.jpg"),
            FileName("foo.jpeg"),
            FileName("foo.png"),
        ],
    )
    async def test_incorrect_file_data(
        self,
        filename: FileName,
        file_meta_controller_factory: Callable[..., "FileMetaController"],
    ):
        controller = file_meta_controller_factory()

        with pytest.raises(UnidentifiedImageError, match="cannot identify image file"):
            await controller.create_file(
                filename=filename,
                path=FilePath("foo"),
                data=io.BytesIO(b"bar"),
                replace=False,
            )

    async def test_already_exists_in_db(
        self,
        file_meta_controller_factory: Callable[..., "FileMetaController"],
        file_meta_document_factory: Callable[..., Awaitable["FileMetaDocument"]],
    ):
        controller = file_meta_controller_factory()

        with tempfile.NamedTemporaryFile(buffering=0, suffix=".pdf", delete=False) as fp:
            _ = fp.write(b"bar")
            raw_path = FilePath(fp.name)
            filename = FileName(raw_path.name)
            path = raw_path.parent

            _ = await file_meta_document_factory(filename=filename, path=path)

            with pytest.raises(FileExistsError, match=f"{fp.name} exists in DB"):
                await controller.create_file(
                    filename=filename,
                    path=path,
                    data=io.BytesIO(b"baz"),
                    replace=False,
                )

            assert not (path / filename).exists()

    @pytest.mark.usefixtures("_init_beanie")
    @pytest.mark.parametrize(
        ("data_format", "suffix"),
        [
            ("PDF", ".pdf"),
            ("JPEG", ".jpg"),
            ("JPEG", ".jpeg"),
            ("PNG", ".png"),
        ],
    )
    async def test_success_without_replace(
        self,
        file_meta_controller_factory: Callable[..., "FileMetaController"],
        generate_image: Callable[[str], io.BytesIO],
        data_format: str,
        suffix: str,
    ):
        controller = file_meta_controller_factory()
        data = generate_image(data_format) if data_format != "PDF" else io.BytesIO(b"bar")

        with tempfile.TemporaryDirectory() as temp_dir_name:
            path = FilePath(temp_dir_name)
            filename = FileName(f"test{suffix}")

            await controller.create_file(
                filename=filename,
                path=path,
                data=data,
                replace=False,
            )

            assert (path / filename).exists()

            object_in_db = await FileMetaDocument.find_one(
                FileMetaDocument.path == path,
                FileMetaDocument.filename == filename,
            )

            assert object_in_db
            assert object_in_db.type_ == SupportedFileTypes(suffix.lstrip("."))
            assert object_in_db.icon is not None
            assert object_in_db.created_date is not None

    @pytest.mark.parametrize("is_exists_in_db", [True, False])
    @pytest.mark.parametrize("is_exists_in_os", [True, False])
    @pytest.mark.parametrize(
        ("data_format", "suffix"),
        [
            ("PDF", ".pdf"),
            ("JPEG", ".jpg"),
            ("JPEG", ".jpeg"),
            ("PNG", ".png"),
        ],
    )
    async def test_success_with_replace(
        self,
        file_meta_controller_factory: Callable[..., "FileMetaController"],
        file_meta_document_factory: Callable[..., Awaitable["FileMetaDocument"]],
        generate_image: Callable[[str], io.BytesIO],
        *,
        is_exists_in_db: bool,
        is_exists_in_os: bool,
        data_format: str,
        suffix: str,
    ):
        controller = file_meta_controller_factory()
        data = generate_image(data_format) if data_format != "PDF" else io.BytesIO(b"bar")

        with tempfile.TemporaryDirectory() as temp_dir_name:
            path = FilePath(temp_dir_name)
            filename = FileName(f"test{suffix}")

            if is_exists_in_os:
                filepath = path / filename
                with filepath.open("wb") as f:
                    _ = f.write(data.read())
                    _ = data.seek(0)

            if is_exists_in_db:
                _ = await file_meta_document_factory(
                    filename=filename,
                    path=path,
                    type_=SupportedFileTypes(suffix.lstrip(".")),
                )

            await controller.create_file(
                filename=filename,
                path=path,
                data=data,
                replace=True,
            )

            assert (path / filename).exists()

            object_in_db = await FileMetaDocument.find_one(
                FileMetaDocument.path == path,
                FileMetaDocument.filename == filename,
            )

            assert object_in_db
            assert object_in_db.type_ == SupportedFileTypes(suffix.lstrip("."))
            assert object_in_db.icon is not None
            assert object_in_db.created_date is not None


class TestDeleteFile:
    @pytest.mark.parametrize("is_exists_in_db", [True, False])
    @pytest.mark.parametrize("is_exists_in_os", [True, False])
    async def test_success(
        self,
        file_meta_controller_factory: Callable[..., "FileMetaController"],
        file_meta_document_factory: Callable[..., Awaitable["FileMetaDocument"]],
        *,
        is_exists_in_db: bool,
        is_exists_in_os: bool,
    ):
        controller = file_meta_controller_factory()
        data = io.BytesIO(b"bar")
        filename = FileName("test.pdf")

        with tempfile.TemporaryDirectory() as temp_dir_name:
            path = FilePath(temp_dir_name)

            if is_exists_in_os:
                filepath = path / filename
                with filepath.open("wb") as f:
                    _ = f.write(data.read())
                    _ = data.seek(0)

            if is_exists_in_db:
                _ = await file_meta_document_factory(
                    filename=filename,
                    path=path,
                    type_=SupportedFileTypes.PDF,
                )

            await controller.delete_file(
                filename=filename,
                path=path,
            )

            assert not (path / filename).exists()

            object_in_db = await FileMetaDocument.find_one(
                FileMetaDocument.path == path,
                FileMetaDocument.filename == filename,
            )

            assert not object_in_db


class TestRenameFile:
    @pytest.mark.parametrize(
        ("is_exists_in_db", "is_exists_in_os"),
        [
            (False, False),
            (True, False),
            (False, True),
        ],
    )
    async def test_not_old_file(
        self,
        file_meta_controller_factory: Callable[..., "FileMetaController"],
        file_meta_document_factory: Callable[..., Awaitable["FileMetaDocument"]],
        *,
        is_exists_in_db: bool,
        is_exists_in_os: bool,
    ):
        controller = file_meta_controller_factory()
        filename = FileName("test.pdf")

        with tempfile.TemporaryDirectory() as temp_dir_name:
            old_path = FilePath(temp_dir_name)

            if is_exists_in_os:
                filepath = old_path / filename
                with filepath.open("wb") as f:
                    _ = f.write(b"foo")

            if is_exists_in_db:
                _ = await file_meta_document_factory(
                    filename=filename,
                    path=old_path,
                    type_=SupportedFileTypes.PDF,
                )

            with pytest.raises(FileNotFoundError, match=f"{old_path / filename} is not exists"):
                await controller.rename_file(
                    old_path=old_path,
                    old_filename=filename,
                    new_path=FilePath("bar"),
                    new_filename=filename,
                )

            assert not (old_path / filename).exists()

        object_in_db = await FileMetaDocument.find_one(
            FileMetaDocument.path == old_path,
            FileMetaDocument.filename == filename,
        )

        assert not object_in_db

    async def test_not_new_path_in_os(
        self,
        file_meta_controller_factory: Callable[..., "FileMetaController"],
        file_meta_document_factory: Callable[..., Awaitable["FileMetaDocument"]],
    ):
        controller = file_meta_controller_factory()
        filename = FileName("test.pdf")

        with tempfile.TemporaryDirectory() as temp_dir_name:
            old_path = FilePath(temp_dir_name)
            new_path = FilePath("bar")

            filepath = old_path / filename
            with filepath.open("wb") as f:
                _ = f.write(b"foo")

            _ = await file_meta_document_factory(
                filename=filename,
                path=old_path,
                type_=SupportedFileTypes.PDF,
            )

            with pytest.raises(FileNotFoundError, match=f"{new_path} not found in OS"):
                await controller.rename_file(
                    old_path=old_path,
                    old_filename=filename,
                    new_path=new_path,
                    new_filename=filename,
                )

            assert (old_path / filename).exists()

        object_in_db = await FileMetaDocument.find_one(
            FileMetaDocument.path == old_path,
            FileMetaDocument.filename == filename,
        )

        assert object_in_db

    async def test_success(
        self,
        file_meta_controller_factory: Callable[..., "FileMetaController"],
        file_meta_document_factory: Callable[..., Awaitable["FileMetaDocument"]],
    ):
        controller = file_meta_controller_factory()
        filename = FileName("test.pdf")

        with tempfile.TemporaryDirectory() as old_raw_path, tempfile.TemporaryDirectory() as new_raw_path:
            old_path = FilePath(old_raw_path)
            new_path = FilePath(new_raw_path)

            filepath = old_path / filename
            with filepath.open("wb") as f:
                _ = f.write(b"foo")

            file_meta_document = await file_meta_document_factory(
                filename=filename,
                path=old_path,
                type_=SupportedFileTypes.PDF,
            )

            await controller.rename_file(
                old_path=old_path,
                old_filename=filename,
                new_path=new_path,
                new_filename=filename,
            )

            assert not (old_path / filename).exists()
            assert (new_path / filename).exists()

        old_object_in_db = await FileMetaDocument.find_one(
            FileMetaDocument.path == old_path,
            FileMetaDocument.filename == filename,
        )

        assert not old_object_in_db

        new_object_in_db = await FileMetaDocument.find_one(
            FileMetaDocument.path == new_path,
            FileMetaDocument.filename == filename,
        )

        assert new_object_in_db
        assert new_object_in_db.type_ == file_meta_document.type_
        assert new_object_in_db.icon == file_meta_document.icon
        assert bytes(cast("Binary", new_object_in_db.nonce)) == file_meta_document.nonce
        assert new_object_in_db.created_date != file_meta_document.created_date


class TestGetFile:
    @pytest.mark.parametrize(
        ("is_exists_in_db", "is_exists_in_os"),
        [
            (False, False),
            (True, False),
            (False, True),
        ],
    )
    async def test_not_exist_file(
        self,
        file_meta_controller_factory: Callable[..., "FileMetaController"],
        file_meta_document_factory: Callable[..., Awaitable["FileMetaDocument"]],
        *,
        is_exists_in_db: bool,
        is_exists_in_os: bool,
    ):
        controller = file_meta_controller_factory()
        filename = FileName("test.pdf")

        with tempfile.TemporaryDirectory() as temp_dir_name:
            path = FilePath(temp_dir_name)

            if is_exists_in_os:
                filepath = path / filename
                with filepath.open("wb") as f:
                    _ = f.write(b"foo")

            if is_exists_in_db:
                _ = await file_meta_document_factory(
                    filename=filename,
                    path=path,
                    type_=SupportedFileTypes.PDF,
                )

            with pytest.raises(FileNotFoundError, match=f"{path / filename} is not exists"):
                _ = await controller.get_file(
                    path=path,
                    filename=filename,
                )

            assert not (path / filename).exists()

        object_in_db = await FileMetaDocument.find_one(
            FileMetaDocument.path == path,
            FileMetaDocument.filename == filename,
        )

        assert not object_in_db

    async def test_invalid_decrypt(
        self,
        file_meta_controller_factory: Callable[..., "FileMetaController"],
        file_meta_document_factory: Callable[..., Awaitable["FileMetaDocument"]],
    ):
        controller = file_meta_controller_factory()
        filename = FileName("test.pdf")

        with tempfile.TemporaryDirectory() as temp_dir_name:
            path = FilePath(temp_dir_name)

            filepath = path / filename
            with filepath.open("wb") as f:
                _ = f.write(b"foo")

            _ = await file_meta_document_factory(
                filename=filename,
                path=path,
                type_=SupportedFileTypes.PDF,
            )

            with pytest.raises(ValueError, match="MAC check failed"):
                _ = await controller.get_file(
                    path=path,
                    filename=filename,
                )

    async def test_success(
        self,
        file_meta_controller_factory: Callable[..., "FileMetaController"],
        file_meta_document_factory: Callable[..., Awaitable["FileMetaDocument"]],
    ):
        controller = file_meta_controller_factory()
        filename = FileName("test.pdf")
        original_data = io.BytesIO(b"bar")
        encoded_data, nonce = encrypt(original_data)

        with tempfile.TemporaryDirectory() as temp_dir_name:
            path = FilePath(temp_dir_name)

            filepath = path / filename
            with filepath.open("wb") as f:
                _ = f.write(encoded_data.read())

            _ = await file_meta_document_factory(
                filename=filename,
                path=path,
                type_=SupportedFileTypes.PDF,
                nonce=nonce,
            )

            decoded_file = await controller.get_file(
                path=path,
                filename=filename,
            )

            assert decoded_file.read() == original_data.read()
