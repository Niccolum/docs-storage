import io
import logging

from backend.storage.dao.mongo_file_meta import MongoFileMetaDAO
from backend.storage.dao.os_file_meta import OSFileMetaDAO
from backend.storage.dao_schemas.file_meta import FileMetaDAOSchema
from backend.storage.encryption import decrypt, encrypt
from backend.storage.icon import get_thumbnail
from backend.storage.path_helper import get_file_type
from backend.storage.typing_ import FileName, FilePath

logger = logging.getLogger(__name__)


class FileMetaController:
    def __init__(self, db_dao: MongoFileMetaDAO, os_dao: OSFileMetaDAO) -> None:
        self.db_dao = db_dao
        self.os_dao = os_dao

    async def create_file(self, *, path: FilePath, filename: FileName, data: io.BytesIO, replace: bool) -> None:
        file_type = get_file_type(filename)
        icon = get_thumbnail(file_type=file_type, file_=data)
        encrypted_data, nonce = encrypt(data)

        schema = FileMetaDAOSchema(path=path, filename=filename, type_=file_type, icon=icon, nonce=nonce)

        try:
            await self.db_dao.save(schema, replace=replace)
        except FileExistsError:
            self.os_dao.delete(path=path / filename)
            raise

        self.os_dao.create(data=encrypted_data, filename=filename, path=path, replace=True)

    async def rename_file(
        self,
        *,
        old_path: FilePath,
        old_filename: FileName,
        new_path: FilePath,
        new_filename: FileName,
    ) -> None:
        _ = await self._get_existed_file_from_db(path=old_path, filename=old_filename)

        self.os_dao.rename(old_path=old_path / old_filename, new_path=new_path / new_filename)
        await self.db_dao.update(
            path=old_path,
            filename=old_filename,
            data_to_update={"filename": new_filename, "path": new_path},
        )

    async def get_file(self, *, path: FilePath, filename: FileName) -> io.BytesIO:
        db_file = await self._get_existed_file_from_db(path=path, filename=filename)

        encrypted_file = self.os_dao.get(path / filename)
        decrypted_file = decrypt(encrypted_file, db_file.nonce)
        return decrypted_file

    async def _get_existed_file_from_db(self, *, path: FilePath, filename: FileName) -> "FileMetaDAOSchema":
        db_file = await self.db_dao.get(filename=filename, path=path)

        if not db_file or not self.os_dao.is_exists(path / filename):
            await self.delete_file(path=path, filename=filename)
            raise FileNotFoundError(f"{path / filename} is not exists")

        return db_file

    async def delete_file(self, *, path: FilePath, filename: FileName) -> None:
        self.os_dao.delete(path=path / filename)
        await self.db_dao.delete(path=path, filename=filename)
