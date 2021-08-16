from aide_sdk.inference.inference_manager import InferenceManager
from aide_sdk.inference.aideoperator import AideOperator
from aide_sdk.manifests.manifest import load
from aide_sdk.messaging.config import QueueConfiguration, ElasticConfiguration, PacsConfiguration
from aide_sdk.messaging.consumer import ModelConsumer
from aide_sdk.messaging.pacs_client import PacsClient
from aide_sdk.messaging.publisher import ModelPublisher
from aide_sdk.messaging.elastic_api import ElasticWebAPIClient


class AideApplication:
    @staticmethod
    def start(operator: AideOperator) -> None:
        manifest = load()
        consumer_config = QueueConfiguration(queue=manifest.get_queue_name())
        publisher_config = QueueConfiguration(queue="input")
        elastic_config = ElasticConfiguration()
        pacs_config = PacsConfiguration()

        model_consumer = ModelConsumer(consumer_config)
        model_publisher = ModelPublisher(publisher_config)
        elastic_client = ElasticWebAPIClient(elastic_config)
        pacs_client = PacsClient(pacs_config)

        manager = InferenceManager(model_consumer, model_publisher, operator, elastic_client, pacs_client)
        manager.execute()
