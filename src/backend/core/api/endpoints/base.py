from typing import Annotated

from fastapi import APIRouter, Depends

from backend.core.schema import base
from backend.core.settings import Settings, get_settings

router = APIRouter()


@router.get("/healthcheck", response_model=base.HealthCheck, name="healthcheck")
async def healthcheck(settings: Annotated[Settings, Depends(get_settings)]) -> dict[str, str]:
    return {"message": f"Application {settings.app_name} started"}
