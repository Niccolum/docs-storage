import io
import shutil
from typing import Iterable

from backend.core.settings import get_settings
from backend.storage.typing_ import FileName, FilePath


class OSFileMetaDAO:
    def get(self, path: FilePath) -> io.BytesIO:
        with path.open("rb") as raw_file:
            return io.BytesIO(raw_file.read())

    def rename(self, *, old_path: FilePath, new_path: FilePath) -> None:
        self.check_exists(old_path)
        self.check_exists(new_path.parent)

        _ = old_path.rename(new_path)

    def create(self, *, path: FilePath, filename: FileName, data: io.BytesIO, replace: bool) -> None:
        self.check_exists(path)
        if not replace:
            self._check_not_exists(path / filename)

        _ = (path / filename).write_bytes(data.read())

    def create_dir(self, *, path: FilePath, filename: FileName, exist_ok: bool = True) -> FilePath:
        full_path = path / filename
        full_path.mkdir(exist_ok=exist_ok)
        return full_path

    def delete(self, path: FilePath, *, silent: bool = True) -> None:
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=silent)
        else:
            path.unlink(missing_ok=silent)

    def ls(self, path: FilePath) -> Iterable[FilePath]:
        yield from path.iterdir()

    def get_all(self) -> Iterable[FilePath]:
        settings = get_settings()

        for item in settings.storage_path.rglob("*"):
            yield FilePath(item)

    def check_exists(self, path: FilePath) -> None:
        if not self.is_exists(path):
            raise FileNotFoundError(f"{path} not found in OS")

    def _check_not_exists(self, path: FilePath) -> None:
        if self.is_exists(path):
            raise FileExistsError(f"{path} found in OS")

    def is_exists(self, path: FilePath) -> bool:
        return path.exists()
