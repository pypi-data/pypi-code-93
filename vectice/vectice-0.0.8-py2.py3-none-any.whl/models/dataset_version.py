from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .artifact import _Base
from .with_data_resources import WithDataResources
from .with_properties import WithProperties
from .with_version import WithVersion


@dataclass
class DatasetVersion(_Base, WithVersion, WithProperties, WithDataResources):
    """"""

    autoVersion: bool = True

    def with_auto_version(self, auto_version=True) -> DatasetVersion:
        """"""
        self.autoVersion = auto_version
        self.userDeclaredVersion = None
        self.version = None
        return self

    def with_user_version(
        self,
        user_version: str,
        name: Optional[str] = None,
        uri: Optional[str] = None,
        description: Optional[str] = None,
    ) -> DatasetVersion:
        self.autoVersion = False
        return super().with_user_version(user_version, name, uri, description)

    def with_existing_version_id(self, version_number: int) -> DatasetVersion:
        self.autoVersion = False
        return super().with_existing_version_id(version_number)

    def with_existing_version_name(self, version_name: str) -> DatasetVersion:
        self.autoVersion = False
        return super().with_existing_version_name(version_name)
