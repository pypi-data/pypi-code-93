# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
# in a Flask environment, we should always have Werkzeug
from werkzeug.exceptions import NotFound

from contrast.agent.assess.rules.config import (
    FlaskHttpOnlyRule,
    FlaskSecureFlagRule,
    FlaskSessionAgeRule,
)
from contrast.agent.middlewares.route_coverage.flask_routes import (
    create_flask_routes,
    build_flask_route,
)
from contrast.wsgi.middleware import WSGIMiddleware
from contrast.utils.decorators import fail_safely


class FlaskMiddleware(WSGIMiddleware):
    def __init__(self, app):
        self.app = app

        self.config_rules = [
            FlaskSessionAgeRule(),
            FlaskSecureFlagRule(),
            FlaskHttpOnlyRule(),
        ]

        super(FlaskMiddleware, self).__init__(app.wsgi_app, app_name=app.name)

    def get_routes_on_first_request(self):
        """
        If an app is None, we won't do coverage.

        Flask requires there to be an app in the request context. There is only a
        context on init, which we use, and during the `self.wsgi_app` call. That is why
        flask.current_app.app_context doesn't work. There is nothing on the LocalProxy
        request context thread yet.
        """
        if self.app is None:
            return
        super(FlaskMiddleware, self).get_routes_on_first_request()

    @fail_safely("Unable to get route coverage", return_value={})
    def get_route_coverage(self):
        return create_flask_routes(self.app)

    @fail_safely("Unable to get Flask view func")
    def get_view_func(self, request):
        adapter = self.app.url_map.bind("empty")

        if None in (request, adapter):
            return None

        try:
            match = adapter.match(request.path, method=request.method)
        except NotFound:
            match = None

        func = None
        if match is not None:
            func = self.app.view_functions[match[0]]

        return func

    @fail_safely("Unable to build route", return_value="")
    def build_route(self, view_func, url):
        return build_flask_route(view_func.__name__, view_func)

    @fail_safely("Failed to run config scanning rules")
    def scan_configs(self):
        for rule in self.config_rules:
            rule.apply(self.app)
