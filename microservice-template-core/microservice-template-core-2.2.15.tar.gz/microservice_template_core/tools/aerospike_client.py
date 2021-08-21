import aerospike
from microservice_template_core.tools.logger import get_logger
from microservice_template_core.settings import AerospikeConfig
from aerospike import predexp as predexp
from aerospike import exception as exception
from prometheus_client import Summary

logger = get_logger()


class AerospikeClient(object):
    # Prometheus Metrics
    AEROSPIKE_CONNECTIONS = Summary('aerospike_connections_latency_seconds', 'Time spent processing connect to aerospike')
    AEROSPIKE_READ = Summary('aerospike_read_latency_seconds', 'Time spent processing read from aerospike')
    AEROSPIKE_WRITE = Summary('aerospike_write_latency_seconds', 'Time spent processing write to aerospike')
    AEROSPIKE_DELETE = Summary('aerospike_delete_latency_seconds', 'Time spent processing delete from aerospike')
    AEROSPIKE_UPDATE = Summary('aerospike_update_latency_seconds', 'Time spent processing update in aerospike')
    AEROSPIKE_SCAN = Summary('aerospike_scan_latency_seconds', 'Time spent processing scan in aerospike')
    AEROSPIKE_QUERY = Summary('aerospike_query_latency_seconds', 'Time spent processing query in aerospike')
    AEROSPIKE_CREATE_INDEX = Summary('aerospike_create_index_latency_seconds', 'Time spent creating index in aerospike')

    def __init__(self, aerospike_set: str, bin_index: dict):
        self.client = self.client_aerospike()
        self.records_result = []
        self.create_index_string(aerospike_set=aerospike_set, bin_index=bin_index)

    @staticmethod
    @AEROSPIKE_CONNECTIONS.time()
    def client_aerospike():
        config = {
            'hosts': [(AerospikeConfig.AEROSPIKE_HOST, AerospikeConfig.AEROSPIKE_PORT)]
        }

        try:
            client = aerospike.client(config).connect()
            logger.info(msg=f"Connected to Aerospike - {config['hosts']}")
        except Exception as err:
            client = None
            logger.error(msg=f"failed to connect to the cluster with: {err} - {config['hosts']}")

        return client

    @AEROSPIKE_WRITE.time()
    def put_message(self, aerospike_set, aerospike_key, aerospike_message):
        key = (AerospikeConfig.AEROSPIKE_NAMESPACE, aerospike_set, aerospike_key)
        try:
            logger.info(msg=f"Add message to Aerospike: KEY - {key}")
            self.client.put(key, aerospike_message)
        except Exception as e:
            logger.error(msg=f"error: {e}")

    @AEROSPIKE_DELETE.time()
    def delete_message(self, aerospike_set, aerospike_key):
        key = (AerospikeConfig.AEROSPIKE_NAMESPACE, aerospike_set, aerospike_key)
        try:
            logger.info(msg=f"Delete message from Aerospike: KEY - {key}")
            self.client.remove(key)
        except Exception as e:
            logger.error(msg=f"error: {e}")

    @AEROSPIKE_UPDATE.time()
    def update_bin(self, aerospike_set, aerospike_key, bin_name, bin_value):
        key = (AerospikeConfig.AEROSPIKE_NAMESPACE, aerospike_set, aerospike_key)
        try:
            logger.info(msg=f"Updated bin value in Aerospike: KEY - {key}")
            self.client.append(key, bin_name, bin_value)
        except Exception as e:
            logger.error(msg=f"error: {e}")

    @AEROSPIKE_READ.time()
    def read_message(self, aerospike_set, aerospike_key):
        try:
            logger.info(msg=f'Read data from Aerospike. KEY - {aerospike_key}, SET - {aerospike_set}')
            key = (AerospikeConfig.AEROSPIKE_NAMESPACE, aerospike_set, aerospike_key)
            (key, metadata, record) = self.client.get(key)
        except Exception as err:
            logger.info(msg=f"Can`t read data from Aerospike. Return empty list of notifications for key - {aerospike_key}\nError: {err}")
            return []

        return record

    @AEROSPIKE_SCAN.time()
    def scan_keys(self, aerospike_set):
        s = self.client.scan(AerospikeConfig.AEROSPIKE_NAMESPACE, aerospike_set)
        records = []

        def callback(input_tuple):
            (_, _, record) = input_tuple
            records.append(record)
            return records

        s.foreach(callback)

        return records

    @AEROSPIKE_QUERY.time()
    def query_messages_predexps(self, aerospike_set, predexps: list):
        self.records_result = []

        q = self.client.query(AerospikeConfig.AEROSPIKE_NAMESPACE, aerospike_set)
        q.predexp(predexps)
        q.foreach(self.callback)

        return self.records_result

    @AEROSPIKE_CREATE_INDEX.time()
    def create_index_string(self, aerospike_set, bin_index: dict):
        """
        :param aerospike_set: table name
        :param bin_index: example {"alert_id": "integer"}. Possible values: "integer", "string"
        :return: None
        """

        for bin_name, bin_type in bin_index.items():
            try:
                if bin_type == 'string':
                    self.client.index_string_create(AerospikeConfig.AEROSPIKE_NAMESPACE, aerospike_set, bin_name, f'{aerospike_set}_{bin_name}_idx')
                elif bin_type == 'integer':
                    self.client.index_integer_create(AerospikeConfig.AEROSPIKE_NAMESPACE, aerospike_set, bin_name, f'{aerospike_set}_{bin_name}_idx')
            except exception.IndexFoundError:
                pass

    def callback(self, input_tuple):
        (key, meta, rec) = input_tuple
        self.records_result.append((rec))
        return self.records_result
