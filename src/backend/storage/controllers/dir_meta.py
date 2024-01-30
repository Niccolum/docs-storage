import logging
from typing import AsyncIterator

from backend.storage.constants import SupportedFileTypes
from backend.storage.dao.mongo_file_meta import MongoFileMetaDAO
from backend.storage.dao.os_file_meta import OSFileMetaDAO
from backend.storage.dao_schemas.file_meta import DirMetaDAOSchema
from backend.storage.typing_ import FileName, FilePath, OptionalFileAttributes

logger = logging.getLogger(__name__)


class DirMetaController:
    def __init__(self, db_dao: MongoFileMetaDAO, os_dao: OSFileMetaDAO) -> None:
        self.db_dao = db_dao
        self.os_dao = os_dao

    async def rename_dir(
        self,
        *,
        old_path: FilePath,
        old_filename: FileName,
        new_path: FilePath,
        new_filename: FileName,
    ) -> None:
        _ = await self.create_dir(path=new_path, filename=new_filename)

        self.os_dao.rename(old_path=old_path / old_filename, new_path=new_path / new_filename)

        data_to_update = OptionalFileAttributes({"path": new_path, "filename": new_filename})
        await self.db_dao.update(path=old_path, filename=old_filename, data_to_update=data_to_update)
        await self.db_dao.regex_update(
            key="path",
            old_value=str(old_path / old_filename),
            new_value=str(new_path / new_filename),
        )

        await self.delete_dir(path=old_path, filename=old_filename)

    async def create_dir(self, *, path: FilePath, filename: FileName) -> FilePath:
        file_path = self.os_dao.create_dir(path=path, filename=filename, exist_ok=True)

        schema = DirMetaDAOSchema(path=path, filename=filename, type_=SupportedFileTypes.DIR)
        await self.db_dao.save(schema, replace=True)

        return file_path

    async def delete_dir(self, *, path: FilePath, filename: FileName) -> None:
        self.os_dao.delete(path=path / filename)
        await self.db_dao.regex_delete(
            key="path",
            value=str(path / filename),
        )
        await self.db_dao.delete(path=path, filename=filename)

    async def ls(self, *, path: FilePath) -> AsyncIterator[FilePath]:
        async for document in self.db_dao.ls(path):
            if not self.os_dao.is_exists(document.path / document.filename):
                await self.db_dao.delete(path=document.path, filename=document.filename)
                continue
            yield document.path / document.filename

    async def check_integrity(self) -> None:
        errors = []

        for os_filepath in self.os_dao.get_all():
            path = os_filepath.parent
            filename = FileName(os_filepath.name)

            if not await self.db_dao.is_exists(filename=filename, path=path):
                errors.append(f"NOT IN DB: {os_filepath}")
                logger.warning(f"Path {os_filepath} exists in filesystem, but not exist in mongo")

        async for document in self.db_dao.get_all():
            db_filepath = document.path / document.filename
            if not self.os_dao.is_exists(db_filepath):
                errors.append(f"NOT IN OS: {db_filepath}")
                logger.warning(f"Path {db_filepath} exists in mongo, but not exist really")

        if errors:
            str_errors = "\n".join(errors)
            raise FileNotFoundError(f"Files: \n{str_errors}\n not exists")
