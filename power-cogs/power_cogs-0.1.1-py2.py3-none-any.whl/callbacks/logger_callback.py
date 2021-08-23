import sys

from loguru import logger

# internal
from power_cogs.callbacks.callback import Callback


class LoggerCallback(Callback):
    def __init__(self):
        super(LoggerCallback, self).__init__()
        logger.add(sys.stderr)

    def before(self, wrapped_obj, f, *args, **kwargs):
        class_str = " "
        if wrapped_obj is not None:
            class_str = " class: {} -- ".format(wrapped_obj.__class__.__name__)
        logger.info("Entering{}{}".format(class_str, f.__name__))

    def after(self, prev_output, wrapped_obj, f, *args, **kwargs):
        logger.info("Exiting: {}, Got output: {}".format(f.__name__, prev_output))
        return prev_output

    def handle_exception(self, exception: Exception):
        logger.exception(exception)
