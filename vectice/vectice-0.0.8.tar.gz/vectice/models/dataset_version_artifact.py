from __future__ import annotations

from typing import Optional

from .artifact import Artifact
from .artifact_type import ArtifactType
from .dataset_version import DatasetVersion
from .with_data_resources import WithDelegatedDataResources
from .with_properties import WithDelegatedProperties
from .with_version import WithDelegatedVersion


class DatasetVersionArtifact(Artifact, WithDelegatedProperties, WithDelegatedVersion, WithDelegatedDataResources):
    """"""

    def __init__(self, dataset: DatasetVersion, description: Optional[str] = None):
        self.artifactType = ArtifactType.DATASET
        self.description = description
        self.dataset: DatasetVersion = dataset

    @classmethod
    def create(
        cls,
        description: Optional[str] = None,
    ) -> DatasetVersionArtifact:
        """"""
        return cls(DatasetVersion(), description)

    def _get_delegate(self) -> DatasetVersion:
        return self.dataset

    def with_auto_version(self, auto_version=True) -> DatasetVersionArtifact:
        """
        Indicate if we should or not use the auto version mechanism

        :return: itself
        """
        self.dataset.with_auto_version(auto_version)
        return self
