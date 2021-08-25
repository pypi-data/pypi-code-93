#    Copyright 2021 SolarWinds, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
""" AppOptics APM instrumentation for requests.

Instrumentation is done in urllib3.
"""
import logging

from decorator import decorator

import appoptics_apm.util as util

logger = logging.getLogger(__name__)

HTTPLIB_LAYER = 'httplib'


def safeindex(_list, index):
    return _list[index] if len(_list) > index else None


def safeget(obj, key):
    return obj.get(key, None) if obj and hasattr(obj, 'get') else None


def wrap_request_putrequest(func, f_args, f_kwargs):
    self = safeindex(f_args, 0)
    if self:
        try:
            # the _protocol attribute is currently only available in HTTPSConnection objects
            protocol = self._protocol
        except AttributeError:
            protocol = 'http'
        try:
            host = self.host
        except AttributeError:
            host = 'unkown_host'
        try:
            port = self.port
        except AttributeError:
            port = 'unkown_port'
        path = safeindex(f_args, 2) or safeget(f_kwargs, 'url') or '/'
        self.__appoptics_apm_http_method = safeindex(f_args, 1) or safeget(f_kwargs, 'method')
        self.__appoptics_apm_remote_url = "{}://{}:{}{}".format(protocol, host, port, path)
    return f_args, f_kwargs, {}


def wrap_request_endheaders(func, *f_args, **f_kwargs):
    ctx = util.Context.get_default()
    if not ctx.is_valid():
        return func(*f_args, **f_kwargs)

    self = safeindex(f_args, 0)
    if self:
        # X-Trace always needs to be propagated if there is a valid context
        self.putheader('X-Trace', str(ctx))
    try:
        res = func(*f_args, **f_kwargs)
    except Exception:
        util.log_exception()
        util.log('exit', HTTPLIB_LAYER, store_backtrace=False)
        raise
    return res


def wrap_request_getresponse(func, f_args, f_kwargs, res):
    kvs = {
        'Spec': 'rsc',
        'IsService': True,
    }
    self = safeindex(f_args, 0)
    if self:
        try:
            kvs['RemoteURL'] = str(self.__appoptics_apm_remote_url)
        except AttributeError:
            pass
        try:
            kvs['HTTPMethod'] = str(self.__appoptics_apm_http_method)
        except AttributeError:
            pass
    try:
        kvs['HTTPStatus'] = str(res.status)
    except AttributeError:
        pass
    xtr = ''
    try:
        # Check if the HTTP header contains a non-empty X-Trace
        xtr = res.getheader('x-trace') or xtr
    except AttributeError:
        pass
    edge_str = xtr if util.Metadata.fromString(xtr).isSampled() else None
    return kvs, edge_str


def wrap(module):
    try:
        # Wrap putrequest.  This marks the beginning of the request, and is also
        # where
        wrapper_putrequest = util.log_method(
            HTTPLIB_LAYER,
            before_callback=wrap_request_putrequest,
            send_exit_event=False,
            store_backtrace=util._collect_backtraces('httplib'))
        setattr(module.HTTPConnection, 'putrequest', wrapper_putrequest(module.HTTPConnection.putrequest))

        # endheaders must be wrapped manually, as X-Trace must be injected even if the request is not sampled
        fn = getattr(module.HTTPConnection, 'endheaders', None)
        if hasattr(fn, '__func__'):  # Is this a bound method of an object
            fn = fn.__func__  # then wrap the unbound method
        setattr(module.HTTPConnection, 'endheaders', decorator(wrap_request_endheaders, fn))
        logger.info('wrap wraps {} of {} object'.format(fn.__name__, module.HTTPConnection.__name__))

        wrapper_getresponse = util.log_method(HTTPLIB_LAYER, callback=wrap_request_getresponse, send_entry_event=False)
        setattr(module.HTTPConnection, 'getresponse', wrapper_getresponse(module.HTTPConnection.getresponse))
    except Exception as e:
        logger.error("AppOptics APM error: %s" % str(e))


if util.ready():
    try:
        import httplib
        wrap(httplib)
    except ImportError:
        import http.client
        wrap(http.client)
