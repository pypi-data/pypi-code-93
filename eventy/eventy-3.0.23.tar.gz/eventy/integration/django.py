# Copyright (c) Qotto, 2021

"""
Django integration utilities

Utility functions to integrate the eventy protocol in django apps
"""
import logging
from typing import Callable

import django.http as vendor_django_http

import eventy.config.django
from eventy.trace_id import correlation_id_var, request_id_var
from eventy.trace_id.generator import gen_trace_id

logger = logging.getLogger(__name__)


def django_trace_middleware(
    get_response: Callable[[vendor_django_http.HttpRequest], vendor_django_http.HttpResponse]
) -> Callable:
    """
    Middleware to extract and propagate correlation_id and generate request_id.

    Log each access, except for health check on ``eventy.config.django.DJANGO_ACCESS_HEALTH_ROUTE``
    if ``eventy.config.django.DJANGO_ACCESS_DISABLE_HEALTH_LOGGING`` is set to True

    :param get_response: Actual response logic
    :return: Modified response
    """

    def _middleware(request: vendor_django_http.HttpRequest) -> vendor_django_http.HttpResponse:
        # test if access should be logged
        is_health_check: bool = request.method == 'GET' and request.path == eventy.config.django.DJANGO_ACCESS_HEALTH_ROUTE
        log_access: bool = not (is_health_check and eventy.config.django.DJANGO_ACCESS_DISABLE_HEALTH_LOGGING)

        # fetch or generate correlation_id
        correlation_id = None
        for key, val in request.headers.items():
            if key.lower() == 'x-correlation-id':
                correlation_id = val
        correlation_id_var.set(correlation_id or gen_trace_id(f'{request.method}_{request.path}'))

        # always generate request_id
        request_id_var.set(gen_trace_id(f'{request.method}_{request.path}'))

        # log request
        if log_access:
            logger.info(f'Request: {request.method} {request.path}')

        # get response
        response = get_response(request)

        # log response
        if log_access:
            logger.info(f'Response: {request.method} {request.path} {response.status_code} ({len(response.content)})')

        return response

    logger.info("Eventy for Django middleware initialized.")
    return _middleware
