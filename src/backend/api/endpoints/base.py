from typing import Annotated

from fastapi import APIRouter, Depends

from backend.schema import base
from backend.settings import base as app_settings

router = APIRouter()


@router.get("/healthcheck", response_model=base.HealthCheck, name="healthcheck")
async def healthcheck(settings: Annotated[app_settings.Settings, Depends(app_settings.get_settings)]) -> dict[str, str]:
    return {"message": f"Application {settings.app_name} started"}
