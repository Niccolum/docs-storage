import contextlib
import io
from collections.abc import AsyncGenerator, Callable, Iterator
from pathlib import Path
from typing import TYPE_CHECKING, Any, BinaryIO, Literal

import pytest
from bson import Binary
from fastapi import FastAPI
from httpx import AsyncClient
from PIL import Image

from backend.core.events import setup_mongo, teardown_mongo
from backend.create_app import create_app
from backend.storage.constants import SupportedFileTypes
from backend.storage.controllers.dir_meta import DirMetaController
from backend.storage.controllers.file_meta import FileMetaController
from backend.storage.dao.mongo_file_meta import MongoFileMetaDAO
from backend.storage.dao.os_file_meta import OSFileMetaDAO
from backend.storage.documents.file_meta import FileMetaDocument

if TYPE_CHECKING:
    from faker import Faker


@pytest.fixture()
def app() -> FastAPI:
    return create_app()


@pytest.fixture()
async def test_client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://localhost") as c:
        yield c


@pytest.fixture()
def override_settings(app: FastAPI) -> Callable[[Any, Any], contextlib.AbstractContextManager[None]]:
    @contextlib.contextmanager
    def wrapper(key: Any, value: Any) -> Iterator[None]:
        try:
            app.dependency_overrides[key] = value
            yield
        finally:
            app.dependency_overrides = {}

    return wrapper


@pytest.fixture()
async def _init_beanie() -> AsyncGenerator[None]:  # pyright: ignore reportUnusedFunction
    await setup_mongo()

    yield

    await teardown_mongo()


@pytest.fixture()
def file_meta_controller_factory():
    def wrapper(db_dao: MongoFileMetaDAO | None = None, os_dao: OSFileMetaDAO | None = None) -> FileMetaController:
        db_dao = db_dao or MongoFileMetaDAO()
        os_dao = os_dao or OSFileMetaDAO()
        return FileMetaController(db_dao=db_dao, os_dao=os_dao)

    return wrapper


@pytest.fixture()
def dir_meta_controller_factory():
    def wrapper(db_dao: MongoFileMetaDAO | None = None, os_dao: OSFileMetaDAO | None = None) -> DirMetaController:
        db_dao = db_dao or MongoFileMetaDAO()
        os_dao = os_dao or OSFileMetaDAO()
        return DirMetaController(db_dao=db_dao, os_dao=os_dao)

    return wrapper


@pytest.fixture()
def generate_image():
    def wrapper(image_format: Literal["JPEG", "PNG"]) -> BinaryIO:
        input_image = Image.new(mode="RGB", size=(300, 300), color="red")
        file_ = io.BytesIO()
        input_image.save(file_, format=image_format)
        _ = file_.seek(0)
        return file_

    return wrapper


@pytest.fixture()
async def file_meta_document_factory(_init_beanie: None, file_meta_document_teardown: None, faker: "Faker"):
    async def wrapper(**kwargs: Any) -> FileMetaDocument:
        type_ = kwargs.get("type_", faker.enum(SupportedFileTypes))
        document = FileMetaDocument(
            path=kwargs.get("path", Path(faker.file_path(depth=3)).parent),
            filename=kwargs.get("filename", faker.file_name()),
            type_=type_,
            icon=kwargs.get("icon", None if type_ == SupportedFileTypes.DIR else Binary(faker.pystr().encode())),
            nonce=kwargs.get("nonce", None if type_ == SupportedFileTypes.DIR else faker.pystr().encode()),
        )
        d = await document.create()
        return d

    return wrapper


@pytest.fixture()
async def file_meta_document_teardown():
    yield
    _ = await FileMetaDocument.delete_all()
