from typing import Dict
from typing import List
from typing import Optional

from tecton.data_sources.base_data_source import BaseStreamDataSource
from tecton_proto.args import data_source_pb2
from tecton_proto.args import virtual_data_source_pb2
from tecton_spark import data_source_helper
from tecton_spark import function_serialization
from tecton_spark.time_utils import strict_pytimeparse


class KinesisDSConfig(BaseStreamDataSource):
    """
    Configuration used to reference a Kinesis stream.

    The KinesisDSConfig class is used to create a reference to an AWS Kinesis stream.

    This class used as an input to a :class:`VirtualDataSource`'s parameter ``batch_config``. This class is not
    a Tecton Primitive: it is a grouping of parameters. Declaring this class alone will not register a data source.
    Instead, declare a VirtualDataSource that takes this configuration class as an input.
    """

    def __init__(
        self,
        stream_name: str,
        region: str,
        raw_stream_translator,
        timestamp_key: str,
        default_initial_stream_position: str,
        default_watermark_delay_threshold: str,
        deduplication_columns: List[str] = None,
        options=None,
    ):
        """
        Instantiates a new KinesisDSConfig.

        :param stream_name: Name of the Kinesis stream.
        :param region: AWS region of the stream, e.g: "us-west-2".
        :param raw_stream_translator: Python user defined function f(DataFrame) -> DataFrame that takes in raw
                                      Pyspark data source DataFrame and translates it to the DataFrame to be
                                      consumed by the Feature View. See an example of
                                      raw_stream_translator in the `User Guide`_.
        :param timestamp_key: Name of the column containing timestamp for watermarking.
        :param default_initial_stream_position: Initial position in stream, e.g: "latest" or "trim_horizon".
                                                More information available in `Spark Kinesis Documentation`_.
        :param default_watermark_delay_threshold: Watermark time interval, e.g: "30 minutes"
        :param deduplication_columns: (Optional) Columns in the stream data that uniquely identify data records.
                                        Used for de-duplicating.
        :param options: (Optional) A map of additional Spark readStream options

        :return: A KinesisDSConfig class instance.

        .. _User Guide: https://docs.tecton.ai/v2/overviews/framework/data_sources.html
        .. _Spark Kinesis Documentation: https://spark.apache.org/docs/latest/streaming-kinesis-integration.html
        """

        self._args = prepare_kinesis_ds_args(
            stream_name=stream_name,
            region=region,
            raw_stream_translator=raw_stream_translator,
            timestamp_key=timestamp_key,
            default_initial_stream_position=default_initial_stream_position,
            default_watermark_delay_threshold=default_watermark_delay_threshold,
            deduplication_columns=deduplication_columns,
            options=options,
        )

    def _merge_stream_args(self, virtual_data_source_args: virtual_data_source_pb2.VirtualDataSourceArgs):
        virtual_data_source_args.kinesis_ds_config.CopyFrom(self._args)


def prepare_kinesis_ds_args(
    *,
    stream_name: str,
    region: str,
    raw_stream_translator,
    timestamp_key: str,
    default_initial_stream_position: Optional[str],
    default_watermark_delay_threshold: Optional[str],
    deduplication_columns: Optional[List[str]],
    options: Optional[Dict[str, str]],
):
    args = data_source_pb2.KinesisDataSourceArgs()
    args.stream_name = stream_name
    args.region = region
    args.raw_stream_translator.CopyFrom(function_serialization.to_proto(raw_stream_translator))
    args.timestamp_key = timestamp_key
    if default_initial_stream_position:
        args.default_initial_stream_position = data_source_helper.INITIAL_STREAM_POSITION_STR_TO_ENUM[
            default_initial_stream_position
        ]
    if default_watermark_delay_threshold:
        args.default_watermark_delay_threshold.FromSeconds(strict_pytimeparse(default_watermark_delay_threshold))
    if deduplication_columns:
        for column_name in deduplication_columns:
            args.deduplication_columns.append(column_name)
    options_ = options or {}
    for key in sorted(options_.keys()):
        option = data_source_pb2.Option()
        option.key = key
        option.value = options_[key]
        args.options.append(option)

    return args
