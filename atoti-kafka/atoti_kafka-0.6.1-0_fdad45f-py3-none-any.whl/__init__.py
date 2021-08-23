"""Plugin to load real time Kafka streams into atoti tables.

This package is required to use :meth:`atoti.table.Table.load_kafka`.
"""

from ._custom import create_deserializer
from ._deserializer import JSON_DESERIALIZER as _JSON_DESERIALIZER

JSON_DESERIALIZER = _JSON_DESERIALIZER
"""Core JSON deserializer.

Each JSON object corresponds to a row of the table, keys of the JSON object must match columns of the table.
"""

__all__ = ["create_deserializer", "JSON_DESERIALIZER"]
