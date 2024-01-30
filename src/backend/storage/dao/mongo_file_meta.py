from typing import AsyncIterator

from beanie.operators import RegEx, Set

from backend.storage.constants import SupportedFileTypes
from backend.storage.dao_schemas.file_meta import DirMetaDAOSchema, FileMetaDAOSchema
from backend.storage.documents.file_meta import FileMetaDocument
from backend.storage.typing_ import FileName, FilePath, OptionalFileAttributes


class MongoFileMetaDAO:
    async def get(self, *, path: FilePath, filename: FileName) -> FileMetaDAOSchema | None:
        return await FileMetaDocument.find_one(
            FileMetaDocument.path == path,
            FileMetaDocument.filename == filename,
        ).project(FileMetaDAOSchema)

    async def update(
        self,
        *,
        path: FilePath,
        filename: FileName,
        data_to_update: OptionalFileAttributes,
    ) -> None:
        await FileMetaDocument.find_one(
            FileMetaDocument.path == path,
            FileMetaDocument.filename == filename,
        ).update(Set(data_to_update))  # pyright: ignore reportGeneralTypeIssues

    async def save(self, data: FileMetaDAOSchema | DirMetaDAOSchema, *, replace: bool) -> None:
        is_exists = await self.is_exists(path=data.path, filename=data.filename)
        if is_exists and not replace:
            raise FileExistsError(f"{data.path}/{data.filename} exists in DB")

        document = FileMetaDocument.model_validate(data.model_dump())

        if replace:
            data_to_update = data.model_dump(exclude={"path", "type_", "filename"}, exclude_unset=True)

            _ = await FileMetaDocument.find_one(  # pyright: ignore reportUnknownVariableType
                FileMetaDocument.path == document.path,
                FileMetaDocument.filename == document.filename,
            ).upsert(
                Set(data_to_update),
                on_insert=document,
            )  # pyright: ignore reportGeneralTypeIssues
        else:
            _ = await document.create()

    async def delete(self, *, path: FilePath, filename: FileName, type_: SupportedFileTypes | None = None) -> None:
        data_to_search = {"filename": filename, "path": path}
        if type_:
            data_to_search |= {"type_": type_}

        _ = await FileMetaDocument.find_one(data_to_search).delete()

    async def regex_delete(self, key: str, value: str) -> None:
        _ = await FileMetaDocument.find(
            RegEx(
                getattr(FileMetaDocument, key),
                pattern=f"^{value}",
                options="m",
            ),
        ).delete()

    async def ls(self, path: FilePath) -> AsyncIterator[FileMetaDAOSchema | DirMetaDAOSchema]:
        async for document in FileMetaDocument.find(
            FileMetaDocument.path == path,
            FileMetaDocument.type_ != SupportedFileTypes.DIR,
        ).project(FileMetaDAOSchema):
            yield document

        async for document in FileMetaDocument.find(
            FileMetaDocument.path == path,
            FileMetaDocument.type_ == SupportedFileTypes.DIR,
        ).project(DirMetaDAOSchema):
            yield document

    async def regex_update(self, key: str, old_value: str, new_value: str) -> None:
        collection = FileMetaDocument.get_motor_collection()

        _ = await collection.update_many(
            filter=RegEx(
                getattr(FileMetaDocument, key),
                pattern=f"^{old_value}",
                options="m",
            ),
            update=[
                Set(
                    {
                        key: {
                            "$replaceAll": {
                                "input": f"${key}",
                                "find": old_value,
                                "replacement": new_value,
                            },
                        },
                    },
                ),
            ],
        )

    async def get_all(self) -> AsyncIterator[FileMetaDAOSchema | DirMetaDAOSchema]:
        async for document in FileMetaDocument.find(FileMetaDocument.type_ != SupportedFileTypes.DIR).project(
            FileMetaDAOSchema,
        ):
            yield document

        async for document in FileMetaDocument.find(FileMetaDocument.type_ == SupportedFileTypes.DIR).project(
            DirMetaDAOSchema,
        ):
            yield document

    async def is_exists(
        self,
        *,
        filename: FileName,
        path: FilePath,
    ) -> bool:
        return bool(
            await FileMetaDocument.find_one(
                FileMetaDocument.path == path,
                FileMetaDocument.filename == filename,
            ),
        )
