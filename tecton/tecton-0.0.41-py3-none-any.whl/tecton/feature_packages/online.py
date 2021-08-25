from tecton.feature_packages.feature_type import FeatureType
from tecton_proto.data import feature_types_pb2


class Online(FeatureType):
    def __init__(self, proto):
        self._proto = proto

    @classmethod
    def create(cls):
        proto = feature_types_pb2.Online(no_op=True)
        obj = cls(proto)
        return obj

    def to_proto(self) -> feature_types_pb2.FeatureType:
        wrapper = feature_types_pb2.FeatureType()
        wrapper.online.CopyFrom(self._proto)
        return wrapper

    def validate(self, view_schema, raw_feature_names, is_streaming_ds):
        """Runs validity checks on the feature definition, raising an error if any fail."""
        return

    @property
    def timestamp_key(self) -> str:
        assert False, "OnlineFeaturePackages do not have a timestamp_key"
