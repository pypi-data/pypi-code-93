import abc

from elasticsearch_dsl import connections
from elasticsearch.exceptions import ConnectionError, RequestError
from aide_sdk.messaging.config import ElasticConfiguration
from aide_sdk.logger.logger import LogManager


logger = LogManager._get_audit_logger()


class AbstractElasticAPIClient(abc.ABC):
    class ElasticBaseError(Exception):
        pass

    class ElasticServerError(ElasticBaseError):
        pass

    @abc.abstractmethod
    def add_execution(self, execution: str, correlation_id: str):
        raise NotImplementedError


class ElasticBaseError(Exception):
    pass


class ElasticServerError(ElasticBaseError):
    pass


class ElasticWebAPIClient(AbstractElasticAPIClient):

    def __init__(self, config: ElasticConfiguration):
        self.host = config.host
        self.username = config.username
        self.password = config.password
        self.port = config.port
        self.scheme = config.scheme
        self.verify_certs = config.verify_certs
        self.create_connection()

    def create_connection(self):
        try:
            connections.create_connection(
                hosts=[self.host],
                http_auth="{}:{}".format(self.username, self.password),
                verify_certs=self.verify_certs,
                scheme=self.scheme,
                port=self.port,
            )
        except ConnectionError as e:
            url = self.host
            message = f"Error connecting to {url} {e.info}"
            logger.exception(message)
            raise

    def add_execution(self, execution: str, correlation_id: str):
        self._add(execution)
        logger.info('Saved to elastic message %s, collaboration_id %s', execution, correlation_id)

    def _add(self, body):
        try:
            connection = self._check_cluster_health()
            connection.index(body=body, doc_type='_doc', index="executions")
        except self.ElasticBaseError as e:
            logger.exception(str(e))
        except ConnectionError as e:
            url = self.host
            message = f"Error connecting to {url} {e.info}"
            logger.exception(message)
        except RequestError as e:
            message = f"Error ({e.error}): {e.info['error']['reason']}"
            logger.exception(message)
        except Exception as e:
            logger.exception(str(e))

    def _check_cluster_health(self):
        connection = connections.get_connection()
        health = connection.cluster.health()
        status = health["status"]
        if status not in ("green", "yellow"):
            raise ElasticServerError(f"status {status} not green or yellow")
        return connection
