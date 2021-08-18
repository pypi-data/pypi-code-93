from typing import Optional

from tecton.data_sources.base_data_source import BaseStreamDataSource
from tecton_proto.args import data_source_pb2
from tecton_proto.args import virtual_data_source_pb2
from tecton_spark import function_serialization
from tecton_spark.time_utils import strict_pytimeparse


class KafkaDSConfig(BaseStreamDataSource):
    """
    Configuration used to reference a Kafka stream.

    The KafkaDSConfig class is used to create a reference to a Kafka stream.

    This class used as an input to a :class:`VirtualDataSource`'s parameter ``batch_config``. This class is not
    a Tecton Primitive: it is a grouping of parameters. Declaring this class alone will not register a data source.
    Instead, declare a VirtualDataSource that takes this configuration class as an input.
    """

    def __init__(
        self,
        kafka_bootstrap_servers: str,
        topics: str,
        raw_stream_translator,
        timestamp_key: str,
        default_watermark_delay_threshold: str = None,
        options=None,
        ssl_keystore_location: Optional[str] = None,
        ssl_keystore_password_secret_id: Optional[str] = None,
    ):
        """
        Instantiates a new KafkaDSConfig.

        :param kafka_bootstrap_servers: A comma-separated list of the Kafka bootstrap server addresses. Passed directly
                                        to the Spark ``kafka.bootstrap.servers`` option.
        :param topics: A comma-separated list of Kafka topics to subscribe to. Passed directly to the Spark ``subscribe``
                       option.
        :param raw_stream_translator: Python user defined function f(DataFrame) -> DataFrame that takes in raw
                                      Pyspark data source DataFrame and translates it to the DataFrame to be
                                      consumed by the Feature View. See an example of
                                      raw_stream_translator in the `User Guide`_.
        :param timestamp_key: Name of the column containing timestamp for watermarking.
        :param default_watermark_delay_threshold: (Optional) Watermark time interval, e.g: "30 minutes"
        :param options: (Optional) A map of additional Spark readStream options
        :param ssl_keystore_location: An S3 URI that points to the keystore file that should be used for SSL brokers.
            Example: ``s3://tecton-${cluster_name}/internal/intermediate-data/kafka_client_keystore.jks``
        :param ssl_keystore_password_secret_id: The config key for the password for the Keystore.
            Should start with ``SECRET_``, example: ``SECRET_KAFKA_PRODUCTION``.

        :return: A KafkaDSConfig class instance.

        .. _User Guide: https://docs.tecton.ai/v2/overviews/framework/data_sources.html
        """
        self._args = args = data_source_pb2.KafkaDataSourceArgs()
        args.kafka_bootstrap_servers = kafka_bootstrap_servers
        args.topics = topics
        args.raw_stream_translator.CopyFrom(function_serialization.to_proto(raw_stream_translator))
        args.timestamp_key = timestamp_key
        if default_watermark_delay_threshold:
            args.default_watermark_delay_threshold.FromSeconds(strict_pytimeparse(default_watermark_delay_threshold))
        for key in sorted((options or {}).keys()):
            option = data_source_pb2.Option()
            option.key = key
            option.value = options[key]
            args.options.append(option)
        if ssl_keystore_location:
            args.ssl_keystore_location = ssl_keystore_location
        if ssl_keystore_password_secret_id:
            args.ssl_keystore_password_secret_id = ssl_keystore_password_secret_id

    def _merge_stream_args(self, virtual_data_source_args: virtual_data_source_pb2.VirtualDataSourceArgs):
        virtual_data_source_args.kafka_ds_config.CopyFrom(self._args)
