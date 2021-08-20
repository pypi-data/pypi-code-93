import os
import pkg_resources
import sys

from stackifyapm.base import Client
from stackifyapm.conf import constants
from stackifyapm.decorators import exception_handler
from stackifyapm.handlers.exceptions import get_exception_context
from stackifyapm.utils import compat
from stackifyapm.utils.helper import can_insert_script
from stackifyapm.utils.helper import get_stackify_header
from stackifyapm.instrumentation.control import instrument
from stackifyapm.traces import execution_context
from stackifyapm.traces import set_transaction_context
from stackifyapm.utils import get_url_data
from stackifyapm.utils.helper import get_main_file, get_value_from_key
from stackifyapm.utils.helper import get_rum_script_or_none, insert_rum_script_to_head_str, should_insert_html


def includeme(config):
    config.add_tween('stackifyapm.contrib.pyramid.stackifyapm_tween_factory')
    config.scan('stackifyapm.contrib.pyramid')


def get_data_from_request(request, capture_body=False):
    result = {
        "method": request.method,
        "url": get_url_data(request.url),
    }

    if not capture_body:
        return result

    result["headers"] = dict(**request.headers)

    if request.method in constants.HTTP_WITH_BODY:
        body = ""
        if request.content_type == "application/x-www-form-urlencoded":
            body = compat.multidict_to_dict(request.form)
        elif request.content_type and request.content_type.startswith("multipart/form-data"):
            body = compat.multidict_to_dict(request.form)
        else:
            try:
                body = request.text
            except Exception:
                pass

        if body:
            result["body"] = body
            result["body_size"] = len(body)

    return result


def get_data_from_response(response=None, capture_body=False):
    result = {
        "status_code": response and response.status_int or 500,
    }

    if not capture_body:
        return result

    if response:
        result["headers"] = dict(**response.headers)
        result["body"] = response.text
        result["body_size"] = len(response.text)

    return result


def make_client(registry, **defaults):
    instrument_all_exclude = registry.settings.get('INSTRUMENT_ALL_EXCLUDE', "")
    excludes = instrument_all_exclude and instrument_all_exclude.split(',') or []
    excludes.append(get_main_file())

    config = {
        "FRAMEWORK_NAME": "pyramid",
        "FRAMEWORK_VERSION": pkg_resources.get_distribution("pyramid").version,
        "BASE_DIR": os.getcwd(),
        "INSTRUMENT_ALL_EXCLUDE": ','.join(excludes),
    }
    defaults.update(registry.settings)
    return Client(config, **defaults)


class stackifyapm_tween_factory(object):

    @exception_handler(message="Error creating pyramid StackifyAPM")
    def __init__(self, handler, registry):
        self.handler = handler
        self.registry = registry
        self.client = make_client(registry)
        instrument(client=self.client)

    def __call__(self, request):
        response = None
        self.client.begin_transaction('request', client=self.client)
        try:
            set_transaction_context(
                lambda: get_data_from_request(request, capture_body=self.client.config.prefix_enabled),
                "request",
            )

            transaction = execution_context.get_transaction()

            response = self.handler(request)
            response.headers["X-StackifyID"] = get_stackify_header(transaction)

            content_type = get_value_from_key(response.headers, "Content-Type")
            content_length = get_value_from_key(response.headers, "Content-Length")
            content_encoding = get_value_from_key(response.headers, "Content-Encoding")
            content_disposition = get_value_from_key(response.headers, "Content-Disposition")

            if self.client.config.rum_enabled and should_insert_html(content_type, content_length, content_encoding, content_disposition):
                rum_script = get_rum_script_or_none(transaction)
                data = response.text
                if rum_script and can_insert_script(data):
                    data = insert_rum_script_to_head_str(data, rum_script)
                    response.text = data

            return response
        except Exception:
            exc_info = sys.exc_info()
            if exc_info:
                exception = exc_info[1]
                traceback = exc_info[2]
                self.client.capture_exception(
                    exception=get_exception_context(exception, traceback)
                )
            raise
        finally:
            view_name = request.view_name if hasattr(request, 'view_name') else None
            transaction_name = request.matched_route.pattern if request.matched_route else view_name
            transaction_name = " ".join((request.method, transaction_name)) if transaction_name else ""

            view_class = hasattr(request, '__view__') and request.__view__.__class__.__name__ or None
            route_name = '_'.join(request.request_iface.getName().split('_')[:-1])
            reporting_url = view_class and route_name and "{}#{}".format(view_class, route_name) or view_class or route_name or transaction_name

            set_transaction_context(
                lambda: get_data_from_response(response, capture_body=self.client.config.prefix_enabled),
                "response",
            )
            set_transaction_context(reporting_url, "reporting_url")
            self.client.end_transaction(transaction_name)
