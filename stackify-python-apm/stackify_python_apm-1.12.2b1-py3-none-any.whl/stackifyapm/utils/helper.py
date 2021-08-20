import inspect
import os
import re
import time
import threading
import multiprocessing

from stackifyapm.utils import compat
import stackifyapm

import base64
import json

_HEAD_RE = re.compile(b'<head[^>]*>', re.IGNORECASE)
_HEAD_STR_RE = re.compile('<head[^>]*>', re.IGNORECASE)
_HTML_RE = re.compile(b'<html[^>]*>', re.IGNORECASE)
_URL_ID_RE = re.compile(r'^(\d+)$', re.IGNORECASE)
_URL_EMAIL_RE = re.compile(r'^((([!#$%&\'*+\-\/=?^_`{|}~\w])|([!#$%&\'*+\-\/=?^_`{|}~\w][!#$%&\'*+\-\/=?^_`{|}~\.\w]{0,}[!#$%&\'*+\-\/=?^_`{|}~\w]))[@]\w+([-.]\w+)*\.\w+([-.]\w+)*)$', re.IGNORECASE)
_URL_GUID_RE = re.compile(r'^(?i)(\b[A-F0-9]{8}(?:-[A-F0-9]{4}){3}-[A-F0-9]{12}\b)$', re.IGNORECASE)
_URL_IP_RE = re.compile(r'^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$', re.IGNORECASE)


def get_current_time_in_millis():
    return time.time() * 1000


def get_current_time_in_string():
    return str(int(get_current_time_in_millis()))


def is_async_span():
    return hasattr(threading.current_thread(), 'transaction') or hasattr(multiprocessing.current_process(), 'transaction')


def get_stackify_header(transaction=None):
    if not transaction:
        return ""

    properties = transaction.get_meta_data().get('property_info')
    client_id = properties.get('clientId', None)
    device_id = properties.get('deviceId', None)

    stackify_params = ["V1"]
    transaction and stackify_params.append(str(transaction.get_trace_parent().trace_id))
    client_id and stackify_params.append("C{}".format(client_id))
    device_id and stackify_params.append("CD{}".format(device_id))

    return "|".join(stackify_params)


def get_rum_script_or_none(transaction):
    if transaction:
        meta_data = transaction.get_meta_data()

        if not meta_data:
            return ''

        application_info = meta_data.get('application_info')

        application_name = get_value_from_key(application_info, "application_name")
        environment = get_value_from_key(application_info, "environment")
        rum_script_url = get_value_from_key(application_info, "rum_script_url")
        rum_key = get_value_from_key(application_info, "rum_key")

        if not rum_script_url or not rum_key:
            return ''

        settings = {}

        rum_trace_parent = transaction.get_trace_parent()
        if rum_trace_parent:
            if rum_trace_parent.trace_id:
                settings["ID"] = rum_trace_parent.trace_id

        if application_name:
            application_name_b64 = base64.b64encode(application_name.encode("utf-8")).decode("utf-8")
            if (application_name_b64):
                settings["Name"] = application_name_b64

        if environment:
            environment_b64 = base64.b64encode(environment.encode("utf-8")).decode("utf-8")
            if (environment_b64):
                settings["Env"] = environment_b64

        reporting_url = transaction.get_reporting_url()
        if reporting_url:
            decoded_reporting_url = compat.unquote(reporting_url)
            reporting_url = mask_reporting_url(decoded_reporting_url)
            transaction_context = transaction.get_context()

            if transaction_context and "request" in transaction_context:
                request_method = transaction_context["request"]["method"]
                reporting_url = "{}-{}".format(request_method, reporting_url)

            settings["Trans"] = base64.b64encode(reporting_url.encode("utf-8")).decode("utf-8")

        if not settings:
            return ''

        rum_script_str = '<script type="text/javascript">(window.StackifySettings || (window.StackifySettings = {}))</script><script src="{}" data-key="{}" async></script>'.format(
            json.dumps(settings),
            rum_script_url,
            rum_key
        )

        stackifyapm.set_transaction_context(lambda: True, "rum")
        return rum_script_str

    return ''


def can_insert_script(data):
    try:
        data = str.encode(data)
    except TypeError:
        pass

    html_tag_found = _HTML_RE.search(data)

    return (
        html_tag_found and
        str.encode('</head>') in data and
        str.encode('<script type="text/javascript">(window.StackifySettings ||') not in data  # Temporary checking
    )


def insert_rum_script_to_head(data, script):
    head = _HEAD_RE.search(data)

    if not head or not script or not can_insert_script(data):  # TODO: limit data searching?
        return data

    index = head.end()
    return b''.join((data[:index], str.encode(script), data[index:]))


def insert_rum_script_to_head_str(data, script):
    head = _HEAD_STR_RE.search(data)

    if not head or not script or not can_insert_script(data):  # TODO: limit data searching?
        return data

    index = head.end()
    return ''.join((data[:index], script, data[index:]))


def should_insert_html(content_type=None, content_length=None, content_encoding=None, content_disposition=None):
    pass_through = False

    if content_length:
        try:
            content_length = int(content_length)
        except ValueError:
            pass_through = True

    if pass_through:
        return False

    if content_encoding is not None:
        # This will match any encoding, including if the
        # value 'identity' is used. Technically the value
        # 'identity' should only be used in the header
        # Accept-Encoding and not Content-Encoding. In
        # other words, a WSGI application should not be
        # returning identity. We could check and allow it
        # anyway and still do RUM insertion, but don't.

        return False

    if (content_disposition is not None and
            content_disposition.split(';')[0].strip().lower() ==
            'attachment'):
        return False

    if content_type is None:
        return False

    allowed_content_type = 'text/html'

    if content_type.split(';')[0] not in allowed_content_type:
        return False

    return True


def get_value_from_key(data, key):
    return data[key] if key in data else None


def safe_bytes_to_string(value=""):
    if isinstance(value, compat.binary_type):
        return value.decode('utf-8', errors='replace')

    return str(value or "")


def get_main_file():
    frame = inspect.stack()[-1]
    module = inspect.getmodule(frame[0])
    main_file = module and module.__file__.split(os.sep)[-1].split('.')[0]
    return main_file or "app"


def mask_string(raw_string):
    if (re.match(_URL_ID_RE, raw_string)):
        return '{id}'
    if (re.match(_URL_GUID_RE, raw_string)):
        return '{guid}'
    if (re.match(_URL_EMAIL_RE, raw_string)):
        return '{email}'
    if (re.match(_URL_IP_RE, raw_string)):
        return '{ip}'
    if (';' in raw_string):
        return raw_string[:raw_string.index(';')]
    return raw_string


def mask_reporting_url(raw_url):
    if not raw_url:
        return '/'

    parts = raw_url.split('/')

    if not len(parts):
        return '/'

    maskedParts = []

    for part in parts:
        maskedParts.append(mask_string(part))

    maskedUrl = '/'.join(maskedParts)

    if len(maskedUrl) == 1:
        return maskedUrl

    if maskedUrl.endswith('/'):
        return maskedUrl[:len(maskedUrl) - 1]

    return maskedUrl
