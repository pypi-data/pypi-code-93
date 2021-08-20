from __future__ import absolute_import

from stackifyapm.exceptions import StackifyAPMException
from stackifyapm.instrumentation.decorators import call_exception_handler
from stackifyapm.instrumentation.packages.base import AbstractInstrumentedModule
from stackifyapm.traces import CaptureSpan
from stackifyapm.utils import compat, get_method_name
from stackifyapm.utils.helper import is_async_span


class Redis3CheckMixin(object):
    instrument_list_3 = []
    instrument_list = []

    def get_instrument_list(self):
        try:
            from redis import VERSION

            if VERSION[0] >= 3:
                return self.instrument_list_3
            return self.instrument_list
        except ImportError:
            return self.instrument_list


class RedisInstrumentation(Redis3CheckMixin, AbstractInstrumentedModule):
    name = "redis"

    instrument_list_3 = [("redis.client", "Redis.execute_command")]
    instrument_list = [("redis.client", "Redis.execute_command"), ("redis.client", "StrictRedis.execute_command")]

    @call_exception_handler
    def call(self, module, method, wrapped, instance, args, kwargs):
        try:
            context = {
                "CATEGORY": "Cache",
                "SUBCATEGORY": "Execute",
                "COMPONENT_CATEGORY": "Cache",
                "COMPONENT_DETAIL": "Execute",
                "OPERATION": args and args[0] and args[0].lower() or get_method_name(method),
            }

            try:
                host = instance.connection_pool.connection_kwargs.get('host')
                port = instance.connection_pool.connection_kwargs.get('port')
                context["URL"] = "{}:{}".format(host, port)
            except Exception:
                pass

            cache_name = len(args) > 1 and args[1] or None
            if isinstance(cache_name, compat.binary_type):
                context["CACHEKEY"] = cache_name.decode('utf-8')
            elif cache_name:
                context["CACHEKEY"] = str(cache_name)
        except Exception as e:
            raise StackifyAPMException(e)

        with CaptureSpan("cache.redis", context, leaf=True, is_async=is_async_span()):
            return wrapped(*args, **kwargs)


class RedisPipelineInstrumentation(Redis3CheckMixin, AbstractInstrumentedModule):
    name = "redis"

    instrument_list_3 = [("redis.client", "Pipeline.execute")]
    instrument_list = [("redis.client", "BasePipeline.execute")]

    @call_exception_handler
    def call(self, module, method, wrapped, instance, args, kwargs):
        try:
            operation = args and args[0] and args[0].lower() or get_method_name(method)
            cache_name = len(args) > 1 and args[1] or None

            if hasattr(instance, 'command_stack'):
                operation = instance.command_stack[0][0][0]
                cache_name = instance.command_stack[0][0][1]

            context = {
                "CATEGORY": "Cache",
                "SUBCATEGORY": "Execute",
                "COMPONENT_CATEGORY": "Cache",
                "COMPONENT_DETAIL": "Execute",
                "OPERATION": operation,
            }

            try:
                host = instance.connection_pool.connection_kwargs.get('host')
                port = instance.connection_pool.connection_kwargs.get('port')
                context["URL"] = "{}:{}".format(host, port)
            except Exception:
                pass

            if isinstance(cache_name, compat.binary_type):
                context["CACHEKEY"] = cache_name.decode('utf-8')
            elif cache_name:
                context["CACHEKEY"] = str(cache_name)

        except Exception as e:
            raise StackifyAPMException(e)

        with CaptureSpan("cache.redis", context, leaf=True, is_async=is_async_span()):
            return wrapped(*args, **kwargs)
