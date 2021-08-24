# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import contrast
from contrast.agent import scope
from contrast.agent.policy.trigger_node import TriggerNode
from contrast.agent.middlewares.base_django_middleware import DjangoBaseMiddleware
from contrast.agent.middlewares.response_wrappers.django_response_wrapper import (
    DjangoResponseWrapper,
)
from contrast.agent.request_context import RequestContext
from contrast.utils.decorators import cached_property, log_time_cm
from contrast.utils.exceptions.contrast_service_exception import (
    ContrastServiceException,
)

from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


class DjangoMiddleware(DjangoBaseMiddleware):
    """
    Newer style of Django Middleware; This middleware is for Django 1.10+ and 2.+.
    """

    setting_name = "MIDDLEWARE"

    def __init__(self, get_response=None):
        self.validate_middleware()
        super(DjangoMiddleware, self).__init__()

        self.get_response = get_response

    def __call__(self, request):
        if self.is_agent_enabled():
            body = self.get_body(request)
            if body is not None:
                context = RequestContext(request.environ, body)

                with contrast.CS__CONTEXT_TRACKER.lifespan(context):
                    return self.call_with_agent(context, request)

        return self.call_without_agent(request)

    def call_with_agent(self, context, request, environ=None):
        super(DjangoMiddleware, self).call_with_agent(context, request)

        try:
            self.prefilter(context)

            with log_time_cm("app code and get response"):
                response = self.get_response(request)

            with scope.contrast_scope():
                wrapped_response = DjangoResponseWrapper(response)

            context.extract_response_to_context(wrapped_response)

            self.postfilter(context)

            self.check_for_blocked(context)

        except ContrastServiceException as e:
            logger.warning(e)
            return self.call_without_agent(request)
        except Exception as e:
            return self.handle_exception(e)
        finally:
            self.handle_ensure(context, request)
            self.log_end_request_analysis(request.path)
            if self.settings.is_assess_enabled():
                contrast.STRING_TRACKER.ageoff()

        return response

    def call_without_agent(self, request):
        """
        Normal without middleware call
        """
        super(DjangoMiddleware, self).call_without_agent()
        return self.get_response(request)

    @cached_property
    def trigger_node(self):
        """
        Trigger node property used by assess reflected xss postfilter rule
        """
        method_name = self.get_response.__name__

        module, class_name, args, instance_method = self._process_trigger_handler(
            self.get_response
        )

        return (
            TriggerNode(module, class_name, instance_method, method_name, "RETURN"),
            args,
        )
