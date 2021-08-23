from dataclasses import dataclass


@dataclass(frozen=True)
class KafkaDeserializer:
    """Kafka Deserializer."""

    name: str
    """Name of the deserializer."""


JSON_DESERIALIZER = KafkaDeserializer(
    "io.atoti.loading.kafka.impl.serialization.JsonDeserializer"
)
"""Core JSON deserializer.

Each JSON object corresponds to a row of the table, keys of the JSON object must match columns of the table.
"""
