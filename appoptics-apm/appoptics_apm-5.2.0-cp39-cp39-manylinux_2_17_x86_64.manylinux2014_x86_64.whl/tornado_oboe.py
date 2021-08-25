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
""" AppOptics APM instrumentation for Tornado.
"""
# useful methods for instrumenting Tornado
from __future__ import with_statement

import functools
import logging
import time

import tornado.web
from appoptics_apm import aoasync, util
from appoptics_apm.transaction_filter import UrlGetter

logger = logging.getLogger(__name__)


# instrumentation functions for tornado.web.RequestHandler
def request_handler_start(self):
    """ runs from the main HTTP server thread (doesn't set/get Context)

        takes 'self' parameter, which is the current RequestHandler
        instance (which holds the current HTTPRequest in self.request)
    """
    start_time = int(time.time() * 1e6)

    # check for X-Trace header in HTTP request
    url = UrlGetter(self.request.full_url())
    ctx, evt = util.Context.start_trace('tornado', xtr=self.request.headers.get("X-Trace"), url_getter=url)
    setattr(util.Context.transaction_dict, 'url_tran', url.get_url())

    if ctx.is_sampled() and evt.is_valid():
        if hasattr(self, '__class__') and hasattr(self.__class__, '__name__'):
            evt.add_info("Controller", self.__class__.__name__)
            evt.add_info("Action", self.request.method.lower())
        ctx.report(evt)
    self.request._appoptics_apm_ctx = ctx

    logger.debug('tornado_oboe::request_handler_start trace: {tr}'.format(tr=str(ctx)))
    self.request._appoptics_apm_span_start = start_time


RequestHandler_start = request_handler_start


def request_handler_finish(self):
    """ runs from the main HTTP server thread, or from write/flush() callback
        doesn't set/get Context; just checks if finish event was set by appoptics_apm_start()
    """
    if hasattr(self, 'get_status'):  # recent Tornado
        status_code = self.get_status()
    elif hasattr(self, '_status_code'):  # older Tornado
        status_code = self._status_code
    else:
        status_code = 500

    try:
        ctx = getattr(self.request, '_appoptics_apm_ctx', util.Context.get_default())
        start_time = getattr(self.request, '_appoptics_apm_span_start', None)
        if not ctx.get_transaction_name():
            ctx.set_transaction_name(
                '{controller}.{action}'.format(controller=self.__class__.__name__, action=self.request.method.lower()))
        setattr(util.Context.transaction_dict, 'domain', self.request.host)
        setattr(util.Context.transaction_dict, 'start_time', start_time)
        setattr(util.Context.transaction_dict, 'request_method', self.request.method)
        setattr(util.Context.transaction_dict, 'status_code', status_code)

        xtr = util.end_http_trace(ctx.layer)
        if xtr:
            # the received Context might have been invalid (i.e. xtr='') in which case we should not inject the x-trace
            self.set_header("X-Trace", xtr)
    except Exception as e:
        logger.error("AppOptics APM tornado_oboeerror: %s" % str(e))
    # clear the stored appoptics_apm event/metadata from the request object
    self.request._appoptics_apm_ctx = None


RequestHandler_finish = request_handler_finish


# instrumentation for tornado.httpclient.AsyncHTTPClient
def AsyncHTTPClient_start(request):
    """ takes 'request' param, which is the outgoing HTTPRequest, not the request currently being handled """
    # this is called from AsyncHTTPClient.fetch(), which runs from the RequestHandler's context
    util.log("entry", "cURL", keys={'cURL_URL': request.url, 'Async': True})
    ctx = util.Context.get_default()
    if hasattr(request, 'headers'):
        if hasattr(request.headers, '__setitem__'):  # could be dict or tornado.httputil.HTTPHeaders
            request.headers['X-Trace'] = str(ctx)  # add X-Trace header to outgoing request

    if ctx.is_sampled():
        request._appoptics_apm_ctx = ctx.copy()


def AsyncHTTPClient_finish(request, callback=None, headers=None):
    """
    fires exit event for Async HTTP requests.

    checks for wrapped metadata stored in user's callback function: if
    it exists, that metadata is used & updated when reporting the
    event, so that the callback will "happen after" the exit event.
    """
    if hasattr(callback, '_appoptics_apm_ctx'):  # wrapped callback contains md
        ev = callback._appoptics_apm_ctx.create_event('exit', 'cURL')  # adds edge to md
        if hasattr(request, '_appoptics_apm_ctx'):  # add edge to entry event for this async HTTP call
            ev.add_edge(request._appoptics_apm_ctx)
        mdobj = callback

    elif hasattr(request, '_appoptics_apm_ctx'):  # callback contains no metadata, but request obj does
        ev = request._appoptics_apm_ctx.create_event('exit', 'cURL')
        mdobj = request

    else:  # no metadata found
        return

    if headers and hasattr(headers, 'get') and headers.get('X-Trace', None):
        response_md = headers.get('X-Trace')
        ev.add_edge_str(response_md)  # add response X-Trace header

    mdobj._appoptics_apm_ctx.report(ev)  # increments metadata in mdobj


# used for wrapping stack contexts in Tornado v1.2 stack_context.py
class AppOpticsApmContextWrapper:
    def __init__(self, wrapped):
        self.wrapped = wrapped
        # get current context at wrap time (e.g. when preparing "done" callback for an async call)
        if util.Context.get_default().is_sampled():
            # store wrap-time context for use at call time
            self._appoptics_apm_ctx = util.Context.get_default().copy()

    def __call__(self, *args, **kwargs):
        with aoasync.AppOpticsApmContextManager(self):  # uses self._appoptics_apm_ctx as context
            return self.wrapped.__call__(*args, **kwargs)


# replacement for _StackContextWrapper in Tornado v2.x stack_context.py
class _StackContextWrapper(functools.partial):
    def __init__(self, *args, **kwargs):
        if util.Context.get_default().is_sampled():
            self._appoptics_apm_ctx = util.Context.get_default().copy()
        super(_StackContextWrapper, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        with aoasync.AppOpticsApmContextManager(self):
            return super(_StackContextWrapper, self).__call__(*args, **kwargs)


class AppOpticsApmBaseHandler(tornado.web.RequestHandler):
    """The base request handler to insert instrumentation code to the normal request
    handling processes. All the request handlers of the application need to inherit
    from this base class.
    """

    # pylint: disable-msg=abstract-method
    def prepare(self):
        """This function will be called by tornado.web.Application before the user
        defined handler. If a handler inherits from this base handler, it should call
        this function in its own prepare() function."""
        super(AppOpticsApmBaseHandler, self).prepare()
        if util.ready():
            request_handler_start(self)

    def finish(self, **kwargs):
        """This function will be called by tornado.web.Application after the user defined
        handler. If a handler inherits from this base handler, it should call this function
        in its own prepare() function."""
        if util.ready():
            request_handler_finish(self)
        super(AppOpticsApmBaseHandler, self).finish(**kwargs)


util.report_layer_init('tornado')
