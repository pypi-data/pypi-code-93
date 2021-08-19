from microservice_template_core.tools.logger import get_logger
from microservice_template_core.settings import KafkaConfig
from kafka import KafkaProducer
import json
import traceback
from prometheus_client import Summary

logger = get_logger()


class KafkaProduceMessages(object):
    KAFKA_PRODUCER_START = Summary('kafka_producer_start_latency_seconds', 'Time spent starting Kafka producer')
    KAFKA_PRODUCE_MESSAGES = Summary('kafka_produce_messages_latency_seconds', 'Time spent processing produce to Kafka')

    def __init__(self):
        self.producer = self.init_producer()

    @staticmethod
    @KAFKA_PRODUCER_START.time()
    def init_producer():
        try:
            producer = KafkaProducer(
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                bootstrap_servers=KafkaConfig.KAFKA_SERVERS
            )

            return producer
        except Exception as err:
            logger.error(
                msg=f"Can`t connect to Kafka cluster - {KafkaConfig.KAFKA_SERVERS}\nError: {err}\nTrace: {traceback.format_exc()}"
            )
            return None

    @KAFKA_PRODUCE_MESSAGES.time()
    def produce_message(self, topic, message):
        logger.debug(
            msg=f"Start producing message to topic - {topic}\nBody: {message}"
        )
        try:
            self.producer.send(topic, message)
            logger.debug(
                msg=f"Successfully pushed message to - {topic}"
            )
        except Exception as err:
            logger.error(
                msg=f"Can`t push message to - {topic}\nBody: {message}\nError: {err}\nTrace: {traceback.format_exc()}"
            )
