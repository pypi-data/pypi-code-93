from __future__ import annotations

from datetime import datetime
from typing import Dict

from media_platform.lang import datetime_serialization
from media_platform.lang.serialization import Serializable, Deserializable
from media_platform.service.lifecycle import Lifecycle


class ACL:
    public = 'public'
    private = 'private'

    @classmethod
    def has_value(cls, value):
        return value in [cls.public, cls.private]


class FileType:
    file = '-'
    directory = 'd'
    symlink = 'l'


class FileMimeType:
    directory = 'application/vnd.wix-media.dir'
    symlink = 'application/vnd.wix-media.symlink'
    defualt = 'application/octet-stream'


class FileDescriptor(Serializable, Deserializable):
    def __init__(self, path: str, file_id: str, file_type: FileType, mime_type: str, size: int, acl: ACL = ACL.public,
                 lifecycle: Lifecycle = None, file_hash: str = None,
                 date_created: datetime = None, date_updated: datetime = None, bucket: str = None):
        self._validate_values(acl, path)

        self.path = path
        self.file_id = file_id
        self.type = file_type
        self.mime_type = mime_type
        self.size = size
        self.acl = acl
        self.lifecycle = lifecycle
        self.hash = file_hash
        self.date_created = date_created or datetime.utcnow()
        self.date_updated = date_updated or datetime.utcnow()
        self.bucket = bucket

    @classmethod
    def deserialize(cls, data: Dict) -> FileDescriptor:
        lifecycle_data = data.get('lifecycle')
        return FileDescriptor(
            data['path'],
            data['id'],
            data['type'],
            data['mimeType'],
            data['size'],
            data['acl'],
            Lifecycle.deserialize(lifecycle_data) if lifecycle_data else None,
            data.get('hash'),
            datetime_serialization.deserialize(data.get('dateCreated')),
            datetime_serialization.deserialize(data.get('dateUpdated')),
            data.get('bucket')
        )

    def serialize(self) -> Dict:
        data = {
            'id': self.file_id,
            'path': self.path,
            'type': self.type,
            'mimeType': self.mime_type,
            'size': self.size,
            'hash': self.hash,
            'acl': self.acl,
            'lifecycle': self.lifecycle.serialize() if self.lifecycle else None,
            'dateUpdated': datetime_serialization.serialize(self.date_updated),
            'dateCreated': datetime_serialization.serialize(self.date_created)
        }

        if self.bucket:
            data['bucket'] = self.bucket

        return data

    @staticmethod
    def _validate_values(acl, path):
        FileDescriptor.path_validator(path)
        FileDescriptor.acl_validator(acl)

    @staticmethod
    def path_validator(path: str):
        if not path.startswith('/'):
            raise ValueError(f'path must start with "/"')

    @staticmethod
    def acl_validator(acl):
        if not ACL.has_value(acl):
            raise ValueError(f'ACL {acl} not supported')
