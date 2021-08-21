from typing import Optional, Any, Dict

from pydantic.dataclasses import dataclass

from architect.core.config import settings
from architect.core.schemas import BaseDataClass

from architect.core.backends.local import LocalFilesystemBackend
from architect.core.backends.aws_ssm import AwsSystemsManagerBackend


ALL_BACKENDS = {
    'local': LocalFilesystemBackend,
    'aws_ssm': AwsSystemsManagerBackend
}


@dataclass
class SecretSchema(BaseDataClass):
    name: str
    type: Optional[str]
    data: Dict[str, Any]


@dataclass
class ConnectionSchema(BaseDataClass):
    name: str
    type: Optional[str]
    data: Dict[str, Any]
    secret: Optional[str]


class SecretsBackend:
    schema_class = SecretSchema

    def get_backend(self, backend_type: Optional[str] = None):
        backend_type = backend_type if backend_type else settings.DEFAULT_BACKEND_TYPE
        return ALL_BACKENDS[backend_type](schema_class=self.schema_class)


class ConnectionsBackend:
    schema_class = ConnectionSchema

    def get_backend(self, backend_type: Optional[str] = None):
        backend_type = backend_type if backend_type else settings.DEFAULT_BACKEND_TYPE
        return ALL_BACKENDS[backend_type](schema_class=self.schema_class)
