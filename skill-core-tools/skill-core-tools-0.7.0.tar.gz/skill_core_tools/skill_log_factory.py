import logging
import os


class SkillLogFactory:
    @staticmethod
    def get_logger(name: str):
        """
        Provides a logger with the given name and a preconfigured formatter.
        :param name:
        :return: logger instance
        """
        log_level = os.environ.get("LOG_LEVEL", "INFO")
        logging.basicConfig(level=log_level.upper(),
                            format='%(asctime)s.%(msecs)03d %(levelname)s [%(threadName)s:%(name)s.%(funcName)s] %(message)s',
                            datefmt='%Y-%m-%d,%H:%M:%S')

        return logging.getLogger(name)