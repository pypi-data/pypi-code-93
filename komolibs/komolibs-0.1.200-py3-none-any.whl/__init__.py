__version__ = '0.1.0'

import logging

from komolibs.logger.struct_logger import StructLogRecord, StructLogger

STRUCT_LOGGER_SET = False
DEV_STRATEGY_PREFIX = "dev"
_prefix_path = None

# Do not raise exceptions during log handling
logging.setLogRecordFactory(StructLogRecord)
logging.setLoggerClass(StructLogger)