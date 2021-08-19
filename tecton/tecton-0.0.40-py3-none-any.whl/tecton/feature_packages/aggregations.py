from typing import List

from google.protobuf.duration_pb2 import Duration

from tecton._internals import errors
from tecton.feature_packages.feature_type import FeatureType
from tecton_proto.common.aggregation_function_pb2 import AggregationFunction
from tecton_proto.data import feature_types_pb2
from tecton_spark.time_utils import strict_pytimeparse

MIN_SLIDE_PERIOD_SECONDS = 60
MIN_AGG_WINDOW_SECONDS = 60
MAX_STREAMING_AGG_WINDOW_SECONDS = 3600 * 24 * 366


class TrailingTimeWindowAggregationBuilder(FeatureType):
    def __init__(self, proto: feature_types_pb2.TrailingTimeWindowAggregation):
        super().__init__(proto)
        # Initialized in create() method
        self._aggregation_slide_period = None
        self._is_continuous = None

    def to_proto(self) -> feature_types_pb2.FeatureType:
        wrapper = feature_types_pb2.FeatureType()
        wrapper.trailing_time_window_aggregation.CopyFrom(self._proto)
        return wrapper

    @classmethod
    def create(cls, timestamp_key, aggregation_slide_period):
        """
        Create a new time window aggregation

        :param timestamp_key: Column name of the time key that will be used in aggregation. The column must be of type Spark timestamp.
        :param aggregation_slide_period: How often Tecton (re)computes the aggregation. Example format: `"7days"`.
        """
        aggregation = feature_types_pb2.TrailingTimeWindowAggregation()
        aggregation.time_key = timestamp_key
        try:
            if isinstance(aggregation_slide_period, Duration):
                slide_period_seconds = aggregation_slide_period.ToSeconds()
            else:
                slide_period_seconds = strict_pytimeparse(aggregation_slide_period)
            aggregation.is_continuous = slide_period_seconds == 0
            aggregation.aggregation_slide_period.FromSeconds(slide_period_seconds)
        except TypeError:
            raise errors.TIME_PARSING_ERROR("aggregation_slide_period", aggregation_slide_period)

        obj = cls(aggregation)
        # cached for constructing output_feature_name in the add() method
        obj._aggregation_slide_period = aggregation_slide_period
        return obj

    @staticmethod
    def _from_feature_type_proto(feature_type):
        if not feature_type.HasField("trailing_time_window_aggregation"):
            which = feature_type.WhichOneof("specific_type")
            if which is None:
                return None
            raise ValueError(f"Unsupported time aggregation on deserialization '{which}'")
        return TrailingTimeWindowAggregationBuilder(feature_type.trailing_time_window_aggregation)

    def add(
        self,
        feature_to_aggregate,
        aggregation_function,
        aggregation_windows,
        output_feature_name_override=None,
    ):
        """
        Add a feature to be aggregated

        :param feature_to_aggregate: Column name of a feature we are aggregating
        :param aggregation_function: One of the built-in aggregation functions (`'count'`, `'sum'`, `'mean'`, `'min'`, `'max'`).
        :param aggregation_windows: Length of time we are aggregating over.
            Example formats: `"30days"`, `["8hours", "30days", "365days"]`.
        """

        if not isinstance(aggregation_windows, list):
            aggregation_windows = [aggregation_windows]

        for aggregation_window in aggregation_windows:
            feature = self._proto.features.add()
            feature.input_feature_name = feature_to_aggregate
            if output_feature_name_override is None:
                feature.output_feature_name = TrailingTimeWindowAggregationBuilder._construct_output_feature_name(
                    feature_to_aggregate, aggregation_function, aggregation_window, self._aggregation_slide_period
                )
            else:
                feature.output_feature_name = output_feature_name_override

            try:
                feature.function = TrailingTimeWindowAggregationBuilder._get_aggregation_enum_type(aggregation_function)
            except ValueError:
                raise errors.TTWA_UNSUPPORTED_AGGREGATION("aggregation_function", aggregation_function)

            try:
                feature.window.FromSeconds(strict_pytimeparse(aggregation_window))
            except TypeError:
                raise errors.TIME_PARSING_ERROR("aggregation_window", aggregation_window)

        return self

    @property
    def timestamp_key(self):
        return self._proto.time_key

    @property
    def slide_period_seconds(self):
        return self._proto.aggregation_slide_period.ToSeconds()

    @property
    def features(self) -> List[str]:
        feature_names = [f.output_feature_name for f in self._proto.features]
        return [f for f in feature_names if f != self._proto.time_key]

    @staticmethod
    def _get_aggregation_enum_type(aggregation_function_name):
        return AggregationFunction.Value("AGGREGATION_FUNCTION_" + aggregation_function_name.upper())

    @staticmethod
    def _get_aggregation_function_name(aggregation_function_enum):
        return AggregationFunction.Name(aggregation_function_enum).replace("AGGREGATION_FUNCTION_", "").lower()

    @staticmethod
    def _construct_output_feature_name(
        feature_to_aggregate, aggregation_function, aggregation_window, aggregation_slide_period
    ):
        # Time intervals (aggregation_window, aggregation_slide_period) may contain spaces,
        # so we remove spaces from the name
        return f"{feature_to_aggregate}_{aggregation_function}_{aggregation_window}_{aggregation_slide_period}".replace(
            " ", ""
        )

    def validate(self, view_schema, raw_feature_names, is_streaming_ds):
        """Runs validity checks on the aggregation definition, raising an error if any fail."""

        if len(self._proto.features) == 0:
            raise errors.TTWA_EMPTY_FEATURES

        time_key = self._proto.time_key
        try:
            time_key_type = view_schema.spark_type(time_key)
        except ValueError as e:
            raise errors.ERROR_RESOLVING_COLUMN(time_key)
        if time_key_type != "timestamp":
            raise errors.TIME_KEY_TYPE_ERROR(time_key, time_key_type)

        remaining_raw_feature_names = set(raw_feature_names)
        for feature in self._proto.features:
            remaining_raw_feature_names.discard(feature.input_feature_name)
            try:
                view_schema.tecton_type(feature.input_feature_name)
            except ValueError as e:
                raise errors.ERROR_RESOLVING_COLUMN(feature.input_feature_name)

            input_feature_type = view_schema.spark_type(feature.input_feature_name)
            if (
                feature.function == AggregationFunction.AGGREGATION_FUNCTION_SUM
                or feature.function == AggregationFunction.AGGREGATION_FUNCTION_MEAN
            ) and (input_feature_type == "string" or input_feature_type == "bool"):
                raise errors.TTWA_INVALID_NUMERIC_AGGREGATION(
                    self._get_aggregation_function_name(feature.function),
                    feature.input_feature_name,
                    input_feature_type,
                )

            if feature.window.ToSeconds() % self.slide_period_seconds != 0:
                raise errors.TTWA_WINDOW_LENGTH_ERROR(feature.output_feature_name, self._aggregation_slide_period)

        if len(remaining_raw_feature_names) > 0:
            raise errors.TTWA_UNREFERENCED_COLUMNS(remaining_raw_feature_names)

        if self.slide_period_seconds < MIN_SLIDE_PERIOD_SECONDS:
            raise errors.TTWA_SLIDE_PERIOD_TOO_SMALL(self.slide_period_seconds, MIN_SLIDE_PERIOD_SECONDS)

        for feature in self._proto.features:
            if feature.window.ToSeconds() < MIN_AGG_WINDOW_SECONDS:
                raise errors.TTWA_AGG_WINDOW_TOO_SMALL(feature, MIN_AGG_WINDOW_SECONDS)
            if is_streaming_ds and feature.window.ToSeconds() > MAX_STREAMING_AGG_WINDOW_SECONDS:
                raise errors.TTWA_AGG_WINDOW_TOO_LARGE(feature, MAX_STREAMING_AGG_WINDOW_SECONDS)
