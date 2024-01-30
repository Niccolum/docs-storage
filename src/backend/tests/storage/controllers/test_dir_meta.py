import re
import tempfile
from typing import TYPE_CHECKING, Awaitable, Callable

import pytest

from backend.core.settings.main import Settings
from backend.storage.constants import SupportedFileTypes
from backend.storage.documents.file_meta import FileMetaDocument
from backend.storage.typing_ import FileName, FilePath

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

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

    @pytest.mark.usefixtures("file_meta_document_teardown")
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
    async def test_no_os_parent_dir(self, dir_meta_controller_factory: Callable[..., "DirMetaController"]):
        controller = dir_meta_controller_factory()

        with pytest.raises(OSError, match=re.escape("[Errno 2] No such file or directory: '/foo/bar/baz'")):
            _ = await controller.create_dir(
                path=FilePath("/foo/bar/"),
                filename=FileName("baz"),
            )

    @pytest.mark.usefixtures("_init_beanie")
    async def test_success_already_exist_dir_in_os(
        self,
        dir_meta_controller_factory: Callable[..., "DirMetaController"],
    ):
        controller = dir_meta_controller_factory()

        with tempfile.TemporaryDirectory() as dir_path:
            base_path = FilePath(dir_path)
            path = base_path.parent
            filename = FileName(base_path.name)

            created_file_path = await controller.create_dir(
                path=path,
                filename=filename,
            )

        assert created_file_path == base_path == path / filename

        dir_in_db = await FileMetaDocument.find_one(
            FileMetaDocument.path == path,
        )

        assert dir_in_db
        assert dir_in_db.filename == filename
        assert dir_in_db.type_ == SupportedFileTypes.DIR
        assert dir_in_db.icon is None
        assert dir_in_db.created_date is not None

    @pytest.mark.usefixtures("_init_beanie")
    async def test_success_already_exist_parent_dir_in_os(
        self,
        dir_meta_controller_factory: Callable[..., "DirMetaController"],
    ):
        controller = dir_meta_controller_factory()

        with tempfile.TemporaryDirectory() as dir_path:
            path = FilePath(dir_path)
            filename = FileName("foo")

            created_file_path = await controller.create_dir(
                path=path,
                filename=filename,
            )

        assert created_file_path == path / filename

        dir_in_db = await FileMetaDocument.find_one(
            FileMetaDocument.path == path,
        )

        assert dir_in_db
        assert dir_in_db.filename == filename
        assert dir_in_db.type_ == SupportedFileTypes.DIR
        assert dir_in_db.icon is None
        assert dir_in_db.created_date is not None


class TestDeleteDir:
    @pytest.mark.usefixtures("_init_beanie")
    async def test_success_not_exists_dir(self, dir_meta_controller_factory: Callable[..., "DirMetaController"]):
        controller = dir_meta_controller_factory()

        await controller.delete_dir(
            path=FilePath("/foo/bar/"),
            filename=FileName("baz"),
        )

    async def test_success_exists_dir(
        self,
        dir_meta_controller_factory: Callable[..., "DirMetaController"],
        file_meta_document_factory: Callable[..., Awaitable["FileMetaDocument"]],
    ):
        controller = dir_meta_controller_factory()

        with tempfile.TemporaryDirectory() as raw_dir_path:
            dir_path = FilePath(raw_dir_path)

            with (dir_path / "foo.pdf").open("wb") as f:
                _ = f.write(b"test")

            _ = await file_meta_document_factory(
                path=dir_path.parent,
                filename=dir_path.name,
                type_=SupportedFileTypes.DIR,
            )
            _ = await file_meta_document_factory(
                path=dir_path,
                filename="foo.pdf",
                type_=SupportedFileTypes.PDF,
            )

            await controller.delete_dir(
                path=dir_path.parent,
                filename=dir_path.name,
            )

            assert not dir_path.exists()

            dir_in_db = await FileMetaDocument.find(FileMetaDocument.path == dir_path.parent).to_list()
            assert dir_in_db == []

            file_in_db = await FileMetaDocument.find(FileMetaDocument.path == dir_path).to_list()
            assert file_in_db == []

    @pytest.mark.usefixtures("_init_beanie")
    async def test_success_not_empty_os_dir(self, dir_meta_controller_factory: Callable[..., "DirMetaController"]):
        controller = dir_meta_controller_factory()

        with tempfile.TemporaryDirectory() as raw_dir_path:
            dir_path = FilePath(raw_dir_path)

            with (dir_path / "foo.pdf").open("wb") as f:
                _ = f.write(b"test")

            with (dir_path / "bar.pdf").open("wb") as f:
                _ = f.write(b"test")

            await controller.delete_dir(
                path=dir_path.parent,
                filename=dir_path.name,
            )

            assert not dir_path.exists()

    async def test_success_not_empty_db_dir(
        self,
        dir_meta_controller_factory: Callable[..., "DirMetaController"],
        file_meta_document_factory: Callable[..., Awaitable["FileMetaDocument"]],
    ):
        controller = dir_meta_controller_factory()

        dir_path = FilePath("/foo/bar/baz")

        _ = await file_meta_document_factory(
            path=dir_path.parent,
            filename=dir_path.name,
            type_=SupportedFileTypes.DIR,
        )
        _ = await file_meta_document_factory(
            path=dir_path,
            filename="foo.pdf",
            type_=SupportedFileTypes.PDF,
        )

        await controller.delete_dir(
            path=dir_path.parent,
            filename=dir_path.name,
        )

        assert not dir_path.exists()

        dir_in_db = await FileMetaDocument.find(FileMetaDocument.path == dir_path.parent).to_list()
        assert dir_in_db == []

        file_in_db = await FileMetaDocument.find(FileMetaDocument.path == dir_path).to_list()
        assert file_in_db == []


class TestLs:
    @pytest.mark.usefixtures("_init_beanie")
    async def test_no_dir(self, dir_meta_controller_factory: Callable[..., "DirMetaController"]):
        controller = dir_meta_controller_factory()

        data = [file_ async for file_ in controller.ls(path=FilePath("/foo/bar"))]

        assert data == []

    @pytest.mark.usefixtures("_init_beanie")
    async def test_no_dir_in_db(self, dir_meta_controller_factory: Callable[..., "DirMetaController"]):
        controller = dir_meta_controller_factory()

        with tempfile.TemporaryDirectory() as raw_dir_path:
            dir_path = FilePath(raw_dir_path)

            data = [file_ async for file_ in controller.ls(path=dir_path)]

            assert data == []

    @pytest.mark.usefixtures("_init_beanie")
    async def test_no_dir_in_os(
        self,
        dir_meta_controller_factory: Callable[..., "DirMetaController"],
        file_meta_document_factory: Callable[..., Awaitable["FileMetaDocument"]],
    ):
        with tempfile.TemporaryDirectory() as raw_dir_path:
            dir_path = FilePath(raw_dir_path)
            _ = await file_meta_document_factory(
                path=dir_path,
                type_=SupportedFileTypes.DIR,
            )

            controller = dir_meta_controller_factory()

            data = [file_ async for file_ in controller.ls(path=dir_path)]

            assert data == []

    async def test_no_files_in_dir_in_db(
        self,
        dir_meta_controller_factory: Callable[..., "DirMetaController"],
        file_meta_document_factory: Callable[..., Awaitable["FileMetaDocument"]],
    ):
        with tempfile.TemporaryDirectory() as raw_dir_path:
            dir_path = FilePath(raw_dir_path)

            with (dir_path / "foo.pdf").open("wb") as f:
                _ = f.write(b"test")

            _ = await file_meta_document_factory(
                path=dir_path.parent,
                filename=dir_path.name,
                type_=SupportedFileTypes.DIR,
            )

            controller = dir_meta_controller_factory()

            data = [file_ async for file_ in controller.ls(path=dir_path)]

            assert data == []
            assert (dir_path / "foo.pdf").exists()

    async def test_no_files_in_dir_in_os(
        self,
        dir_meta_controller_factory: Callable[..., "DirMetaController"],
        file_meta_document_factory: Callable[..., Awaitable["FileMetaDocument"]],
    ):
        with tempfile.TemporaryDirectory() as raw_dir_path:
            dir_path = FilePath(raw_dir_path)

            _ = await file_meta_document_factory(
                path=dir_path.parent,
                filename=dir_path.name,
                type_=SupportedFileTypes.DIR,
            )
            _ = await file_meta_document_factory(
                path=dir_path,
                filename="foo.pdf",
                type_=SupportedFileTypes.PDF,
            )

            controller = dir_meta_controller_factory()

            data = [file_ async for file_ in controller.ls(path=dir_path)]

            assert data == []
            assert not (dir_path / "foo.pdf").exists()

            dir_in_db = await FileMetaDocument.find(FileMetaDocument.path == dir_path.parent).to_list()
            assert len(dir_in_db) == 1

            files_in_db = await FileMetaDocument.find(FileMetaDocument.path == dir_path).to_list()
            assert files_in_db == []

    async def test_files_in_db_and_os(  # noqa: NQA103 FNE007 RUF100
        self,
        dir_meta_controller_factory: Callable[..., "DirMetaController"],
        file_meta_document_factory: Callable[..., Awaitable["FileMetaDocument"]],
    ):
        with tempfile.TemporaryDirectory() as raw_dir_path:
            dir_path = FilePath(raw_dir_path)

            nested_path = dir_path / "foo"
            nested_path.mkdir()

            file_path = dir_path / "bar.pdf"
            with file_path.open("wb") as f:
                _ = f.write(b"test")

            _ = await file_meta_document_factory(
                path=dir_path,
                filename="foo",
                type_=SupportedFileTypes.DIR,
            )
            _ = await file_meta_document_factory(
                path=dir_path,
                filename="bar.pdf",
                type_=SupportedFileTypes.PDF,
            )

            controller = dir_meta_controller_factory()

            data = [file_ async for file_ in controller.ls(path=dir_path)]

            assert data == [file_path, nested_path]
            assert nested_path.exists()
            assert file_path.exists()

            dir_in_db = await FileMetaDocument.find(FileMetaDocument.path == dir_path).to_list()
            assert len(dir_in_db) == len(data)

    async def test_not_find_nested_files(
        self,
        dir_meta_controller_factory: Callable[..., "DirMetaController"],
        file_meta_document_factory: Callable[..., Awaitable["FileMetaDocument"]],
    ):
        with tempfile.TemporaryDirectory() as raw_dir_path:
            dir_path = FilePath(raw_dir_path)

            nested_path = dir_path / "foo"
            nested_path.mkdir()

            nested_file = nested_path / "bar.pdf"
            with nested_file.open("wb") as f:
                _ = f.write(b"test")

            _ = await file_meta_document_factory(
                path=dir_path,
                filename="foo",
                type_=SupportedFileTypes.DIR,
            )
            _ = await file_meta_document_factory(
                path=nested_path,
                filename="bar.pdf",
                type_=SupportedFileTypes.PDF,
            )

            controller = dir_meta_controller_factory()

            data = [file_ async for file_ in controller.ls(path=dir_path)]

            assert data == [nested_path]
            assert nested_path.exists()
            assert nested_file.exists()

            dir_in_db = await FileMetaDocument.find(FileMetaDocument.path == dir_path).to_list()
            assert len(dir_in_db) == 1

            nested_file_in_db = await FileMetaDocument.find(FileMetaDocument.path == nested_path).to_list()
            assert len(nested_file_in_db) == 1


class TestCheckIntegrity:
    async def test_success_in_db_not_in_os(
        self,
        mocker: "MockerFixture",
        dir_meta_controller_factory: Callable[..., "DirMetaController"],
        file_meta_document_factory: Callable[..., Awaitable["FileMetaDocument"]],
    ):
        dir_path = FilePath("/path/to/dir")

        _ = mocker.patch(
            "backend.storage.dao.os_file_meta.get_settings",
            return_value=Settings(storage_path=dir_path),  # pyright: ignore reportGeneralTypeIssues
        )

        _ = await file_meta_document_factory(
            path=dir_path.parent,
            filename=dir_path.name,
            type_=SupportedFileTypes.DIR,
        )
        _ = await file_meta_document_factory(
            path=dir_path,
            filename="foo.pdf",
            type_=SupportedFileTypes.PDF,
        )

        controller = dir_meta_controller_factory()

        with pytest.raises(FileNotFoundError, match=f"NOT IN OS: {dir_path / 'foo.pdf'}"):
            await controller.check_integrity()
        with pytest.raises(FileNotFoundError, match=f"NOT IN OS: {dir_path}"):
            await controller.check_integrity()

    @pytest.mark.usefixtures("_init_beanie")
    async def test_success_in_os_not_in_db(
        self,
        mocker: "MockerFixture",
        dir_meta_controller_factory: Callable[..., "DirMetaController"],
    ):
        with tempfile.TemporaryDirectory() as raw_dir_path:
            dir_path = FilePath(raw_dir_path)

            _ = mocker.patch(
                "backend.storage.dao.os_file_meta.get_settings",
                return_value=Settings(storage_path=dir_path),  # pyright: ignore reportGeneralTypeIssues
            )

            nested_path = dir_path / "foo"
            nested_path.mkdir()

            file_path = dir_path / "bar.pdf"
            with file_path.open("wb") as f:
                _ = f.write(b"test")

            controller = dir_meta_controller_factory()

            with pytest.raises(FileNotFoundError, match=f"NOT IN DB: {dir_path / 'bar.pdf'}"):
                await controller.check_integrity()
            with pytest.raises(FileNotFoundError, match=f"NOT IN DB: {nested_path}"):
                await controller.check_integrity()

    async def test_success_same_in_db_in_os(
        self,
        mocker: "MockerFixture",
        dir_meta_controller_factory: Callable[..., "DirMetaController"],
        file_meta_document_factory: Callable[..., Awaitable["FileMetaDocument"]],
    ):
        with tempfile.TemporaryDirectory() as raw_dir_path:
            dir_path = FilePath(raw_dir_path)

            _ = mocker.patch(
                "backend.storage.dao.os_file_meta.get_settings",
                return_value=Settings(storage_path=dir_path),  # pyright: ignore reportGeneralTypeIssues
            )

            nested_path = dir_path / "foo"
            nested_path.mkdir()

            _ = await file_meta_document_factory(
                path=dir_path,
                filename="foo",
                type_=SupportedFileTypes.DIR,
            )

            file_path = dir_path / "bar.pdf"
            with file_path.open("wb") as f:
                _ = f.write(b"test")

            _ = await file_meta_document_factory(
                path=dir_path,
                filename="bar.pdf",
                type_=SupportedFileTypes.PDF,
            )

            controller = dir_meta_controller_factory()

            await controller.check_integrity()
