import ssl

from channels_integrations import new_order_pb2
from confluent_kafka.schema_registry.protobuf import ProtobufDeserializer
from confluent_kafka.serialization import SerializationContext

from .managers import LoaferManager
from loafer.ext.kafka.message_translators import KafkaMessageTranslator
from loafer.ext.kafka.routes import KafkaRoute

context = ssl.create_default_context()


class ProtobufSchemaMessageTranslator(KafkaMessageTranslator):
    def __init__(self, message_type):
        self.deserializer = ProtobufDeserializer(message_type)

    def translate(self, message):
        translated = super().translate(message)

        ctx = SerializationContext(translated["metadata"]["topic"], "value")
        translated["content"] = self.deserializer(translated["content"], ctx)

        return translated


provider_options = {
    "bootstrap_servers": "pkc-4nym6.us-east-1.aws.confluent.cloud:9092",
    "sasl_mechanism": "PLAIN",
    "security_protocol": "SASL_SSL",
    "sasl_plain_username": "S45TOSINLWDJ6CFD",
    "sasl_plain_password": "afW5z25UOvvFokQJy+iLMwtON9NbWJQ+GGawlgFk79iJ/O/Ya7HofN1sjN7PSv2S",
    "group_id": "mygroup87473",
    "auto_offset_reset": "earliest",
    "ssl_context": context,
    "options": {
        "max_records": 50,
        "timeout_ms": 10000,
    },
    "retry_topic": lambda t, n: t if n < 5 else "dev__retry__channels__new_order__received"
}


class Handler:
    async def handle(self, *args):
        return False


routes = (
    KafkaRoute(
        "dev__channels__new_order__received",
        provider_options,
        handler=Handler(),
        message_translator=ProtobufSchemaMessageTranslator(new_order_pb2.NewOrder),
    ),
)

manager = LoaferManager(routes)
manager.run()
