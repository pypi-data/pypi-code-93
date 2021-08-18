import pendulum
import pytimeparse

from tecton._internals import errors
from tecton.feature_packages.feature_type import FeatureType
from tecton_proto.data import feature_types_pb2


class Temporal(FeatureType):
    def to_proto(self) -> feature_types_pb2.FeatureType:
        wrapper = feature_types_pb2.FeatureType()
        wrapper.temporal.CopyFrom(self._proto)
        return wrapper

    @classmethod
    def create(cls, timestamp_key: str, serving_ttl: str, data_lookback: str):
        """
        Create a new Temporal feature type

        :param timestamp_key: Column name of the time key that will be used for determining the most recent value that
                will be persisted in the Feature Store and subsequently served. Must be a Spark timestamp.
        :param serving_ttl: How much time after a feature's timestamp, the corresponding feature value is eligible
                            to be served by the online feature store. E.g. if serving_ttl is "30 minutes" and a feature
                            value has a timestamp of 1:00pm, that feature will only be served by the online feature
                            store until the raw data is materialized till 1:30pm.
                            This behavior is mimicked when generating data from the offline feature store.
                            Note, that approximate time ranges are not supported (e.g. months or years).
        How much time after a feature value’s timestamp the corresponding feature value is eligible
                            to be served by the online feature store. E.g. if serving_ttl is "20 minutes" and a feature
                            value has a timestamp of 1:00pm, that value will only be served by the online feature store
                            until 1:20pm. This behavior is mimicked when generating data from the offline feature store.
                            Note, that approximate time ranges are not supported (e.g. months or years).
        :param data_lookback: How long to look back in raw data time from the current position. This will
                              apply the time range filter to the temp views which are passed to the transformer functions
        """
        proto = feature_types_pb2.Temporal()
        proto.time_key = timestamp_key
        proto.serving_ttl.seconds = pytimeparse.parse(serving_ttl)
        proto.data_lookback.seconds = pytimeparse.parse(data_lookback)

        obj = cls(proto)
        return obj

    @staticmethod
    def _from_feature_type_proto(feature_type):
        if not feature_type.HasField("temporal"):
            which = feature_type.WhichOneof("specific_type")
            if which is None:
                return None
            raise ValueError(f"Unsupported temporal feature deserialization '{which}'")
        return Temporal(feature_type.temporal)

    @property
    def timestamp_key(self) -> str:
        return self._proto.time_key

    @property
    def serving_ttl(self) -> pendulum.Duration:
        return pendulum.Duration(seconds=self._proto.serving_ttl.ToSeconds())

    @property
    def data_lookback(self) -> pendulum.Duration:
        return pendulum.Duration(seconds=self._proto.data_lookback.ToSeconds())

    def validate(self, view_schema, raw_feature_names, is_streaming_ds):
        """Runs validity checks on the feature definition, raising an error if any fail."""
        try:
            time_key_type = view_schema.spark_type(self.timestamp_key)
        except ValueError as e:
            raise errors.ERROR_RESOLVING_COLUMN(self.timestamp_key)
        if time_key_type != "timestamp":
            raise errors.TIME_KEY_TYPE_ERROR(self.timestamp_key, time_key_type)
        # Validate serving_ttl is positive, and that it doesn't contain
        # unsupported ambiguous durations (months & years)
        if self.serving_ttl <= pendulum.Duration() or self.serving_ttl.months > 0 or self.serving_ttl.years > 0:
            raise errors.DURATION_NEGATIVE_OR_AMBIGUOUS("serving_ttl", self.serving_ttl)
        if self.data_lookback <= pendulum.Duration() or self.data_lookback.months > 0 or self.data_lookback.years > 0:
            raise errors.DURATION_NEGATIVE_OR_AMBIGUOUS("data_lookback", self.data_lookback)
