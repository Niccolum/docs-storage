import logging

from single_source import (
    VersionNotFoundError,
    get_version,
)

from backend.settings.app import PROJECT_DIR

logger = logging.getLogger(__name__)
path_to_pyproject_toml = PROJECT_DIR

try:
    __version__ = get_version(__name__, path_to_pyproject_toml, fail=True)
except VersionNotFoundError:
    logger.warning(f"Can't find version in pyproject.toml using '{path_to_pyproject_toml}' path")
    __version__ = ""
