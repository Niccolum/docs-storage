from fastapi import APIRouter, Depends

from backend.schema import base
from backend.settings import app as app_settings


router = APIRouter()


@router.get("/healthcheck", response_model=base.HealthCheck, name="healthcheck")
async def healthcheck(settings: app_settings.Settings = Depends(app_settings.get_settings)):
    return {"message": f"Application {settings.app_name} started"}
