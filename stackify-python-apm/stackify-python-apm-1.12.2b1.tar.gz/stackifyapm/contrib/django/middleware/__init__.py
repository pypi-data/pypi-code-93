from __future__ import absolute_import

import threading

from django.apps import apps
from django.conf import settings as django_settings

import stackifyapm
from stackifyapm.contrib.django.client import client, get_client
from stackifyapm.decorators import exception_handler
from stackifyapm.utils.helper import can_insert_script
from stackifyapm.utils.helper import get_rum_script_or_none, insert_rum_script_to_head, should_insert_html
from stackifyapm.utils.helper import get_stackify_header, get_value_from_key
from stackifyapm.traces import execution_context
from stackifyapm.utils import build_name_with_http_method_prefix, get_name_from_func, get_name_from_path, wrapt

try:
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    class MiddlewareMixin(object):
        pass


class StackifyAPMClientMiddlewareMixin(object):
    @property
    def client(self):
        try:
            app = apps.get_app_config("stackifyapm.contrib.django")
            return app.client
        except LookupError:
            return get_client()


def get_name_from_middleware(wrapped, instance):
    name = [type(instance).__name__, wrapped.__name__]
    if type(instance).__module__:
        name = [type(instance).__module__] + name
    return ".".join(name)


def process_request_wrapper(wrapped, instance, args, kwargs):
    response = wrapped(*args, **kwargs)
    try:
        if response is not None:
            request = args[0]
            stackifyapm.set_transaction_name(
                build_name_with_http_method_prefix(get_name_from_middleware(wrapped, instance), request),
                override=True,
            )
    finally:
        return response


def process_response_wrapper(wrapped, instance, args, kwargs):
    response = wrapped(*args, **kwargs)
    try:
        request, original_response = args
        if not hasattr(request, "_stackifyapm_view_func") and response is not original_response:
            stackifyapm.set_transaction_name(
                build_name_with_http_method_prefix(get_name_from_middleware(wrapped, instance), request),
                override=True,
            )
    finally:
        return response


class TracingMiddleware(MiddlewareMixin, StackifyAPMClientMiddlewareMixin):
    _stackifyapm_instrumented = False
    _instrumenting_lock = threading.Lock()

    @exception_handler(message="Error creating django TracingMiddleware")
    def __init__(self, *args, **kwargs):
        super(TracingMiddleware, self).__init__(*args, **kwargs)
        if not self._stackifyapm_instrumented:
            with self._instrumenting_lock:
                if not self._stackifyapm_instrumented:
                    if self.client.config.instrument_django_middleware:
                        self.instrument_middlewares()

                    TracingMiddleware._stackifyapm_instrumented = True

    def instrument_middlewares(self):
        middlewares = getattr(django_settings, "MIDDLEWARE", None) or getattr(
            django_settings, "MIDDLEWARE_CLASSES", None
        )
        if middlewares:
            for middleware_path in middlewares:
                module_path, class_name = middleware_path.rsplit(".", 1)
                try:
                    module = import_module(module_path)
                    middleware_class = getattr(module, class_name)
                    if middleware_class == type(self):
                        continue
                    if hasattr(middleware_class, "process_request"):
                        wrapt.wrap_function_wrapper(middleware_class, "process_request", process_request_wrapper)
                    if hasattr(middleware_class, "process_response"):
                        wrapt.wrap_function_wrapper(middleware_class, "process_response", process_response_wrapper)
                except ImportError:
                    client.logger.info("Can't instrument middleware {}".format(middleware_path))

    def process_view(self, request, view_func, view_args, view_kwargs):
        request._stackifyapm_view_func = view_func

    def process_request(self, request):
        try:
            stackifyapm.set_transaction_context(
                lambda: self.client.get_data_from_request(request, capture_body=self.client.config.prefix_enabled),
                "request",
            )

        except Exception:
            self.client and self.client.error_logger.error("Exception during timing of process request", exc_info=True)

    def process_response(self, request, response):
        try:
            if hasattr(response, "status_code"):
                transaction_name = ''
                if hasattr(request.resolver_match, "route"):
                    transaction_name = request.resolver_match.route
                elif getattr(request, "_stackifyapm_view_func", False):
                    transaction_name = get_name_from_func(request._stackifyapm_view_func)
                else:
                    transaction_name = get_name_from_path(request.path)

                if transaction_name:
                    transaction_name = build_name_with_http_method_prefix(transaction_name, request)
                else:
                    try:
                        transaction_name = request.build_absolute_uri()
                    except Exception:
                        self.client.error_logger.error("Exception during build_absolute_uri", exc_info=True)
                        transaction_name = 'default'  # makign sure we do have default name

                stackifyapm.set_transaction_name(transaction_name, override=True)
                stackifyapm.set_transaction_context(
                    lambda: self.client.get_data_from_request(request, capture_body=self.client.config.prefix_enabled),
                    "request",
                )
                stackifyapm.set_transaction_context(
                    lambda: self.client.get_data_from_response(response, capture_body=self.client.config.prefix_enabled),
                    "response",
                )

            transaction = execution_context.get_transaction()
            response._headers['x-stackifyid'] = ('X-StackifyID', get_stackify_header(transaction))

            content_type = get_value_from_key(response._headers, "content-type")
            content_length = get_value_from_key(response._headers, "content-length")
            content_encoding = get_value_from_key(response._headers, "content-encoding")
            content_disposition = get_value_from_key(response._headers, "content-disposition")

            if content_type:
                content_type = content_type[1]
            if content_length:
                content_length = content_length[1]
            if content_encoding:
                content_encoding = content_encoding[1]
            if content_disposition:
                content_disposition = content_disposition[1]

            if self.client.config.rum_enabled and should_insert_html(content_type, content_length, content_encoding, content_disposition):
                rum_script = get_rum_script_or_none(transaction)
                data = response.content
                if rum_script and can_insert_script(data):
                    data = insert_rum_script_to_head(data, rum_script)
                    response.content = data
                    response._headers['content-length'] = ('Content-Length', str(len(data)))

        except Exception:
            self.client and self.client.error_logger.error("Exception during timing of process response", exc_info=True)

        return response
