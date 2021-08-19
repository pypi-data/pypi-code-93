import logging


def set_logging_level(level):
    logger.setLevel(level)


# chooses the right format for outputs
format = (
    "%(asctime)s - [%(levelname)s] %(module)s.%(funcName)s(%(lineno)d): "
    + "%(message)s"
)
logFormatter = logging.Formatter(format)

# registers the handlers for logfile and stdout
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
fileHandler = logging.FileHandler("logfile.log")
fileHandler.setFormatter(logFormatter)

# Create a custom logger
logger = logging.getLogger(__name__)
logger.addHandler(consoleHandler)
logger.addHandler(fileHandler)

set_logging_level("INFO")
