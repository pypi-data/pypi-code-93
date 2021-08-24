# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import os
import sys

from contrast.agent.assess.rules.config import (
    DjangoHttpOnlyRule,
    DjangoSecureFlagRule,
    DjangoSessionAgeRule,
)

from contrast.wsgi.middleware import WSGIMiddleware
from contrast.agent.middlewares.route_coverage.django_routes import (
    create_django_routes,
    build_django_route,
)
from contrast.utils.decorators import fail_safely

try:
    from django.urls import get_resolver
except ImportError:
    from django.core.urlresolvers import get_resolver


from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


class DjangoWSGIMiddleware(WSGIMiddleware):
    """
    A subclass of the WSGI middleware that provides django route coverage and config
    scanning.

    This is not a Django-style middleware - it must wrap django's WSGI_APPLICATION,
    and does not belong in MIDDLEWARE / MIDDLEWARE_CLASSES.
    """

    def __init__(self, wsgi_app):
        self.app_name = self.get_app_name()

        self.config_rules = [
            DjangoSessionAgeRule(),
            DjangoSecureFlagRule(),
            DjangoHttpOnlyRule(),
        ]

        super(DjangoWSGIMiddleware, self).__init__(wsgi_app, self.app_name)

    def get_app_name(self):
        try:
            from django.conf import settings

            wsgi_application = settings.WSGI_APPLICATION

            return wsgi_application.split(".")[0]
        except Exception:
            return "Django Application"

    @fail_safely("Unable to get Django view func")
    def get_view_func(self, request):
        match = get_resolver().resolve(request.path_info or "/")
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
