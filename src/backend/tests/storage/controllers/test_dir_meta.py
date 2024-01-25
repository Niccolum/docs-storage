import tempfile
from typing import TYPE_CHECKING, Awaitable, Callable

import pytest

from backend.storage.constants import SupportedFileTypes
from backend.storage.documents.file_meta import FileMetaDocument
from backend.storage.typing_ import FileName, FilePath

if TYPE_CHECKING:
    from backend.storage.controllers.dir_meta import DirMetaController


class TestRenameDir:
    async def test_not_new_dir_in_os(self, dir_meta_controller_factory: Callable[..., "DirMetaController"]):
        controller = dir_meta_controller_factory()
        new_path = FilePath("/foo/bar")
        filename = FileName("baz")

        with pytest.raises(FileNotFoundError, match="No such file or directory: '/foo/bar/baz'"):
            await controller.rename_dir(
                old_path=FilePath("/"),
                old_filename=filename,
                new_path=new_path,
                new_filename=filename,
            )

    @pytest.mark.usefixtures("_init_beanie")
    async def test_not_old_dir_in_os(self, dir_meta_controller_factory: Callable[..., "DirMetaController"]):
        controller = dir_meta_controller_factory()

        with tempfile.TemporaryDirectory() as dir_path:
            new_path = FilePath(dir_path)
            filename = FileName("baz")

            with pytest.raises(FileNotFoundError, match="/foo/bar/baz not found in OS"):
                await controller.rename_dir(
                    old_path=FilePath("/foo/bar"),
                    old_filename=filename,
                    new_path=new_path,
                    new_filename=filename,
                )

    async def test_success_different_base_dir(
        self,
        dir_meta_controller_factory: Callable[..., "DirMetaController"],
        file_meta_document_factory: Callable[..., Awaitable["FileMetaDocument"]],
    ):
        controller = dir_meta_controller_factory()

        with tempfile.TemporaryDirectory() as old_dir_path, tempfile.TemporaryDirectory() as new_dir_path:
            old_base_path = FilePath(old_dir_path)
            new_base_path = FilePath(new_dir_path)
            old_filename = FileName("foo")
            new_filename = FileName("bar")

            (old_base_path / old_filename).mkdir()

            with (old_base_path / old_filename / "baz.pdf").open("wb") as f:
                _ = f.write(b"test")

            old_db_dir = await file_meta_document_factory(
                path=old_base_path,
                filename=old_filename,
                type_=SupportedFileTypes.DIR,
            )
            old_db_file = await file_meta_document_factory(
                path=old_base_path / old_filename,
                filename="baz.pdf",
                type_=SupportedFileTypes.PDF,
            )

            await controller.rename_dir(
                old_path=old_base_path,
                old_filename=old_filename,
                new_path=new_base_path,
                new_filename=new_filename,
            )

            assert not (old_base_path / old_filename).exists()
            assert (new_base_path / new_filename).exists()

            assert (new_base_path / new_filename / "baz.pdf").exists()
            with (new_base_path / new_filename / "baz.pdf").open("rb") as f:
                assert f.read() == b"test"

            dir_in_db = await FileMetaDocument.find_one(
                FileMetaDocument.path == new_base_path,
            )

            assert dir_in_db
            assert dir_in_db.filename == new_filename
            assert dir_in_db.type_ == old_db_dir.type_ == SupportedFileTypes.DIR
            assert dir_in_db.icon == old_db_dir.icon

            file_in_db = await FileMetaDocument.find_one(
                FileMetaDocument.path == new_base_path / new_filename,
            )

            assert file_in_db
            assert file_in_db.filename == old_db_file.filename == "baz.pdf"
            assert file_in_db.type_ == old_db_file.type_ == SupportedFileTypes.PDF
            assert file_in_db.icon == old_db_file.icon

    async def test_success_same_base_dir(
        self,
        dir_meta_controller_factory: Callable[..., "DirMetaController"],
        file_meta_document_factory: Callable[..., Awaitable["FileMetaDocument"]],
    ):
        controller = dir_meta_controller_factory()

        with tempfile.TemporaryDirectory() as dir_path:
            base_path = FilePath(dir_path)
            old_filename = FileName("foo")
            new_filename = FileName("bar")

            (base_path / old_filename).mkdir()

            with (base_path / old_filename / "baz.pdf").open("wb") as f:
                _ = f.write(b"test")

            old_db_dir = await file_meta_document_factory(
                path=base_path,
                filename=old_filename,
                type_=SupportedFileTypes.DIR,
            )
            old_db_file = await file_meta_document_factory(
                path=base_path / old_filename,
                filename="baz.pdf",
                type_=SupportedFileTypes.PDF,
            )

            await controller.rename_dir(
                old_path=base_path,
                old_filename=old_filename,
                new_path=base_path,
                new_filename=new_filename,
            )

            assert not (base_path / old_filename).exists()
            assert (base_path / new_filename).exists()

            assert (base_path / new_filename / "baz.pdf").exists()
            with (base_path / new_filename / "baz.pdf").open("rb") as f:
                assert f.read() == b"test"

            dir_in_db = await FileMetaDocument.find_one(
                FileMetaDocument.path == base_path,
            )

            assert dir_in_db
            assert dir_in_db.filename == new_filename
            assert dir_in_db.type_ == old_db_dir.type_ == SupportedFileTypes.DIR
            assert dir_in_db.icon == old_db_dir.icon

            file_in_db = await FileMetaDocument.find_one(
                FileMetaDocument.path == base_path / new_filename,
            )

            assert file_in_db
            assert file_in_db.filename == old_db_file.filename == "baz.pdf"
            assert file_in_db.type_ == old_db_file.type_ == SupportedFileTypes.PDF
            assert file_in_db.icon == old_db_file.icon


class TestCreateDir:
    async def test_already_exist_in_os(self):
        ...

    async def test_success(self):
        ...


class TestDeleteDir:
    async def test_not_empty_dir(self):
        ...

    async def test_success(self):
        ...


class TestLs:
    async def test_not_exist_dir_in_db(self):
        ...

    async def test_not_exist_subdir_in_os(self):
        ...

    async def test_success(self):
        ...


class TestCheckIntegrity:
    async def test_success_in_db_not_in_os(self):
        ...

    async def test_success_in_os_not_in_db(self):
        ...

    async def test_success_same_in_db_in_os(self):
        ...
