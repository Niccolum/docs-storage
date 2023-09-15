from pydantic_settings.sources import DotenvType

from backend.core.constants import ENVIRONMENT, PROJECT_DIR

env_file: DotenvType  = [
    PROJECT_DIR / "env" / ENVIRONMENT.value / "public.env",
    PROJECT_DIR / "env" / ENVIRONMENT.value / ".secret.env",
]
