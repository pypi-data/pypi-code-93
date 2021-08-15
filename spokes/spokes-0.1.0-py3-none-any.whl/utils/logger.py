import sys
from datetime import datetime
import os
import logging

def setup_spokes_logger(name = "spokes", dir_path=None):
    logger = logging.getLogger(name)

    logging.addLevelName(15, "VERBOSE")
    setattr(logger, 'verbose', lambda message : logger.log(15, message))

    logger.setLevel(logging.INFO)

    format = logging.Formatter("%(asctime)s :: %(name)s :: %(levelname)-8s :: %(message)s")
    stream = logging.StreamHandler(sys.stdout)
    stream.setFormatter(format)
    logger.handlers.clear()
    logger.addHandler(stream)

    if dir_path != 'None':
        file_name = datetime.now().strftime("spokes_%d_%m_%Y_%H_%M_%S.log")
        file_path = os.path.join(dir_path, file_name)
        file = logging.FileHandler(file_path)
        file.setFormatter(format)
        logger.addHandler(file)

    else:
        file_path = "No log file specified"

    return logger, file_path

def get_logger(unit_name, name = "spokes"):
    logger = logging.getLogger(name).getChild(unit_name)
    setattr(logger, 'verbose', lambda message : logger.log(15, message))
    return logger
