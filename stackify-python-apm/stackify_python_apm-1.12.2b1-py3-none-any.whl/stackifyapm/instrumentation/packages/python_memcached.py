from stackifyapm.exceptions import StackifyAPMException
from stackifyapm.instrumentation.decorators import call_exception_handler
from stackifyapm.instrumentation.packages.base import AbstractInstrumentedModule
from stackifyapm.traces import CaptureSpan
from stackifyapm.utils import compat, get_method_name
from stackifyapm.utils.helper import is_async_span


class PythonMemcachedInstrumentation(AbstractInstrumentedModule):
    name = "python_memcached"

    memcached_method_list = [
        "add",
        "append",
        "cas",
        "decr",
        "delete",
        "delete_multi",
        "disconnect_all",
        "flush_all",
        "get",
        "get_multi",
        "get_slabs",
        "get_stats",
        "gets",
        "incr",
        "prepend",
        "replace",
        "set",
        "set_multi",
        "touch",
    ]

    def get_instrument_list(self):
        method_list = [("memcache", "Client.{}".format(method)) for method in self.memcached_method_list]
        method_list += [("pymemcache.client.base", "Client.{}".format(method)) for method in self.memcached_method_list]
        return method_list

    @call_exception_handler
    def call(self, module, method, wrapped, instance, args, kwargs):
        try:
            method_name = get_method_name(method)
            context = {
                "CATEGORY": "Cache",
                "SUBCATEGORY": "Execute",
                "COMPONENT_CATEGORY": "Cache",
                "COMPONENT_DETAIL": "Execute",
                "OPERATION": method_name,
            }

            if hasattr(instance, 'servers'):
                host, port = instance.servers[0].address
                context["URL"] = "{}:{}".format(host, port)
            elif hasattr(instance, 'server'):
                host, port = instance.server
                context["URL"] = "{}:{}".format(host, port)

            cache_name = args and args[0] or None
            if isinstance(cache_name, compat.binary_type):
                context["CACHEKEY"] = cache_name.decode('utf-8')
            elif cache_name:
                context["CACHEKEY"] = str(cache_name)
        except Exception as e:
            raise StackifyAPMException(e)

        with CaptureSpan("cache.memcached", context, is_async=is_async_span()):
            return wrapped(*args, **kwargs)
