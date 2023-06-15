from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import Any

import httpx
import pytest
from fastapi import FastAPI, status

from backend.core.settings import Settings, get_settings


@pytest.mark.asyncio()
async def test_healthcheck(
    app: FastAPI,
    test_client: httpx.AsyncClient,
    override_settings: Callable[[Any, Any], AbstractContextManager[None]],
):
    test_app_name = "testing_application"

    def mock_service_name() -> Settings:
        return Settings(app_name=test_app_name)  # pyright: ignore reportGeneralTypeIssues

    with override_settings(get_settings, mock_service_name):
        url = app.router.url_path_for("healthcheck")
        response = await test_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": f"Application {test_app_name} started"}
