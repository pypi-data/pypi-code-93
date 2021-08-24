# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import os
import sys

from contrast.agent import scope
from contrast.agent.assess.policy.source_node import SourceNode
from contrast.agent.assess.policy.source_policy import cs__apply_source
from contrast.agent.assess.rules.config import (
    DjangoHttpOnlyRule,
    DjangoSecureFlagRule,
    DjangoSessionAgeRule,
)

from contrast.agent.middlewares.base_middleware import BaseMiddleware
from contrast.agent.middlewares.environ_tracker import (
    track_cookie_sources,
    track_environ_sources,
)
from contrast.agent.middlewares.route_coverage.django_routes import (
    create_django_routes,
    build_django_route,
)
from contrast.utils.decorators import fail_safely
from contrast.utils.exceptions.wrong_django_middleware_exception import (
    WrongDjangoMiddlewareException,
)

FILE_NODE_DICT = {
    "module": "django.http.request",
    "class_name": "HttpRequest",
    "instance_method": False,
    "method_name": "FILES",
    "target": "RETURN",
    "type": "PARAMETER",
}

from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


class DjangoBaseMiddleware(BaseMiddleware):
    """
    Base class for all django middlewares.
    """

    def __init__(self):
        self.app_name = self.get_app_name()

        self.config_rules = [
            DjangoSessionAgeRule(),
            DjangoSecureFlagRule(),
            DjangoHttpOnlyRule(),
        ]

        super(DjangoBaseMiddleware, self).__init__()

    def get_app_name(self):
        try:
            from django.conf import settings

            wsgi_application = settings.WSGI_APPLICATION

            return wsgi_application.split(".")[0]
        except:
            return "root"

    @fail_safely("Unable to get Django view func")
    def get_view_func(self, request):
        match = request.resolver_match
        if not match:
            return None

        return match.func

    @fail_safely("Unable to build route", return_value="")
    def build_route(self, view_func, url):
        return build_django_route(view_func)

    @fail_safely("Unable to get route coverage", return_value={})
    def get_route_coverage(self):
        """
        Route Coverage is the Assess feature that looks for routes generally defined
        in Django apps in a file like urls.py
        """
        return create_django_routes()

    def generate_security_exception_response(self):
        from django.http.response import HttpResponseForbidden

        return HttpResponseForbidden(content=self.OVERRIDE_MESSAGE)

    def call_with_agent(self, context, request):
        self.log_start_request_analysis(request.path)

        # For now, django does not track the wsgi.input stream since it's not a true IO
        # stream object and we have other ways of getting the sources we need. No need
        # to track request.META since it is equivalent to request.environ.
        track_environ_sources("django", context, request.environ, skip_wsgi_input=True)
        track_cookie_sources("django", context, request.COOKIES)
        with scope.contrast_scope():
            self.track_files(context, request)

    def track_files(self, context, request):
        """
        Add uploaded files as sources
        """
        if not self.settings.is_assess_enabled():
            return

        node = SourceNode.from_dict("django", FILE_NODE_DICT)
        for name, fileobj_list in request.FILES.lists():
            cs__apply_source(context, node, name, request, name, (), {})
            for fileobj in fileobj_list:
                if hasattr(fileobj, "file") and hasattr(fileobj.file, "cs__source"):
                    fileobj.file.cs__source = True
                    fileobj.file.cs__source_type = "MULTIPART_CONTENT_DATA"
                    fileobj.file.cs__source_tags = ["UNTRUSTED", "CROSS_SITE"]

                cs__apply_source(
                    context, node, fileobj.name, request, fileobj.name, (), {}
                )

    def validate_middleware(self):
        """
        Verify that the middleware is being used properly (legacy -> MIDDLEWARE_CLASSES, standard -> MIDDLEWARE).
        If it is not, raise a RuntimeError with a helpful error message.
        """
        from django.conf import settings

        middleware_name = ".".join([self.__class__.__module__, self.__class__.__name__])
        middlewares = getattr(settings, self.setting_name, []) or []
        if middleware_name not in middlewares:
            # isinstance(self, LegacyDjangoMiddleware) would require a circular import
            raise WrongDjangoMiddlewareException("legacy" in self.__class__.__module__)

    @staticmethod
    @fail_safely(
        "Unable to access request body, likely due to an exhaustive read by an earlier"
        " middleware. We suggest moving the contrast middleware higher up in the"
        " middleware stack."
    )
    def get_body(request):
        return request.body

    @fail_safely("Failed to run config scanning rules")
    def scan_configs(self):
        """
        Run config scanning rules for assess

        Overridden from base class; gets called from base class
        """
        from django.conf import settings as app_settings

        app_config_module_name = os.environ.get("DJANGO_SETTINGS_MODULE")
        if not app_config_module_name:
            logger.warning("Unable to find Django settings for config scanning")
            return

        app_config_module = sys.modules.get(app_config_module_name)
        if not app_config_module:
            logger.warning("Django settings module not loaded; can't scan config")
            return

        for rule in self.config_rules:
            rule.apply(app_settings, app_config_module)
