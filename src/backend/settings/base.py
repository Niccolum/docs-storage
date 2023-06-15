import os
from pathlib import Path

from single_source import get_version

from backend.constants import Environment

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
PROJECT_DIR = BASE_DIR.parent.parent

__version__: str = get_version(__name__, PROJECT_DIR, default_return="")  # pyright: ignore reportGeneralTypeIssues

ENVIRONMENT = Environment(os.environ.get("ENVIRONMENT", Environment.DEVELOPMENT.value))


class SettingsConfigMixin:
    env_file = [
        PROJECT_DIR / "env" / ENVIRONMENT.value / "public.env",
        PROJECT_DIR / "env" / ENVIRONMENT.value / ".secret.env",
    ]
