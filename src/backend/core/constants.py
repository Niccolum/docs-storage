import enum
import os
from pathlib import Path

import tomllib


class Environment(enum.Enum):
    DEVELOPMENT = "dev"
    PRODUCTION = "prod"


BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
PROJECT_DIR = BASE_DIR.parent.parent

def get_version(path: Path = PROJECT_DIR / "pyproject.toml") -> str:
    with path.open("rb") as fp:
        data = tomllib.load(fp)
    return data["tool"]["poetry"]["version"]

__version__ = get_version()

ENVIRONMENT = Environment(os.environ.get("ENVIRONMENT", Environment.DEVELOPMENT.value))
