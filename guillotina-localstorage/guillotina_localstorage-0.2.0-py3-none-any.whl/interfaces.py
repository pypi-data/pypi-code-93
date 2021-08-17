from guillotina.interfaces import IExternalFileStorageManager
from guillotina.interfaces import IFile
from guillotina.interfaces import IFileField


class IDiskFile(IFile):
    """Marker for a DiskFile"""


class IDiskFileField(IFileField):
    """Field marked as DiskFileField"""


class IDiskFileStorageManager(IExternalFileStorageManager):
    pass
