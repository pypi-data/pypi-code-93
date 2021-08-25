# -*- coding: utf-8 -*-
# copyright 2021-2021 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-prometheus views/forms/actions/components for web ui"""

# inspired from github/pypi packages [gandi-]pyramid-prometheus

from time import time
from functools import partial

from pyramid.interfaces import IRoutesMapper
from pyramid.response import Response
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.tweens import EXCVIEW

from prometheus_client import (
    generate_latest,
    CONTENT_TYPE_LATEST,
    REGISTRY,
    Counter,
    Gauge,
    Summary,
    Histogram,
    Info,
)
from cubicweb.debug import subscribe_to_debug_channel, unsubscribe_to_debug_channel

METRIC_TYPE = {
    "counter": Counter,
    "gauge": Gauge,
    "summary": Summary,
    "histogram": Histogram,
    "info": Info,
    # "enum": Enum,
}

PD_METRICS = {}  # pyramid metrics
CW_METRICS = {}  # cubicweb metrics

SLOW_REQUEST_THRESHOLD = 1  # seconds


def get_metrics(request):
    """Pyramid view that return the metrics"""
    request.response.content_type = CONTENT_TYPE_LATEST
    resp = Response(content_type=CONTENT_TYPE_LATEST)
    resp.body = generate_latest(REGISTRY)
    return resp


def get_route_name_and_pattern(request):
    if request.matched_route is None:
        route_name = ""
        path_info_pattern = ""
        routes_mapper = request.registry.queryUtility(IRoutesMapper)
        if routes_mapper:
            info = routes_mapper(request)
            if info and info["route"]:
                path_info_pattern = info["route"].pattern
    else:
        route_name = request.matched_route.name
        path_info_pattern = request.matched_route.pattern
    return route_name, path_info_pattern


def prometheus_pyramid_settings(settings):
    for key in settings:
        if key.startswith("prometheus.pyramid."):
            _, _, param = key.split(".")
            active = bool(settings[key])
            if active:
                yield param


def prometheus_cw_settings(settings):
    for key in settings:
        if key.startswith("prometheus.cubicweb."):
            _, _, channel, param = key.split(".")
            metric_type = settings[key].lower()
            yield (channel, param, metric_type)


def _callback(metric, param, data):
    if isinstance(metric, Gauge):
        metric.inc()
    if isinstance(metric, Histogram):
        metric.observe(data[param])


def tween_factory(handler, registry):
    def tween(request):
        route_name, route_pattern = get_route_name_and_pattern(request)

        # set callbacks to monitor cubicweb activity
        callbacks = {}
        for (channel, param), metric in CW_METRICS.items():
            _cb = callbacks[(channel, param)] = partial(_callback, metric, param)
            subscribe_to_debug_channel(channel, _cb)

        # monitoring pyramid request
        if "current_requests" in PD_METRICS:
            PD_METRICS["current_requests"].labels(
                method=request.method,
                path_info_pattern=route_pattern,
                route_name=route_name,
            ).inc()

        start = time()
        status = "500"
        try:
            # handle request
            response = handler(request)
            status = str(response.status_int)
            return response
        finally:
            # finish monitoring the request
            duration = time() - start
            if "count_routes" in PD_METRICS:
                PD_METRICS["count_routes"].labels(route_name).inc()
            if "time_routes" in PD_METRICS:
                PD_METRICS["time_routes"].labels(route_name).inc(duration)
            if "slow_routes" in PD_METRICS and duration > SLOW_REQUEST_THRESHOLD:
                PD_METRICS["slow_routes"].labels(route_name).inc()
            if "http_requests" in PD_METRICS:
                PD_METRICS["http_requests"].labels(
                    method=request.method,
                    path_info_pattern=request.cw_request.path,
                    route_name=route_name,
                    status=status,
                ).observe(duration)
            if "current_requests" in PD_METRICS:
                PD_METRICS["current_requests"].labels(
                    method=request.method,
                    path_info_pattern=route_pattern,
                    route_name=route_name,
                ).dec()
            # unsubscribe callbacks
            for (channel, param), callback in callbacks.items():
                unsubscribe_to_debug_channel(channel, callback)

    return tween


def includeme(config):
    settings = config.registry.settings

    # create pyramid metrics
    active_metrics = set(prometheus_pyramid_settings(settings))
    if "http_requests" in active_metrics:
        PD_METRICS["http_requests"] = Histogram(
            "pyramid_request",
            "HTTP Requests",
            ["method", "status", "path_info_pattern", "route_name"],
        )
    if "current_requests" in active_metrics:
        PD_METRICS["current_requests"] = Gauge(
            "pyramid_request_ingress",
            "Number of requests currrently processed",
            ["method", "path_info_pattern", "route_name"],
        )
    if "slow_routes" in active_metrics:
        PD_METRICS["slow_routes"] = Counter(
            "pyramid_route_slow_count", "Slow HTTP requests by route", ["route"]
        )
    if "time_routes" in active_metrics:
        PD_METRICS["time_routes"] = Counter(
            "pyramid_route_sum",
            "Sum of time spent processing requests by route",
            ["route"],
        )
    if "count_routes" in active_metrics:
        PD_METRICS["count_routes"] = Counter(
            "pyramid_route_count", "Number of requests by route", ["route"]
        )

    # create cubicweb metrics
    for channel, param, metric_type in prometheus_cw_settings(settings):
        if (channel, param) not in CW_METRICS:
            CW_METRICS[(channel, param)] = METRIC_TYPE[metric_type](
                f"{channel}_{param}", f"Description of {channel}-{param}"
            )

    # route /metrics
    metrics_path_info = config.registry.settings.get(
        "prometheus.metrics_path_info", "/metrics"
    )
    config.add_route("prometheus_metric", metrics_path_info)
    config.add_view(
        get_metrics, route_name="prometheus_metric", permission=NO_PERMISSION_REQUIRED
    )

    # add this tween
    config.add_tween("cubicweb_prometheus.views.tween_factory", over=EXCVIEW)
