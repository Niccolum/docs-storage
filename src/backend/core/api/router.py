from fastapi import APIRouter

from backend.core.api.endpoints import base

api_router = APIRouter()
api_router.include_router(base.router, tags=["base"], prefix="")
