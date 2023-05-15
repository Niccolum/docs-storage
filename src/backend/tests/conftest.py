import contextlib
from collections.abc import AsyncGenerator, Callable, Iterator
from typing import Any

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from backend.create_app import create_app


@pytest.fixture(scope="session")
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
