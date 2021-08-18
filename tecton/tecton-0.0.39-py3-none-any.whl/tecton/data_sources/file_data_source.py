from collections.abc import Callable
from typing import Optional

from pyspark.sql.types import StructType

from tecton.data_sources import base_data_source
from tecton_proto.args.data_source_pb2 import FileDataSourceArgs
from tecton_proto.args.virtual_data_source_pb2 import VirtualDataSourceArgs
from tecton_spark import function_serialization
from tecton_spark.spark_schema_wrapper import SparkSchemaWrapper


class FileDSConfig(base_data_source.BaseBatchDataSource):
    """
    Configuration used to reference a file or directory (S3, etc.)

    The FileDSConfig class is used to create a reference to a file or directory of files in S3,
    HDFS, or DBFS.

    The schema of the data source is inferred from the underlying file(s). It can also be modified using the
    ``raw_batch_translator`` parameter.

    This class used as an input to a :class:`VirtualDataSource`'s parameter ``batch_config``. This class is not
    a Tecton Primitive: it is a grouping of parameters. Declaring this class alone will not register a data source.
    Instead, declare a VirtualDataSource that takes this configuration class as an input.
    """

    def __init__(
        self,
        uri: str,
        file_format: str,
        convert_to_glue_format=False,
        timestamp_column_name: Optional[str] = None,
        timestamp_format: Optional[str] = None,
        raw_batch_translator: Optional[Callable] = None,
        schema_uri: Optional[str] = None,
        schema_override: Optional[StructType] = None,
    ):
        """
        Instantiates a new FileDSConfig.

        :param uri: S3 or HDFS path to file(s).
        :param file_format: File format. "json", "parquet", or "csv"
        :param convert_to_glue_format: Converts all schema column names to lowercase.
        :param timestamp_column_name: Name of timestamp column.
        :param timestamp_format: (Optional) Format of string-encoded timestamp column (e.g. "yyyy-MM-dd'T'hh:mm:ss.SSS'Z'")
        :param raw_batch_translator: Python user defined function f(DataFrame) -> DataFrame that takes in raw
                                     Pyspark data source DataFrame and translates it to the DataFrame to be
                                     consumed by the Feature View. See an example of
                                     raw_batch_translator in the `User Guide`_.
        :param schema_uri: (optional) A file or subpath of "uri" that can be used for fast schema inference.
                           This is useful for deeply nested data sources with many small files.
        :param schema_override: (Optional) a pyspark.sql.types.StructType object that will be used as the schema when
                                reading from the file. If omitted, the schema will be inferred automatically.

        :return: A FileDSConfig class instance.

        .. _User Guide: https://docs.tecton.ai/v2/overviews/framework/data_sources.html
        """
        self._args = prepare_file_ds_args(
            uri=uri,
            file_format=file_format,
            convert_to_glue_format=convert_to_glue_format,
            timestamp_column_name=timestamp_column_name,
            timestamp_format=timestamp_format,
            raw_batch_translator=raw_batch_translator,
            schema_uri=schema_uri,
            schema_override=schema_override,
        )

    def _merge_batch_args(self, virtual_data_source_args: VirtualDataSourceArgs):
        virtual_data_source_args.file_ds_config.CopyFrom(self._args)


def prepare_file_ds_args(
    *,
    uri: str,
    file_format: str,
    convert_to_glue_format: bool,
    timestamp_column_name: Optional[str],
    timestamp_format: Optional[str],
    raw_batch_translator: Optional[Callable],
    schema_uri: Optional[str],
    schema_override: Optional[StructType],
) -> FileDataSourceArgs:
    args = FileDataSourceArgs()
    args.uri = uri
    args.file_format = file_format
    args.convert_to_glue_format = convert_to_glue_format
    if schema_uri is not None:
        args.schema_uri = schema_uri
    if raw_batch_translator is not None:
        args.raw_batch_translator.CopyFrom(function_serialization.to_proto(raw_batch_translator))
    if timestamp_column_name:
        args.timestamp_column_name = timestamp_column_name
    if timestamp_format:
        args.timestamp_format = timestamp_format
    if schema_override:
        args.schema_override.CopyFrom(SparkSchemaWrapper(schema_override).to_proto())

    return args
