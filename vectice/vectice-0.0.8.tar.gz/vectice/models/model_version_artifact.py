from __future__ import annotations

from typing import Optional, Union
from enum import Enum
from vectice.entity.model import ModelType
from vectice.entity.model_version import ModelVersionStatus

from .artifact import Artifact
from .artifact_type import ArtifactType
from .model_version import ModelVersion
from .with_metrics import WithDelegatedMetrics
from .with_properties import WithDelegatedProperties
from .with_version import WithDelegatedVersion


class ModelVersionArtifact(Artifact[ModelVersion], WithDelegatedProperties, WithDelegatedVersion, WithDelegatedMetrics):
    def __init__(self, model: ModelVersion, description: Optional[str] = None):
        self.artifactType = ArtifactType.MODEL
        self.description = description
        self.model: ModelVersion = model

    @classmethod
    def create(
        cls,
        description: Optional[str] = None,
    ) -> ModelVersionArtifact:
        """ """
        return cls(ModelVersion(), description)

    def _get_delegate(self) -> ModelVersion:
        return self.model

    def with_algorithm(self, name: Optional[str]) -> ModelVersionArtifact:
        """Accepts an optional str and assigns it to the ModelVersion.

        :param name: The model's algorithm
        :return: ModelVersionArtifact
        """
        self._get_delegate().with_algorithm(name)
        return self

    def with_status(self, status: Union[Enum, str] = "EXPERIMENTATION") -> ModelVersionArtifact:
        """Accepts either an Enum or str, then checks if the
        option is valid. Then assigns the status to the ModelVersion.

        :param type: The model status
        :return: ModelVersionArtifact
        """
        if not self._valid_option(status):
            raise ValueError(f"The status of {status} isn't supported.")
        self._get_delegate().with_status(status.value) if isinstance(
            status, Enum
        ) else self._get_delegate().with_status(status)
        return self

    def with_type(self, type: Union[Enum, str] = "OTHER") -> ModelVersionArtifact:
        """Accepts either an Enum or str, then checks if the
        option is valid. Then assigns the type to the ModelVersion.

        :param type: The model type
        :return: ModelVersionArtifact
        """
        if not self._valid_option(type):
            raise ValueError(f"The type of {type} isn't supported.")
        self._get_delegate().with_type(type.value) if isinstance(type, Enum) else self._get_delegate().with_type(type)
        return self

    def _valid_option(self, option: Union[Enum, str]) -> bool:
        """Accepts either an Enum or str. Then checks if the option is a
        valid Enum option or if the Str in is the model types or model
        version statuses.

        :param option: An Enum or str
        :return: Bool
        """
        if isinstance(option, Enum):
            return True
        elif option.upper() in ModelType.__members__ or option.upper() in ModelVersionStatus.__members__:
            return True
        else:
            return False
