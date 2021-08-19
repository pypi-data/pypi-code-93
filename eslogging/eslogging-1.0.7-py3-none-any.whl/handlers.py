import datetime
import json
import logging
import platform
import re
import socket
import sys
import traceback
from enum import Enum
from threading import Timer, Lock
from typing import TextIO, Dict, Any, Iterable, Optional

from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch import helpers as eshelpers

try:
    from requests_kerberos import HTTPKerberosAuth, DISABLED

    KERBEROS_SUPPORTED = True
except ImportError:
    KERBEROS_SUPPORTED = False

try:
    from requests_aws4auth import AWS4Auth

    AWS4AUTH_SUPPORTED = True
except ImportError:
    AWS4AUTH_SUPPORTED = False

from eslogging.serializers import ESSerializer


class ESHandler(logging.Handler):
    """ Elasticsearch log handler

    Allows to log to elasticsearch into json format.
    All LogRecord fields are serialised and inserted
    """

    class AuthType(Enum):
        """ Authentication types supported

        The handler supports
         - No authentication
         - Basic authentication
         - Kerberos or SSO authentication (on windows and linux)
        """
        NO_AUTH = 0
        BASIC_AUTH = 1
        KERBEROS_AUTH = 2
        AWS_SIGNED_AUTH = 3

    class IndexNameFrequency(Enum):
        """ Index type supported
        the handler supports
        - Daily indices
        - Weekly indices
        - Monthly indices
        - Year indices
        """
        NO_FREQ = 0
        DAILY = 1
        WEEKLY = 2
        MONTHLY = 3
        YEARLY = 4

    # Defaults for the class
    __DEFAULT_ELASTICSEARCH_HOST = ({'host': 'localhost', 'port': 9200},)
    __DEFAULT_AUTH_USER = ''
    __DEFAULT_AUTH_PASSWD = ''
    __DEFAULT_AWS_ACCESS_KEY = ''
    __DEFAULT_AWS_SECRET_KEY = ''
    __DEFAULT_AWS_REGION = ''
    __DEFAULT_AUTH_TYPE = AuthType.NO_AUTH
    __DEFAULT_INDEX_FREQUENCY = IndexNameFrequency.DAILY
    __DEFAULT_BUFFER_SIZE = 1000
    __DEFAULT_FLUSH_FREQ_INSEC = 1
    __DEFAULT_ES_INDEX_NAME = 'python_logger'
    __DEFAULT_ES_DOC_TYPE = 'python_log'
    __DEFAULT_RAISE_ON_EXCEPTION = False
    __DEFAULT_TIMESTAMP_FIELD_NAME = "timestamp"

    __LOGGING_FILTER_FIELDS = ['msecs',
                               'relativeCreated',
                               'levelno',
                               'created']

    BASE_ES_MODULE_FILTER_RE = re.compile(r'.+elasticsearch[\\/]connection[\\/]base.py.*$', re.I)

    @classmethod
    def es_filter(cls, record: logging.LogRecord) -> bool:
        """Filters out records coming from Elasticsearch base module"""
        return not cls.BASE_ES_MODULE_FILTER_RE.match(record.pathname)

    @staticmethod
    def _get_daily_index_name(es_index_name: str) -> str:
        """ Returns elasticearch index name
        :param: index_name the prefix to be used in the index
        :return: A srting containing the elasticsearch indexname used which should include the date.
        """
        return "{0!s}-{1!s}".format(es_index_name, datetime.datetime.now().strftime('%Y.%m.%d'))

    @staticmethod
    def _get_weekly_index_name(es_index_name: str) -> str:
        """ Return elasticsearch index name
        :param: index_name the prefix to be used in the index
        :return: A srting containing the elasticsearch indexname used which should include the date and specific week
        """
        current_date = datetime.datetime.now()
        start_of_the_week = current_date - datetime.timedelta(days=current_date.weekday())
        return "{0!s}-{1!s}".format(es_index_name, start_of_the_week.strftime('%Y.%m.%d'))

    @staticmethod
    def _get_monthly_index_name(es_index_name: str) -> str:
        """ Return elasticsearch index name
        :param: index_name the prefix to be used in the index
        :return: A srting containing the elasticsearch indexname used which should include the date and specific moth
        """
        return "{0!s}-{1!s}".format(es_index_name, datetime.datetime.now().strftime('%Y.%m'))

    @staticmethod
    def _get_unchanged_index_name(es_index_name: str) -> str:
        """ Return elasticsearch index name
        :param: index_name the prefix to be used in the index
        :return: A srting containing the elasticsearch indexname used which should include the date and specific moth
        """
        return es_index_name

    @staticmethod
    def _get_yearly_index_name(es_index_name: str):
        """ Return elasticsearch index name
        :param: index_name the prefix to be used in the index
        :return: A srting containing the elasticsearch indexname used which should include the date and specific year
        """
        return "{0!s}-{1!s}".format(es_index_name, datetime.datetime.now().strftime('%Y'))

    _INDEX_FREQUENCY_FUNCION_DICT = {
        IndexNameFrequency.NO_FREQ: _get_unchanged_index_name,
        IndexNameFrequency.DAILY:   _get_daily_index_name,
        IndexNameFrequency.WEEKLY:  _get_weekly_index_name,
        IndexNameFrequency.MONTHLY: _get_monthly_index_name,
        IndexNameFrequency.YEARLY:  _get_yearly_index_name
    }

    def __init__(self,
        hosts: Iterable[Dict[str, Any]] = __DEFAULT_ELASTICSEARCH_HOST,
        auth_details=(__DEFAULT_AUTH_USER, __DEFAULT_AUTH_PASSWD),
        aws_access_key: str = __DEFAULT_AWS_ACCESS_KEY,
        aws_secret_key: str = __DEFAULT_AWS_SECRET_KEY,
        aws_region: str = __DEFAULT_AWS_REGION,
        auth_type: AuthType = __DEFAULT_AUTH_TYPE,
        buffer_size: int = __DEFAULT_BUFFER_SIZE,
        flush_frequency_in_sec: int = __DEFAULT_FLUSH_FREQ_INSEC,
        es_index_name: str = __DEFAULT_ES_INDEX_NAME,
        index_name_frequency: IndexNameFrequency = __DEFAULT_INDEX_FREQUENCY,
        es_doc_type: str = __DEFAULT_ES_DOC_TYPE,
        es_additional_fields: Optional[Dict] = None,
        raise_on_indexing_exceptions: bool = __DEFAULT_RAISE_ON_EXCEPTION,
        default_timestamp_field_name: str = __DEFAULT_TIMESTAMP_FIELD_NAME,
        timed_flush: bool = False,
        error_stream: TextIO = sys.stderr,
        **kwargs,):
        """ Handler constructor

        :param hosts: The list of hosts that elasticsearch clients will connect. The list can be provided
                    in the format ```[{'host':'host1','port':9200}, {'host':'host2','port':9200}]``` to
                    make sure the client supports failover of one of the instertion nodes
        :param auth_details: When ```ESHandler.AuthType.BASIC_AUTH``` is used this argument must contain
                    a tuple of string with the user and password that will be used to authenticate against
                    the Elasticsearch servers, for example```('User','Password')
        :param aws_access_key: When ```ESHandler.AuthType.AWS_SIGNED_AUTH``` is used this argument must contain
                    the AWS key id of the  the AWS IAM user
        :param aws_secret_key: When ```ESHandler.AuthType.AWS_SIGNED_AUTH``` is used this argument must contain
                    the AWS secret key of the  the AWS IAM user
        :param aws_region: When ```ESHandler.AuthType.AWS_SIGNED_AUTH``` is used this argument must contain
                    the AWS region of the  the AWS Elasticsearch servers, for example```'us-east'
        :param auth_type: The authentication type to be used in the connection ```ESHandler.AuthType```
                    Currently, NO_AUTH, BASIC_AUTH, KERBEROS_AUTH are supported
        :param use_ssl: A boolean that defines if the communications should use SSL encrypted communication
        :param verify_ssl: A boolean that defines if the SSL certificates are validated or not
        :param buffer_size: An int, Once this size is reached on the internal buffer results are flushed into ES
        :param flush_frequency_in_sec: A float representing how often and when the buffer will be flushed, even
                    if the buffer_size has not been reached yet
        :param es_index_name: A string with the prefix of the elasticsearch index that will be created. Note a
                    date with YYYY.MM.dd, ```python_logger``` used by default
        :param index_name_frequency: Defines what the date used in the postfix of the name would be. available values
                    are selected from the IndexNameFrequency class (IndexNameFrequency.DAILY,
                    IndexNameFrequency.WEEKLY, IndexNameFrequency.MONTHLY, IndexNameFrequency.YEARLY). By default
                    it uses daily indices.
        :param es_doc_type: A string with the name of the document type that will be used ```python_log``` used
                    by default
        :param es_additional_fields: A dictionary with all the additional fields that you would like to add
                    to the logs, such the application, environment, etc.
        :param raise_on_indexing_exceptions: A boolean, True only for debugging purposes to raise exceptions
                    caused when
        :param timed_flush: A boolean, will perform flushing on an independent thread every flush_frequency_in_sec secs
                            regardless if the buffer size is full or not

        :param kwargs: any additional arguments will be passed on to the
            :class:`~elasticsearch.Elasticsearch` class and, subsequently, to the
            :class:`~elasticsearch.Transport` class and, subsequently, to the
            :class:`~elasticsearch.Connection` instances.

        :return: A ready to be used ESHandler.
        """
        logging.Handler.__init__(self)

        self.hosts = hosts
        self.auth_details = auth_details
        self.aws_access_key = aws_access_key
        self.aws_secret_key = aws_secret_key
        self.aws_region = aws_region
        self.auth_type = auth_type
        self.buffer_size = buffer_size
        self.flush_frequency_in_sec = flush_frequency_in_sec
        self.es_index_name = es_index_name
        self.index_name_frequency = index_name_frequency
        self.es_doc_type = es_doc_type
        self.kwargs = kwargs

        if es_additional_fields is None:
            self.es_additional_fields = {}
        else:
            self.es_additional_fields = es_additional_fields.copy()

        host = socket.gethostname()
        if platform.system()!='Darwin':
            try:
                host_ip = socket.gethostbyname(host)
            except Exception as err:
                if err.errno==8:
                    host_ip = '127.0.0.1'
                else:
                    raise err
        else:
            host_ip = '127.0.0.1'
        self.es_additional_fields.update({'host':    host,
                                          'host_ip': host_ip})

        self.raise_on_indexing_exceptions = raise_on_indexing_exceptions
        self.default_timestamp_field_name = default_timestamp_field_name
        self._timed_flush = timed_flush
        self._error_stream = error_stream

        self._client = None
        self._buffer = []
        self._buffer_lock = Lock()
        self._timer = None
        self._index_name_func = ESHandler._INDEX_FREQUENCY_FUNCION_DICT[self.index_name_frequency]
        self.serializer = ESSerializer()
        # Next filter is needed as elasticsearch.bulk function calls logging.info in its http_requests module,
        #       and creates an infinite loop of logging.
        self.addFilter(self.es_filter)

    def _schedule_flush(self) -> None:
        if self._timer is None:
            self._timer = Timer(self.flush_frequency_in_sec, self.flush)
            self._timer.setDaemon(True)
            self._timer.start()

    def _get_es_client(self) -> Elasticsearch:
        if self.auth_type==ESHandler.AuthType.NO_AUTH:
            if self._client is None:
                self._client = Elasticsearch(hosts=self.hosts,
                    serializer=self.serializer,
                    **self.kwargs)
            return self._client

        if self.auth_type==ESHandler.AuthType.BASIC_AUTH:
            if self._client is None:
                return Elasticsearch(hosts=self.hosts,
                    http_auth=self.auth_details,
                    serializer=self.serializer,
                    **self.kwargs
                )
            return self._client

        if self.auth_type==ESHandler.AuthType.KERBEROS_AUTH:
            if not KERBEROS_SUPPORTED:
                raise EnvironmentError("Kerberos module not available. Please install \"requests-kerberos\"")
            # For kerberos we return a new client each time to make sure the tokens are up to date
            return Elasticsearch(hosts=self.hosts,
                connection_class=RequestsHttpConnection,
                http_auth=HTTPKerberosAuth(mutual_authentication=DISABLED),
                serializer=self.serializer,
                **self.kwargs)

        if self.auth_type==ESHandler.AuthType.AWS_SIGNED_AUTH:
            if not AWS4AUTH_SUPPORTED:
                raise EnvironmentError("AWS4Auth not available. Please install \"requests-aws4auth\"")
            if self._client is None:
                awsauth = AWS4Auth(self.aws_access_key, self.aws_secret_key, self.aws_region, 'es')
                self._client = Elasticsearch(
                    hosts=self.hosts,
                    http_auth=awsauth,
                    verify_certs=True,
                    connection_class=RequestsHttpConnection,
                    serializer=self.serializer,
                    **self.kwargs
                )
            return self._client

        raise ValueError("Authentication method not supported")

    def create_index_with_mapping(self, mapping: Dict[str, Any]) -> None:
        """Create an index with specified mapping if there is no other index with specified name."""
        client = self._get_es_client()
        # If index already exists there will be no change.
        client.indices.create(
            index=self.es_index_name,
            body=mapping,
            ignore=400  # ignore 400 already exists code
        )

    def test_es_source(self):
        """ Returns True if the handler can ping the Elasticsearch servers

        Can be used to confirm the setup of a handler has been properly done and confirm
        that things like the authentication is working properly

        :return: A boolean, True if the connection against elasticserach host was successful
        """
        return self._get_es_client().ping()

    @staticmethod
    def _get_es_datetime_str(timestamp: int) -> str:
        """ Returns elasticsearch utc formatted time for an epoch timestamp
        :return: A string valid for elasticsearch time record
        """
        current_date = datetime.datetime.utcfromtimestamp(timestamp)
        return "{0!s}.{1:03d}Z".format(current_date.strftime('%Y-%m-%dT%H:%M:%S'), int(current_date.microsecond / 1000))

    def flush(self) -> None:
        if self._timer is not None and self._timer.is_alive():
            self._timer.cancel()
        self._timer = None

        if self._buffer:
            try:
                with self._buffer_lock:
                    logs_buffer = self._buffer
                actions = (
                    {
                        '_index':  self._index_name_func.__func__(self.es_index_name),
                        '_type':   self.es_doc_type,
                        '_source': log_record
                    }
                    for log_record in logs_buffer
                )
                eshelpers.bulk(
                    client=self._get_es_client(),
                    actions=actions,
                    stats_only=True
                )
                self._buffer = []
            except Exception as exception:
                if self.raise_on_indexing_exceptions:
                    raise exception
                else:
                    traceback.print_exc(file=self._error_stream)
                    self._schedule_flush()

    def close(self) -> None:
        """ Flushes the buffer and release any outstanding resource"""
        if self._timer is not None:
            self.flush()
        self._timer = None

    def _try_flush(self) -> None:
        if len(self._buffer) >= self.buffer_size and not self._timed_flush:
            self.flush()
        else:
            self._schedule_flush()

    def emit(self, record: logging.LogRecord) -> None:
        """ Emit overrides the abstract logging.Handler logRecord emit method
        Format and records the log
        """
        rec = self.es_additional_fields.copy()
        for key, value in record.__dict__.items():
            if key not in ESHandler.__LOGGING_FILTER_FIELDS:
                if key=="args":
                    value = tuple(str(arg) for arg in value)
                rec[key] = "" if value is None else value
        rec[self.default_timestamp_field_name] = self._get_es_datetime_str(record.created)
        with self._buffer_lock:
            self._buffer.append(rec)

        self._try_flush()


class ESHandlerIgnoreESLogs(ESHandler):
    """
    This override is needed because elasticsearch.bulk function calls logging.info in its http_requests module,
    and creates an infinite loop of logging.
    ToDo: add unittests
    """

    def _emit(self, record: logging.LogRecord):
        rec = self.es_additional_fields.copy()
        message = record.getMessage()
        rec["msg"] = message
        log_keys = ["levelname", "pathname", "lineno", "funcName", "threadName", "processName", "process"]
        for key in log_keys:
            v = getattr(record, key, None)
            if v is not None:
                rec[key] = str(v)
        rec[self.default_timestamp_field_name] = self._get_es_datetime_str(record.created)
        with self._buffer_lock:
            self._buffer.append(rec)

        self._try_flush()

    def emit(self, record: logging.LogRecord):
        if isinstance(record.msg, (dict, list, tuple)):
            record.msg = json.dumps(record.msg)
        elif not isinstance(record.msg, str):
            record.msg = str(record.msg)
        self._emit(record)
