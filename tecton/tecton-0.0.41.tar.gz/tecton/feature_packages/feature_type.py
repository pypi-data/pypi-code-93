from abc import ABC
from abc import abstractmethod

from tecton_proto.data import feature_types_pb2


class FeatureType(ABC):
    def __init__(self, proto):
        self._proto = proto

    @abstractmethod
    def to_proto(self) -> feature_types_pb2.FeatureType:
        pass

    @abstractmethod
    def validate(self, view_schema, raw_feature_names, is_streaming_ds):
        """Runs validity checks on the feature definition, raising an error if any fail."""

    @property
    @abstractmethod
    def timestamp_key(self) -> str:
        pass
