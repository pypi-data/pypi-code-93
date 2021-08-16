import os
import sys
import platform
import tempfile
from distutils.util import strtobool
import inspect
import logging
log = logging.getLogger("hyperc")

DEFAULT_LOG_LEVEL = "ERROR"

TEMPDIR = os.getenv('HYPERC_TEMPDIR', os.path.join(tempfile.gettempdir(),
                                                   'hyperc', os.getenv('LOGNAME', 'hyperc')))

APPENDIX = "_"

PYTHON = os.getenv("PYTHON", "NONE")
if PYTHON == "NONE":
    import shutil
    if shutil.which("pypy3"):
        PYTHON = "pypy3"
    else:
        PYTHON = "python"

DOWNWARD_TOTAL_PUSHES = os.getenv("DOWNWARD_TOTAL_PUSHES", "5000000")
USE_CACHE = str(os.getenv("HYPERC_USE_CACHE", "0"))
# default expire time 1 month
HYPERC_CACHE_EXPIRE_TIME = int(os.getenv("HYPERC_CACHE_EXPIRE_TIME", 30*24*60*60))
HYPERC_CACHE_DIR = os.getenv("HYPERC_CACHE_DIR", None)
if HYPERC_CACHE_DIR is None:
    if platform.system() == "Linux":
        HYPERC_CACHE_DIR = '/var/cache/hyperc'
    elif platform.system() == "Windows":
        HYPERC_CACHE_DIR = './'

HYPERC_SILENCE = (os.getenv("HYPERC_SILENCE", "1")) # suppress all output
STORE_STDOUT = int(os.getenv("HYPERC_STORE_STDOUT", 0))
HYPERC_DELETE_STDOUT = os.getenv("HYPERC_DELETE_STDOUT", "0")
HYPERC_SAS_RANDOMIZE = os.getenv("HYPERC_SAS_RANDOMIZE", "0")
HYPERC_HR_LOG = os.getenv("HYPERC_HR_LOG", "0")

STORE_SAS = os.getenv("HYPERC_STORE_SAS", "0")
if STORE_STDOUT == 0:
    HYPERC_CLEANUP = os.getenv("HYPERC_CLEANUP", "1")
else:
    HYPERC_CLEANUP = "0"
HYPERC_LOGGER_TYPE = os.getenv('HYPERC_LOGGER_TYPE', 'DEFAULT').upper()

if HYPERC_LOGGER_TYPE == 'NULL' or HYPERC_SILENCE == "1":
    handler = logging.NullHandler()
elif HYPERC_LOGGER_TYPE == 'SYSLOG':
    handler = logging.handlers.SysLogHandler(address='/dev/log')
elif HYPERC_LOGGER_TYPE == 'STDOUT':
    handler = logging.StreamHandler(sys.stdout)

if HYPERC_LOGGER_TYPE != 'default':
    while len(log.handlers) > 0:
        h = log.handlers[0]
        log.removeHandler(h)
    formatter = logging.Formatter('%(module)s:%(funcName)s:%(message)s')
    handler.setFormatter(formatter)

    log.addHandler(handler)

HYPERC_MAX_PROC = int(os.getenv('HYPERC_MAX_PROC', 200))
HYPERC_MAX_PROC_COUNTER=0

DOWNWARD_FOLDER = os.getenv('HYPERC_DOWNWARD_FOLDER', '')
if not DOWNWARD_FOLDER:
    try:
        import downward_ch.build

        # DOWNWARD_FOLDER = downward_ch.__path__._path[0]
        DOWNWARD_FOLDER = os.path.dirname(inspect.getfile(downward_ch.build))
    except ImportError:
        pass  # Fast downward not installed

DOWNWARD_SCRIPT = os.getenv('HYPERC_DOWNWARD_SCRIPT', None)
if DOWNWARD_SCRIPT is None:
    DOWNWARD_SCRIPT = os.path.join(DOWNWARD_FOLDER, 'fast-downward.py')

SOLVER_MAX_TIME = int(os.getenv('HYPERC_SOLVER_MAX_TIME', 60))

HYPERC_SOLVER_LOGLEVEL = os.getenv('HYPERC_SOLVER_LOGLEVEL', 'trace').lower()  #info, debug and trace available

log = logging.getLogger("hyperc")
log_level_str = os.getenv('HYPERC_LOGLEVEL', DEFAULT_LOG_LEVEL).upper()

if log_level_str in ['DEBUG', 'INFO', "WARNING", "ERROR", "CRITICAL"]:
    log_level = getattr(logging, log_level_str)
else:
    log_level = getattr(logging, DEFAULT_LOG_LEVEL)
logging.basicConfig(level=log_level)
if log_level <= logging.DEBUG:
    DEBUG = True
    print("ENABLING HARD DEBUG")
    plogger = logging.getLogger('hyperc_progress')
    plogger.setLevel(log_level)
    # log.setLevel(log_level)
    log.setLevel(logging.DEBUG)
    log.debug("DEBUG logging enabled")
else:
    DEBUG = False
    if log_level <= logging.INFO:
        plogger = logging.getLogger('hyperc_progress')
        # plogger.addHandler(logging.StreamHandler())
        plogger.setLevel(logging.INFO)
log.debug("DEBUG logging enabled")

HYPERC_SEARCH_CONFIG = os.getenv("HYPERC_SEARCH_CONFIG", "lmcount_alt5").replace("-", "_").lower()
HYPERC_NEW_OBJECTS = int(os.getenv("HYPERC_NEW_OBJECTS", 5))
HYPERC_LIN_COUNT = int(os.getenv("HYPERC_LIN_COUNT", 7))
HYPERC_INT_START = int(os.getenv("HYPERC_INT_START", 0))
HYPERC_FORCE_LIN_COUNT = int(os.getenv("HYPERC_FORCE_LIN_COUNT ", 0))

try:
    import hyperc.web_ff_inter
    BROWSER_MODE = True
except ImportError:
    BROWSER_MODE = False
HYPERC_OLD_SPLITTER = int(os.getenv("HYPERC_OLD_SPLITTER", 0))
HYPERC_SPLIT_SKIP = int(os.getenv("HYPERC_SPLIT_SKIP", 1))
HYPERC_MAX_EFFECT_AMOUNT = int(os.getenv("HYPERC_MAX_EFFECT_AMOUNT", 4))

# Debugging parameters
HYPERC_SPLIT_OFF = int(os.getenv('HYPERC_SPLIT_OFF', '0'))  # WARNING! SPLITTER DISABLED
HYPERC_SPLIT_STRATEGY = os.getenv('HYPERC_SPLIT_STRATEGY', "PATTERN_STRATEGY")  # PATTERN_SPLIT GROUND_LIMIT

HYPERC_DONT_REMOVE_ACTIONS = int(os.getenv('HYPERC_DONT_REMOVE_ACTIONS', '0'))
HYPERC_DONT_FILTER_FACTS = int(os.getenv('HYPERC_DONT_FILTER_FACTS', '0'))
HYPERC_DUMP_ORIGIN = os.getenv('HYPERC_DUMP_ORIGIN', '0')
HYPERC_GEN_PDDL_ONLY = int(os.getenv('HYPERC_GEN_PDDL_ONLY', 0))
HYPERC_CLEANUP = os.getenv('HYPERC_CLEANUP', '0')

HYPERC_RTX_OFF = os.getenv('HYPERC_RTX_OFF', '1')  # TODO: RTX is broken as of now
HYPERC_RTX_TIMEOUT = int(os.getenv('HYPERC_RTX_TIMEOUT', '600'))
HYPERC_RTX_RUNS = int(os.getenv('HYPERC_RTX_RUNS', '0'))

min_int = HYPERC_INT_START
max_int = HYPERC_INT_START + HYPERC_LIN_COUNT

HYPERC_ASE_OFF = int(os.getenv('HYPERC_ASE_OFF', '0'))

HYPERC_STRICT_TYPING = int(os.getenv('HYPERC_STRICT_TYPING', '0'))
HYPERC_STRICT_TYPING_DOC = """Enable strict type checking using python annotations. Fail to compile if types are missing or broken."""

IGNORE_EQ_BRANCH = int(os.getenv('HYPERC_IGNORE_EQ_BRANCH', '0'))

_old_trace = None  # old tracing function in case if run with debugger