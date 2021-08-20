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
    AEROSPIKE_SCAN = Summary('aerospike_scan_latency_seconds', 'Time spent processing scan in aerospike')
    AEROSPIKE_QUERY = Summary('aerospike_query_latency_seconds', 'Time spent processing query in aerospike')
    AEROSPIKE_CREATE_INDEX = Summary('aerospike_create_index_latency_seconds', 'Time spent creating index in aerospike')

    def __init__(self, aerospike_set, bin_index):
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


# data = {
#    "object_name": "monitoring-host",
#    "alert_name": "Auto Test: New alert",
#    "alert_status": 1,
#    "environment": 12,
#    "severity": 3,
#    "source": "API Source",
#    "ms": "api",
#    "service": None,
#    "alert_output": "notification_output: 0",
#    "event_id": "a75b2897-5338-4919-be09-008f37918e85",
#    "ms_alert_id": None,
#    "graph_url": None,
#    "unique_data": {},
#    "extra_urls": {
#       "URL1": "http://some_url",
#       "URL_NAME": "http://some_url_to_docs"
#    },
#    "extra_fields": {
#       "description": "Some Desc",
#       "script_name": "script.py",
#       "owner": "some@gmail.com"
#    },
#    "actions": {},
#    "scenario_id": 1,
#    "org_id": "asd21da3",
#    "scenario": None
# }

# Create index
# aerospike_client = AerospikeClient()
# aerospike_client.create_index_string('dev_active_alerts', bin_type='string', bin_name='alert_name')

# aerospike_client.scan_keys('aggr_notifications')
# aerospike_client.put_message('dev_active_alerts', '123', data)
# print(json.dumps(aerospike_client.read_message('dev_active_alerts', '123')))

# Query with multiple WHERE
# aerospike_client = AerospikeClient()
# predexps = [
#     predexp.integer_bin("environment"),
#     predexp.integer_value(13),
#     predexp.integer_equal(),
#     predexp.string_bin("alert_name"),
#     predexp.string_value("Auto Test: New alert"),
#     predexp.string_equal(),
#     predexp.predexp_and(2)
# ]
# q = aerospike_client.query_messages_predexps('dev_active_alerts', predexps)
#
# print(q)
