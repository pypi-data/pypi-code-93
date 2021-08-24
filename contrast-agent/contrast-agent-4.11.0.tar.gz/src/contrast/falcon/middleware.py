# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.wsgi.middleware import WSGIMiddleware, get_original_app_or_fail
from contrast.agent.middlewares.route_coverage.falcon_routes import (
    create_falcon_routes,
    get_view_method,
    build_falcon_route,
)
from contrast.agent.assess.rules.config.falcon_secure_flag_rule import (
    FalconSecureFlagRule,
)

from contrast.utils.decorators import fail_safely, fail_quietly

from contrast.extern import structlog as logging
import falcon

logger = logging.getLogger("contrast")


class FalconMiddleware(WSGIMiddleware):
    def __init__(self, app, orig_falcon_api_instance=None):

        _app = (
            orig_falcon_api_instance
            if orig_falcon_api_instance is not None
            and isinstance(orig_falcon_api_instance, falcon.API)
            else get_original_app_or_fail(app, falcon.API)
        )
        self.falcon_app = _app
        # used for route coverage only for falcon middleware
        self.endpoint_cls = None

        self.config_rules = (FalconSecureFlagRule(),)

        # Since Falcon is WSGI-based, there is no way to retrieve the app name.
        # Use common config to define an app name.
        super(FalconMiddleware, self).__init__(_app, app_name="Falcon Application")

    @fail_safely("Unable to get route coverage", return_value={})
    def get_route_coverage(self):
        return create_falcon_routes(self.falcon_app)

    @fail_quietly("Unable to get Falcon view func")
    def get_view_func(self, request):
        path = request.path
        if not path:
            return None

        route_info = self.falcon_app._router.find(path)
        if not route_info:
            return None

        self.endpoint_cls, _, _, _ = route_info
        view_func = get_view_method(self.endpoint_cls, request.method)
        return view_func

    @fail_safely("Unable to build route", return_value="")
    def build_route(self, view_func, url):
        return build_falcon_route(view_func, self.endpoint_cls)

    @fail_safely("Failed to run config scanning rules")
    def scan_configs(self):
        """
        Run config scanning rules for assess
        """
        for rule in self.config_rules:
            rule.apply(self.falcon_app.resp_options)
