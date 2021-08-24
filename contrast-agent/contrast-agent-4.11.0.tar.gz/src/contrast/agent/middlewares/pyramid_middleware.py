# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import contrast
from contrast.agent.policy.trigger_node import TriggerNode
from contrast.agent.middlewares.base_middleware import BaseMiddleware
from contrast.agent.middlewares.environ_tracker import track_environ_sources
from contrast.agent.middlewares.route_coverage.pyramid_routes import PyramidRoutesMixin

from contrast.agent.request_context import RequestContext
from contrast.utils.decorators import cached_property, log_time_cm
from contrast.utils.exceptions.contrast_service_exception import (
    ContrastServiceException,
)

from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")

WEBOB = "webob"


class PyramidMiddleware(PyramidRoutesMixin, BaseMiddleware):
    def __init__(self, handler, registry):
        self.registry = registry
        self.app_name = self.get_app_name()

        super(PyramidMiddleware, self).__init__()

        self.handler = handler

    def get_app_name(self):
        try:
            return self.registry.package_name
        except Exception:
            return "pyramid_app"

    def __call__(self, request):
        if self.is_agent_enabled() and request:
            context = RequestContext(request.environ)
            with contrast.CS__CONTEXT_TRACKER.lifespan(context):
                return self.call_with_agent(request, context)

        return self.call_without_agent(request)

    def call_without_agent(self, request):
        """
        Normal without middleware call
        """
        super(PyramidMiddleware, self).call_without_agent()
        return self.handler(request)

    def call_with_agent(self, request, context):
        self.log_start_request_analysis(request.environ.get("PATH_INFO"))

        track_environ_sources(WEBOB, context, request.environ)

        try:
            self.prefilter(context)

            with log_time_cm("app code and get response"):
                response = self.handler(request)

            # Pyramid's response class is based on Webob's, which already
            # implements BaseResponseWrapper's requirements
            context.extract_response_to_context(response)

            self.postfilter(context)

            self.check_for_blocked(context)

            return response
        except ContrastServiceException as e:
            logger.warning(e)
            return self.call_without_agent(request)
        except Exception as e:
            return self.handle_exception(e)
        finally:
            self.handle_ensure(context, request)
            self.log_end_request_analysis(context.request.path)
            if self.settings.is_assess_enabled():
                contrast.STRING_TRACKER.ageoff()

    @cached_property
    def trigger_node(self):
        method_name = self.handler.__name__

        module, class_name, args, instance_method = self._process_trigger_handler(
            self.handler
        )

        return (
            TriggerNode(module, class_name, instance_method, method_name, "RETURN"),
            args,
        )

    def generate_security_exception_response(self):
        from pyramid.httpexceptions import HTTPForbidden

        return HTTPForbidden(explanation=self.OVERRIDE_MESSAGE)
