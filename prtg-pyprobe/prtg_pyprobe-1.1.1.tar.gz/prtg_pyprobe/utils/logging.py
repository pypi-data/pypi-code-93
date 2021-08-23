import logging

from logging.handlers import TimedRotatingFileHandler


def setup_logging() -> (logging.Logger, logging.StreamHandler, logging.Formatter):
    """Setup logging.

    Returns:
        tuple(logging.Logger, logging.StreamHandler, logging.Formatter): Logger, StreamHandler and Formatter.

    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s :: %(levelname)s :: %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level=logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger, console_handler, formatter


def setup_file_logging(
    cfg: dict, logger: logging.Logger, formatter: logging.Formatter, console_handler: logging.StreamHandler
) -> logging.Logger:
    """Set up file logging.

    Args:
        cfg (dict): ProbeConfig as dict.
        logger (logging.Logger): A valid logger.
        formatter (logging.Formatter): Formatter for logger.
        console_handler (logging.StreamHandler): StreamHandler for logger.

    Returns:
        logging.Logger: A file logger.

    Raises:
        Exception: Very broad exception.

    Todo:
        * Catch more specific exceptions.

    """
    try:
        logger.setLevel(cfg["log_level"])

        if cfg["log_file_location"]:
            filehandler = TimedRotatingFileHandler(cfg["log_file_location"], when="d", interval=1, backupCount=7)
            filehandler.setFormatter(formatter)
            logger.addHandler(filehandler)
            logger.removeHandler(console_handler)
        return logger
    # todo: catch explicit
    except Exception:
        raise
