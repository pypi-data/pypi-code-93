import logging
from functools import wraps


logger = logging.getLogger("stackifyapm.instrument")


def exception_handler(message="Error"):
    def handle_exception(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                logger.debug("{}: {}.".format(message, e))

            return None
        return wrapper
    return handle_exception
