from .interfaces import IDiskFile
from .interfaces import IDiskFileField
from .interfaces import IDiskFileStorageManager
from .utils import safe_join
from aiofiles.os import wrap
from guillotina import app_settings
from guillotina import configure
from guillotina.component import get_multi_adapter
from guillotina.exceptions import PreconditionFailed
from guillotina.files import BaseCloudFile
from guillotina.interfaces import IFileCleanup
from guillotina.interfaces import IFileNameGenerator
from guillotina.interfaces import IRequest
from guillotina.interfaces import IResource
from guillotina.response import HTTPNotFound
from guillotina.schema import Object
from zope.interface import implementer

import aiofiles
import os

CHUNK_SIZE = 5 * 1024 * 1024

async_os_fsync = wrap(os.fsync)


@implementer(IDiskFile)  # type: ignore
class DiskFile(BaseCloudFile):
    """File stored in a disk, with a filename."""


@implementer(IDiskFileField)  # type: ignore
class DiskFileField(Object):
    """A NamedBlobFile field."""

    _type = DiskFile
    schema = IDiskFile


@configure.adapter(
    for_=(IResource, IRequest, IDiskFileField), provides=IDiskFileStorageManager
)
class DiskFileStorageManager:

    file_class = DiskFile

    def __init__(self, context, request, field):
        self.context = context
        self.request = request
        self.field = field

    def get_file_path(self, dm=None, file=None):
        if dm:
            return dm.get("tmp_path") or dm.get("path")
        elif file:
            return file.path
        return None

    def get_full_path(self, path):
        base_folder = app_settings.get("storage", {})["upload_folder"]
        return safe_join(base_folder, path)

    def _is_uploaded_file(self, file):
        return (
            file is not None
            and isinstance(file, DiskFile)
            and getattr(file, "path") is not None
        )

    async def range_supported(self) -> bool:
        return False

    async def start(self, dm):
        """
        start upload
        """
        rel_path = get_multi_adapter((self.context, self.field), IFileNameGenerator)()

        # Create the file
        path = self.get_full_path(rel_path)
        if path is None:
            raise PreconditionFailed(self.context, f"Invalid or insecure path '{path}'")

        # Ensure folder exists
        head, _ = os.path.split(path)
        if not os.path.exists(head):
            os.makedirs(head, 0o755)

        # Create the file
        async with aiofiles.open(path, "wb+"):
            pass

        await dm.update(tmp_path=rel_path)

    async def iter_data(self):
        """
        iterate through data in file
        """
        disk_file = self.field.query(self.field.context or self.context, None)
        if not self._is_uploaded_file(disk_file):
            raise HTTPNotFound

        path = self.get_full_path(self.get_file_path(file=disk_file))
        async with aiofiles.open(path, "rb") as f:
            while True:
                b = await f.read(CHUNK_SIZE)
                if not b:
                    break
                yield b

    async def append(self, dm, iterable, offset):
        """
        append data to the file
        """
        size = 0
        path = self.get_full_path(self.get_file_path(dm=dm))
        async with aiofiles.open(path, "wb") as f:
            await f.seek(offset)
            async for chunk in iterable:
                size += len(chunk)
                await f.write(chunk)
            await f.flush()
            await async_os_fsync(f.fileno())
        return size

    async def copy(self, to_storage_manager, to_dm):
        """
        copy file to another file
        """
        await to_storage_manager.start(to_dm)
        await to_storage_manager.append(to_dm, self.iter_data(), 0)
        await to_storage_manager.finish(to_dm)
        await to_dm.finish()

    async def finish(self, dm):
        """
        finish upload
        """
        disk_file = self.field.query(self.field.context or self.context, None)
        if disk_file and disk_file.path:  # There is a existing file
            cleanup = IFileCleanup(self.context, None)
            if cleanup is None or cleanup.should_clean(file=disk_file):
                await self.delete(disk_file)

        await dm.update(path=dm.get("tmp_path"), tmp_path=None)

    async def delete(self, file=None):
        ctx = self.field.context or self.context
        if file is None:
            file = self.field.query(ctx, None)

        if file is None:
            raise HTTPNotFound

        path = self.get_full_path(self.get_file_path(file=file))
        try:
            await aiofiles.os.remove(path)
        except FileNotFoundError:
            pass
        file.path = None
        ctx.register()
