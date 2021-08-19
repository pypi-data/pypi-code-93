import logging


class Logger:
    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._configure_logger()

    @property
    def logger(self):
        return self._logger

    def _configure_logger(self) -> None:
        self._logger.propagate = False
        self._logger.setLevel(logging.INFO)

        if not len(self._logger.handlers):
            handler = self._create_handler()
            self._logger.addHandler(handler)

    def _create_handler(self) -> logging.Handler:
        handler = logging.StreamHandler()
        formatter = self._create_formatter()
        handler.setFormatter(formatter)
        return handler

    def _create_formatter(self) -> logging.Formatter:
        return logging.Formatter(
            f"%(levelname)s:%(name)s:%(asctime)s: %(message)s", "%Y-%m-%d %H:%M:%S"
        )
