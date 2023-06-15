import os
from pathlib import Path

import tomllib

from backend.core.constants import Environment

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent
PROJECT_DIR = BASE_DIR.parent.parent

version_file: Path = PROJECT_DIR / "pyproject.toml"
with version_file.open("rb") as fp:
    data = tomllib.load(fp)
__version__ = data["tool"]["poetry"]["version"]

ENVIRONMENT = Environment(os.environ.get("ENVIRONMENT", Environment.DEVELOPMENT.value))


class SettingsConfigMixin:
    env_file = [
        PROJECT_DIR / "env" / ENVIRONMENT.value / "public.env",
        PROJECT_DIR / "env" / ENVIRONMENT.value / ".secret.env",
    ]
