# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.middlewares.route_coverage.coverage_utils import (
    CoverageUtils,
    DEFAULT_ROUTE_METHODS,
)


def create_flask_routes(app):
    """
    Returns all the routes registered to a Flask app as a dict
    :param app: Flask app
    :return: dict {route_id:  RouteCoverage}
    """
    routes = {}

    with app.app_context():
        for rule in list(app.url_map.iter_rules()):
            view_func = app.view_functions[rule.endpoint]

            route = build_flask_route(rule.endpoint, view_func)

            route_id = str(id(view_func))

            methods = rule.methods or DEFAULT_ROUTE_METHODS

            for method_type in methods:
                key = CoverageUtils.build_key(route_id, method_type)
                routes[key] = CoverageUtils.build_route_coverage(
                    verb=method_type,
                    url=CoverageUtils.get_normalized_uri(str(rule)),
                    route=route,
                )

    return routes


def build_flask_route(view_func_name, view_func):
    view_func_args = CoverageUtils.build_args_from_function(view_func)
    return view_func_name + view_func_args
