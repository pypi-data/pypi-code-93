from __future__ import annotations

from typing import Mapping, Optional

from atoti._java_api import JavaApi
from atoti._sources import DataSource
from atoti.table import Table

from ._custom import CustomDeserializer
from ._deserializer import JSON_DESERIALIZER, KafkaDeserializer


class KafkaDataSource(DataSource):
    """Kafka data source."""

    def __init__(self, java_api: JavaApi):
        """Init."""
        super().__init__(java_api, "KAFKA")

    def load_kafka_into_table(
        self,
        table: Table,
        *,
        bootstrap_servers: str,
        topic: str,
        group_id: str,
        value_deserializer: KafkaDeserializer,
        batch_duration: int,
        consumer_config: Mapping[str, str],
    ):
        """Consume a Kafka topic and stream its records in an existing table."""
        params = {
            "bootstrapServers": bootstrap_servers,
            "topic": topic,
            "consumerGroupId": group_id,
            "keyDeserializerClass": "org.apache.kafka.common.serialization.StringDeserializer",
            "batchDuration": batch_duration,
            "additionalParameters": consumer_config,
        }
        if isinstance(value_deserializer, CustomDeserializer):
            params["pythonValueDeserializer"] = value_deserializer
            params["batchSize"] = value_deserializer.batch_size
        else:
            params["valueDeserializerClass"] = value_deserializer.name
        self.load_data_into_table(
            table.name,
            scenario_name=None,
            source_params=params,
        )


def load_kafka(
    self: Table,
    bootstrap_server: str,
    topic: str,
    *,
    group_id: str,
    batch_duration: int = 1000,
    consumer_config: Optional[Mapping[str, str]] = None,
    deserializer: KafkaDeserializer = JSON_DESERIALIZER,
):  # noqa: D417
    """Consume a Kafka topic and stream its records in the table.

    Note:
        This method requires the :mod:`atoti-kafka <atoti_kafka>` plugin.

    The records' key deserializer default to `StringDeserializer <https://kafka.apache.org/21/javadoc/org/apache/kafka/common/serialization/StringDeserializer.html>`__.

    Args:
        bootstrap_server: ``host[:port]`` that the consumer should contact to bootstrap initial cluster metadata.
        topic: Topic to subscribe to.
        group_id: The name of the consumer group to join.
        batch_duration: Milliseconds spent batching received records before publishing them to the table.
            If ``0``, received records are immediately published to the table.
            Must not be negative.
        consumer_config: Mapping containing optional parameters to set up the KafkaConsumer.
            The list of available params can be found `here <https://kafka.apache.org/10/javadoc/index.html?org/apache/kafka/clients/consumer/ConsumerConfig.html>`__.
        deserializer: Deserialize Kafka records' value to atoti table rows.
            Use :meth:`atoti_kafka.create_deserializer` to create custom ones.
    """
    KafkaDataSource(self._java_api).load_kafka_into_table(
        self,
        bootstrap_servers=bootstrap_server,
        topic=topic,
        group_id=group_id,
        value_deserializer=deserializer,
        batch_duration=batch_duration,
        consumer_config=consumer_config if consumer_config is not None else {},
    )
