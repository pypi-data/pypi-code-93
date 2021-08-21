from microservice_template_core.tools.logger import get_logger
from microservice_template_core.settings import ServiceConfig, KafkaConfig
from kafka import KafkaConsumer

logger = get_logger()


class KafkaConsumeMessages(object):
    def __init__(self, kafka_topic):
        self.kafka_topic = kafka_topic

    def start_consumer(self):
        """
        Start consumer
        """

        logger.debug(f"Initializing Kafka Consumer - {ServiceConfig.SERVICE_NAME}")
        consumer = KafkaConsumer(
            self.kafka_topic,
            group_id=ServiceConfig.SERVICE_NAME,
            bootstrap_servers=KafkaConfig.KAFKA_SERVERS
        )

        return consumer
