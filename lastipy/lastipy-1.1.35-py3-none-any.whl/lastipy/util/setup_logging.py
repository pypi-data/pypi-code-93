from lastipy import definitions
import logging
import logging.handlers
import os


def setup_logging(filename):
    logs_directory = os.path.join(definitions.ROOT_DIR, "logs")
    if not os.path.exists(logs_directory):
        os.makedirs(logs_directory)

    logger = logging.getLogger()
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    file_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(logs_directory, filename),
        maxBytes=2 * 1024 * 1024,  # 2MB
        backupCount=25,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
