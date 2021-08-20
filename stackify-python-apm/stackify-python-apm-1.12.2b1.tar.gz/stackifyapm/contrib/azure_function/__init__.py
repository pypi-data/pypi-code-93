from functools import wraps

from stackifyapm.contrib import _BaseServerlessStackifyAPM
from stackifyapm.instrumentation.control import instrument


class StackifyAPM(_BaseServerlessStackifyAPM):
    """
    Application class for Azure Function.
    """
    def __call__(self, func):

        @wraps(func)
        def wrapper(req, *args, **kwargs):
            azure_context = kwargs.get('context', None)
            self.func_name = azure_context and azure_context.function_name or func.__name__

            with self:
                return func(req, *args, **kwargs)

        return wrapper

    def __enter__(self):
        self.client.begin_transaction("azure", client=self.client)


class HandlerWrapper(object):
    """
    HandlerWrapper class for Azure Function.
    """
    def __init__(self, **defaults):
        self.apm = StackifyAPM(**defaults)
        instrument(self.apm.client)

    def __call__(self, func, *args, **kwargs):

        @wraps(func)
        def wrapper(req, *args, **kwargs):
            return self.apm(func)(req, *args, **kwargs)

        return wrapper
