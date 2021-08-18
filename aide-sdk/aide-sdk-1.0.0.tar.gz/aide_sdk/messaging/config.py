import os
from distutils.util import strtobool


class QueueConfiguration:
    def __init__(self, username="", password="", host="", port="", model_exchange="", output_exchange="", model_routing_key="", output_routing_key="", queue=""):
        self.username = username if username != "" else os.getenv("RABBITMQ_USERNAME", "admin")
        self.password = password if password != "" else os.getenv("RABBITMQ_PASSWORD", "admin")
        self.host = host if host != "" else os.getenv("RABBITMQ_HOST", "localhost")
        self.port = port if port != "" else os.getenv("RABBITMQ_PORT", 5672)
        self.model_exchange = model_exchange if model_exchange != "" else os.getenv("RABBITMQ_MODEL_EXCHANGE", "model-exchange")
        self.output_exchange = output_exchange if output_exchange != "" else os.getenv("RABBITMQ_OUTPUT_EXCHANGE", "output-exchange")
        self.model_routing_key = model_routing_key if model_routing_key != "" else os.getenv("RABBITMQ_MODEL_ROUTING_KEY", "")
        self.output_routing_key = output_routing_key if output_routing_key != "" else os.getenv("RABBITMQ_OUTPUT_ROUTING_KEY", "input")
        self.queue = queue


class ElasticConfiguration:
    def __init__(self, username=None,
                 password=None,
                 host=None,
                 port=None,
                 verify_certs=None,
                 scheme=None):
        self.username = username or os.getenv("ELASTICSEARCH_USERNAME", "admin")
        self.password = password or os.getenv("ELASTICSEARCH_PASSWORD", "admin")
        self.host = host or os.getenv("ELASTICSEARCH_HOST", "localhost:9200")
        self.port = port or int(os.getenv("ELASTICSEARCH_PORT", 0)) or 443
        self.verify_certs = verify_certs or bool(strtobool(os.environ.get("ELASTICSEARCH_VERIFY_CERTS", 'false')))
        self.scheme = scheme or os.environ.get("ELASTICSEARCH_SCHEME", "http")


class PacsConfiguration:
    def __init__(self, ae_title=None,
                 host=None,
                 port=None,
                 dimse_timeout=None):
        self.ae_title = ae_title or os.getenv("PACS_AE_TITLE", "ORTHANC")
        self.host = host or os.getenv("PACS_HOST", "localhost")
        self.port = port or int(os.getenv("PACS_PORT", 0)) or 4242
        self.dimse_timeout = dimse_timeout or int(os.getenv("PACS_DIMSE_TIMEOUT", 30))
