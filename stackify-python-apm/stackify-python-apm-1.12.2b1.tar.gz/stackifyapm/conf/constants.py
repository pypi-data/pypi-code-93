import os


TRACEPARENT_HEADER_NAME = "stackify-apm-traceparent"
TRACE_CONTEXT_VERSION = '2.0'

KEYWORD_MAX_LENGTH = 1024

HTTP_WITH_BODY = {"POST", "PUT", "PATCH", "DELETE"}

ERROR = "error"
TRANSACTION = "transaction"
SPAN = "span"

MAX_LOG_FILE_COUNT = 10

if os.name == 'nt':
    all_users_profile = os.environ.get('ALLUSERSPROFILE') or 'c:\\ProgramData'

    BASE_PATH = "{}\\Stackify\\Python\\".format(all_users_profile)
    LOG_PATH = "{}Log\\".format(BASE_PATH)

    PREFIX_BASE_PATH = "{}\\Stackify\\Agent\\".format(all_users_profile)
    PREFIX_LOG_PATH = "{}log\\".format(PREFIX_BASE_PATH)
    PREFIX_DEBUG_PATH = "{}debug\\".format(PREFIX_BASE_PATH)

else:
    BASE_PATH = "/usr/local/stackify/stackify-python-apm/"
    LOG_PATH = "{}log/".format(BASE_PATH)

    PREFIX_BASE_PATH = "/usr/local/prefix/"
    PREFIX_LOG_PATH = "{}log/".format(PREFIX_BASE_PATH)
    PREFIX_DEBUG_PATH = "{}debug/".format(PREFIX_BASE_PATH)

QUEUE_TIME_INTERVAL_IN_MS = 500
QUEUE_MAX_SIZE = 1000

ASYNC_WAITING_TIME_IN_SEC = 10
ASYNC_MAX_WAITING_TIME_IN_SEC = 40

RUM_COOKIE_NAME = ".Stackify.Rum"

AGENT_TRACES_MAX_SIZE = 50
AGENT_SEND_INTERVAL_IN_SEC = 10
AGENT_TRACES_PATH = '/traces'

TRANSPORT_AGENT_HTTP = "agent_http"
TRANSPORT_AGENT_SOCKET = "agent_socket"
TRANSPORT_DEFAULT = "default"
TRANSPORT_LOGGING = "logging"

DEFAULT_ENVIRONMENT = "Production"
DEFAULT_APPLICATION_NAME = "Python Application"
DEFAULT_CONFIG_FILE = "stackify.json"
DEFAULT_MULTIPROCESSING = False
DEFAULT_RUM_ENABLED = False
DEFAULT_TRANSPORT = TRANSPORT_DEFAULT
DEFAULT_TRANSPORT_SOCKET_FILE = "http+unix://%2Fusr%2Flocal%2Fstackify%2Fstackify.sock"
DEFAULT_HTTP_ENDPOINT = "https://localhost:10601"
DEFAULT_DEBUG = False
DEFAULT_QUEUE = True
DEFAULT_PREFIX_ENABLED = False
DEFAULT_INSTRUMENT_ALL = False
DEFAULT_RUM_SCRIPT_URL = "https://stckjs.stackify.com/stckjs.js"
DEFAULT_RUM_KEY = ""

SQL_STATEMENT_MAX_LENGTH = 100000
