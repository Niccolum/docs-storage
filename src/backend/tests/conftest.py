import contextlib
import typing as t

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from backend.create_app import create_app


@pytest.fixture(scope="session")
def app() -> FastAPI:
    return create_app()


@pytest.fixture()
async def test_client(app: FastAPI) -> t.AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c


@pytest.fixture()
def override_settings(app: FastAPI) -> t.Callable[[t.Any, t.Any], contextlib.AbstractContextManager[None]]:
    @contextlib.contextmanager
    def wrapper(key: t.Any, value: t.Any) -> t.Iterator[None]:
        try:
            app.dependency_overrides[key] = value
            yield
        finally:
            app.dependency_overrides = {}

    return wrapper
