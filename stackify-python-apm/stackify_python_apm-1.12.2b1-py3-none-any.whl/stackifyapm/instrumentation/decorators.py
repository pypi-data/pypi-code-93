import logging
from functools import wraps

from stackifyapm.exceptions import StackifyAPMException


logger = logging.getLogger("stackifyapm.instrument")


def call_exception_handler(func):
    @wraps(func)
    def wrapper(self, module, method, wrapped, instance, args, kwargs):
        try:
            return func(self, module, method, wrapped, instance, args, kwargs)
        except StackifyAPMException as e:
            logger.debug("StackifyAPMExcpetion within instrumentation. Error: {}.".format(e))
            return wrapped(*args, **kwargs)
        except Exception as e:
            logger.debug("Excpetion calling client's method. Error: {}.".format(e))
            raise

    return wrapper
