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
from contrast.utils.decorators import cached_property
from contrast.utils.exceptions.contrast_service_exception import (
    ContrastServiceException,
)

from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


class DjangoMiddleware(DjangoBaseMiddleware):
    """
    Legacy style Django Middleware. For Django versions 1.9 and below.

    It does not have the same __call__ style as previously. The old style has a method for the incoming request and
    outgoing response.
    """

    setting_name = "MIDDLEWARE_CLASSES"

    def __init__(self, *args):
        """
        Older style of Django Middleware; This middleware is for Django 1.9 and below
        (Django 1.10 is also supported but use DjangoMiddleware when possible instead)

        Unlike most framework middlewares, Django 1.9 versions and below call the __init__
        method of all middlewares on the first request made to the app, not when the app
        web server is initialized. This means that this middleware and all of its settings,
        including connection to Speedracer, will not happen until a first request is made to the app.

        Keeping the unused argument *args will allow this middleware to load even if used with the wrong
        Django middleware style. This way we can fail more gracefully, with a helpful message to the user.
        """
        self.validate_middleware()
        super(DjangoMiddleware, self).__init__()

        self.context = None

    def process_request(self, request):
        """
        Process request will only run the prefilter on the request context

        No work on the response is done here
        """
        if self.is_agent_enabled():
            body = self.get_body(request)
            if body is not None:
                context = RequestContext(request.environ, body)
                self.context = context

                # cannot use with contrast.CS__CONTEXT_TRACKER.lifespan(context) because we don't want
                # to delete the context until calling process_response
                contrast.CS__CONTEXT_TRACKER.set_current(context)
                return self.call_with_agent(context, request)

        return self.call_without_agent(request)

    def call_without_agent(self, request):
        """
        Normal without middleware call
        """
        super(DjangoMiddleware, self).call_without_agent()

    def call_with_agent(self, context, request):
        super(DjangoMiddleware, self).call_with_agent(context, request)

        try:
            self.prefilter(context)
        except ContrastServiceException as e:
            logger.warning(e)
            self.call_without_agent(request)
        except Exception as e:
            if self.settings.is_assess_enabled():
                contrast.STRING_TRACKER.ageoff()
            return self.handle_exception(e)

        return None

    def process_exception(self, request, exception):
        """
        Process exception is called when a view raises an exception

        We check if the exception is our own and handle it accordingly. We make sure to
        send any findings that may have occurred prior to the exception. This enables
        us to trigger findings even when the trigger function itself calls an
        exception.
        """
        try:
            return self.handle_exception(exception)
        except ContrastServiceException as e:
            logger.warning(e)
            return self.call_without_agent(request)
        except Exception:
            self.handle_ensure(self.context, request)
            raise

    def process_response(self, request, response):
        """
        Process response wraps the response and then runs the postfilter rules
        """
        if self.context is None:
            return response

        try:
            # This is to make sure that if an application catches our
            # SecurityException, we still block if necessary. Doing this before
            # trying to wrap the response makes sure that we handle the case
            # where the response is None because a SecurityException was raised
            # during process_view.
            self.check_for_blocked(self.context)

            with scope.contrast_scope():
                cs__response = DjangoResponseWrapper(response)

            self.context.extract_response_to_context(cs__response)

            self.postfilter(self.context)

            return response

        except Exception as e:
            return self.handle_exception(e)
        finally:
            self.handle_ensure(self.context, request)
            if request is not None:
                self.log_end_request_analysis(request.path)
            if self.settings.is_assess_enabled():
                contrast.STRING_TRACKER.ageoff()
            contrast.CS__CONTEXT_TRACKER.delete_current()
            self.context = None

    @cached_property
    def trigger_node(self):
        """
        Trigger node property used by assess reflected xss postfilter rule
        """
        try:
            from django.apps import apps

            app = apps.app_configs[self.app_name]
            module = app.module.__name__
            method_name = app.name
        except Exception:
            logger.warning("Failed to get django app metadata for xss trigger")
            module = "<app module>"
            method_name = "<django app>"

        return TriggerNode(module, "", False, method_name, "RETURN"), ()
