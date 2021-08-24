# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from collections import deque
from copy import copy
from importlib import import_module

from django.utils.regex_helper import normalize

from contrast.agent.middlewares.route_coverage.coverage_utils import (
    CoverageUtils,
    DEFAULT_ROUTE_METHODS,
)
from contrast.agent.settings_state import SettingsState
from contrast.extern.backports.functools_lru_cache import lru_cache

from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


@lru_cache(maxsize=1)
def is_django_1():
    settings = SettingsState()
    return settings.framework.version.major == "1"


def create_url(pattern_or_resolver):
    if is_django_1():
        pattern = pattern_or_resolver.regex.pattern
    else:
        pattern = pattern_or_resolver.pattern.regex.pattern

    try:
        normalized = normalize(pattern)[0][0]
        url = normalized.replace("%(", "{").replace(")", "}")
    except Exception:
        url = pattern_or_resolver.name

    return url


def get_method_info(pattern_or_resolver):
    method_types = []
    method_arg_names = "()"

    lowest_function = CoverageUtils.get_lowest_function_call(
        pattern_or_resolver.callback
    )

    if lowest_function is not None:
        method_arg_names = CoverageUtils.build_args_from_function(lowest_function)

        # this method returns a dict because it uses one to store state in the recursive function
        method_types_dict = CoverageUtils.check_for_http_decorator(lowest_function)
        method_types = method_types_dict.get("require_http_methods", [])

        if not isinstance(method_types, list):
            method_types = [method_types]

    return method_types or DEFAULT_ROUTE_METHODS, method_arg_names


def create_one_route(routes, method_type, method_arg_names, pattern_or_resolver):
    """
    Create a new RouteCoverage object and adds it to routes dict

    :param routes: dict of routes
    :param method_type:
    :param method_arg_names:
    :param pattern_or_resolver:
    :return: None, adds to routes dict which is updated through pass-by-reference
    """
    route = build_django_route(pattern_or_resolver, method_arg_names)

    route_id = str(id(pattern_or_resolver.callback))

    key = CoverageUtils.build_key(route_id, method_type)

    routes[key] = CoverageUtils.build_route_coverage(
        verb=method_type, url=create_url(pattern_or_resolver), route=route
    )


def create_routes(urlpatterns):
    if is_django_1():
        try:
            # Django 1.10 and above
            from django.urls.resolvers import RegexURLPattern, RegexURLResolver
        except ImportError:
            # Django 1.9 and below
            from django.core.urlresolvers import RegexURLPattern, RegexURLResolver
    else:
        from django.urls.resolvers import (
            URLPattern as RegexURLPattern,
            URLResolver as RegexURLResolver,
        )

    routes = {}

    urlpatterns_deque = deque(urlpatterns)

    while urlpatterns_deque:
        url_pattern = urlpatterns_deque.popleft()

        if isinstance(url_pattern, RegexURLResolver):
            urlpatterns_deque.extend(url_pattern.url_patterns)

        elif isinstance(url_pattern, RegexURLPattern):
            method_types, method_arg_names = get_method_info(url_pattern)
            for method_type in method_types:
                create_one_route(routes, method_type, method_arg_names, url_pattern)
    return routes


def create_django_routes():
    """
    Grabs all URL's from the root settings and searches for possible required_method decorators

    In Django there is no implicit declaration of GET or POST. Often times decorators are used to fix this.

    Returns a dict of key = id, value = RouteCoverage.
    """

    from django.conf import settings

    if not settings.ROOT_URLCONF:
        logger.info("Application does not define settings.ROOT_URLCONF")
        logger.debug("Skipping enumeration of urlpatterns")
        return None

    try:
        root_urlconf = import_module(settings.ROOT_URLCONF)
    except Exception as exception:
        logger.debug("Failed to import ROOT_URLCONF: %s", exception)
        return None

    try:
        urlpatterns = root_urlconf.urlpatterns or []
    except Exception as exception:
        logger.debug("Failed to get urlpatterns: %s", exception)
        return None

    url_patterns = copy(urlpatterns)
    return create_routes(url_patterns)


def _function_loc(func):
    """Return the function's module and name"""
    return "{0.__module__}.{0.__name__}".format(func)


def build_django_route(obj, method_arg_names=None):
    if hasattr(obj, "lookup_str"):
        route = obj.lookup_str
    elif hasattr(obj, "callback"):
        cb = obj.callback
        route = _function_loc(cb)
    elif callable(obj):
        route = _function_loc(obj)
    else:
        logger.debug("WARNING: can't build django route for object type %s", type(obj))
        return ""

    if method_arg_names is None:
        method_arg_names = CoverageUtils.build_args_from_function(obj)

    route += method_arg_names
    return route
