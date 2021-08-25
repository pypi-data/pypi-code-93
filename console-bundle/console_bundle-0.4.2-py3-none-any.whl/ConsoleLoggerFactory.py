import logging
import colorlog


class ConsoleLoggerFactory:
    def create(self):
        logger = logging.getLogger("console")
        logger.setLevel(logging.DEBUG)

        format_str = "%(message)s"
        date_format = "%H:%M:%S"
        cformat = "%(log_color)s" + format_str
        formatter = colorlog.ColoredFormatter(cformat, date_format)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        logger.handlers = [stream_handler]

        return logger
