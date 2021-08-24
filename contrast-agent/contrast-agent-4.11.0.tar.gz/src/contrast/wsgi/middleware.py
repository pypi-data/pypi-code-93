# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.extern import six
from contrast.extern.webob import Request, Response

import contrast
from contrast.agent.policy.trigger_node import TriggerNode
from contrast.agent.middlewares.base_middleware import BaseMiddleware
from contrast.agent.middlewares.environ_tracker import track_environ_sources
from contrast.agent.request_context import RequestContext
from contrast.utils.decorators import cached_property, fail_safely, log_time_cm
from contrast.utils.exceptions.security_exception import SecurityException
from contrast.utils.exceptions.contrast_service_exception import (
    ContrastServiceException,
)
from contrast.utils.object_utils import get_name

from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


class WSGIMiddleware(BaseMiddleware):
    """
    Contrast middleware; PEP-333(3) WSGI-compliant
    """

    def __init__(self, wsgi_app, app_name="WSGI Application"):
        self.app_name = app_name

        super(WSGIMiddleware, self).__init__()

        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        if self.is_agent_enabled():

            context = RequestContext(environ)
            with contrast.CS__CONTEXT_TRACKER.lifespan(context):
                return self.call_with_agent(context, environ, start_response)

        return self.call_without_agent(environ, start_response)

    def call_with_agent(self, context, environ, start_response):
        self.log_start_request_analysis(environ.get("PATH_INFO"))

        track_environ_sources("wsgi", context, environ)

        try:
            self.prefilter(context)

            with log_time_cm("app code and get response"):
                # this returns a webob response class, which already
                # implements BaseResponseWrapper's requirements
                response = Request(environ).get_response(self.wsgi_app)

            context.extract_response_to_context(response)

            self.postfilter(context)

            self.check_for_blocked(context)

            return response(environ, start_response)

        except ContrastServiceException as e:
            logger.warning(e)
            return self.call_without_agent(environ, start_response)
        except Exception as e:
            response = self.handle_exception(e)
            return response(environ, start_response)
        finally:
            self.handle_ensure(context, context.request)
            self.log_end_request_analysis(context.request.path)
            if self.settings.is_assess_enabled():
                contrast.STRING_TRACKER.ageoff()

    def generate_security_exception_response(self):
        return Response(self.OVERRIDE_MESSAGE, SecurityException.STATUS)

    def call_without_agent(self, environ, start_response):
        """
        Normal without middleware call
        """
        super(WSGIMiddleware, self).call_without_agent()
        return self.wsgi_app(environ, start_response)

    def get_route_coverage(self):
        """
        Unlike frameworks, WSGI is a spec, so it does not have a way to register routes.
        As such, there is no way to discover routes. Instead, routes will be added as
        they are visited via check for new routes.

        :return: empty dict
        """
        return {}

    @cached_property
    def trigger_node(self):
        """
        WSGI-specific trigger node used by reflected xss postfilter rule

        The rule itself is implemented in the base middleware but we need to
        provide a WSGI-specific trigger node for reporting purposes.
        """
        method_name = (
            self.wsgi_app.__name__ if hasattr(self.wsgi_app, "__name__") else "wsgi_app"
        )

        module, class_name, args, instance_method = self._process_trigger_handler(
            self.wsgi_app
        )

        return (
            TriggerNode(module, class_name, instance_method, method_name, "RETURN"),
            args,
        )

    @fail_safely("Unable to get WSGI view func")
    def get_view_func(self, request):
        """
        While most frameworks define view functions, WSGI doesn't so we will rely
        on the path information for reporting.
        If there is no path information, return an empty string

        :param request: RequestContext instance
        :return: string of path information for this request
        """
        return request.environ.get("PATH_INFO", "")

    @fail_safely("Unable to build route", return_value="")
    def build_route(self, view_func, url):
        return url.replace("/", "")


def get_original_app_or_fail(app, orig_app_class):
    _app = find_original_application(app, orig_app_class)
    if isinstance(_app, orig_app_class):
        return _app

    msg = (
        "Unable to find the original {0} Application object. "
        "Please provide the original {0} Application object as the second argument to ContrastMiddleware.".format(
            get_name(orig_app_class)
        )
    )

    logger.error(msg)
    raise RuntimeError(msg)


@fail_safely("Unable to find original WSGI application object")
def find_original_application(wsgi_app, orig_app_class, depth=20):
    """
    Recursively search through the WSGI middleware chain of `wsgi_app` for an
    application of type `orig_app_class`. Most WSGI middlewares are implemented as
    classes and maintain a reference to their wrapped app as an attribute. This function
    makes a best effort to find this attribute on each successive middleware until it
    sees an instance of the desired class.

    This method is not intended to succeed every time, as it is based off of several
    assumptions that will not always be true. It needs only succeed often enough that
    customers rarely need to supply additional information to framework-specific
    middleware constructors.

    This delegates to _find_original_application to ensure that we don't get an extra
    @fail_safely on each recursive call.
    """
    return _find_original_application(wsgi_app, orig_app_class, depth)


def _find_original_application(wsgi_app, orig_app_class, depth):
    if isinstance(wsgi_app, orig_app_class):
        return wsgi_app
    if depth == 0:
        return None

    # this list is in approximate order of expected app attribute name; since this
    # algorithm is greedy, we iterate over the best candidates first
    for attr_name in [
        "app",
        "application",
        "wsgi_app",
        "_app",
        "_wsgi_app",
        "_application",
        "wsgi_application",
        "_wsgi_application",
        "wrapped_app",
        "wrapped_application",
        "wrapped",
        "wrap_app",
        "wrap",
        "registry",  # pyramid
        "_wrapped",
        "_wrapped_app",
        "_wrapped_application",
        "_wrap_app",
        "_wrap",
    ]:
        attr = getattr(wsgi_app, attr_name, None)

        # The name check is a very unfortunate thing we have to do since
        # Pyramid's Registry obj is not a callable.
        if six.callable(attr) or attr.__class__.__name__ == "Registry":
            return _find_original_application(attr, orig_app_class, depth - 1)

    return None
