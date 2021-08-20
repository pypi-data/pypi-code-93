from stackifyapm.exceptions import StackifyAPMException
from stackifyapm.instrumentation.decorators import call_exception_handler
from stackifyapm.instrumentation.packages.base import AbstractInstrumentedModule
from stackifyapm.traces import CaptureSpan
from stackifyapm.utils import compat, get_method_name
from stackifyapm.utils.helper import is_async_span


class PyLibMcInstrumentation(AbstractInstrumentedModule):
    name = "pylibmc"

    instrument_list = [
        ("pylibmc", "Client.get"),
        ("pylibmc", "Client.get_multi"),
        ("pylibmc", "Client.set"),
        ("pylibmc", "Client.set_multi"),
        ("pylibmc", "Client.add"),
        ("pylibmc", "Client.replace"),
        ("pylibmc", "Client.append"),
        ("pylibmc", "Client.prepend"),
        ("pylibmc", "Client.incr"),
        ("pylibmc", "Client.decr"),
        ("pylibmc", "Client.gets"),
        ("pylibmc", "Client.cas"),
        ("pylibmc", "Client.delete"),
        ("pylibmc", "Client.delete_multi"),
        ("pylibmc", "Client.touch"),
        ("pylibmc", "Client.get_stats"),
    ]

    @call_exception_handler
    def call(self, module, method, wrapped, instance, args, kwargs):
        try:
            address, port = None, None
            if instance.addresses:
                first_address = instance.addresses[0]
                if ":" in first_address:
                    address, port = first_address.split(":", 1)
                    try:
                        port = int(port)
                    except ValueError:
                        port = None

            context = {
                "CATEGORY": "Cache",
                "SUBCATEGORY": "Execute",
                "COMPONENT_CATEGORY": "Cache",
                "COMPONENT_DETAIL": "Execute",
                "OPERATION": get_method_name(method),
            }

            if address and port:
                context["URL"] = "{}:{}".format(address, port)

            cache_name = args and args[0] or None
            if cache_name:
                if isinstance(cache_name, compat.string_types):
                    context["CACHENAME"] = cache_name
                    context["CACHEKEY"] = cache_name.split(':')[-1]
                elif isinstance(cache_name, compat.list_type):
                    context["CACHENAME"] = cache_name
                    context["CACHEKEY"] = [name.split(':')[-1] for name in cache_name]
                elif isinstance(cache_name, compat.dict_type):
                    context["CACHENAME"] = list(cache_name.keys())
                    context["CACHEKEY"] = [name.split(':')[-1] for name in cache_name.keys()]
                elif isinstance(cache_name, compat.binary_type):
                    context["CACHEKEY"] = cache_name.decode('utf-8')
                else:
                    context["CACHEKEY"] = cache_name
        except Exception as e:
            raise StackifyAPMException(e)

        with CaptureSpan("cache.memcached", context, is_async=is_async_span()):
            return wrapped(*args, **kwargs)
