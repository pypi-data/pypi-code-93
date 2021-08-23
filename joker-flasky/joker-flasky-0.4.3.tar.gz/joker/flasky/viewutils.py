#!/usr/bin/env python3
# coding: utf-8

import datetime
import decimal
import os.path

import flask
import flask.views
from flask import request
from volkanic.utils import merge_dicts


def respond(*args, **kwargs):
    resp = kwargs
    for arg in args:
        if 'message' not in resp and isinstance(arg, str):
            resp['message'] = arg
            continue
        if 'data' not in resp:
            if isinstance(arg, (dict, int, float, str)):
                resp['data'] = arg
                continue
            if isinstance(arg, (list, tuple, set, frozenset)):
                resp['data'] = list(arg)
                continue
        r = repr(arg)
        msg = f'redundant or invalid argument for respond(): {r}'
        raise TypeError(msg)
    if resp.setdefault('code', 0):
        msg = 'for non-zero code, raise DomainError/TechnicalError instead.'
        raise TypeError(msg)
    return resp


def respond_with_pre_gzipped(content: bytes, content_type=None):
    content_type = content_type or 'text/plain'
    resp = flask.make_response(content)
    resp.headers.set('Content-Type', content_type)
    resp.headers['Content-Encoding'] = 'gzip'
    return resp


def get_request_data(force_json=False):
    if request.method == 'GET':
        return request.args.to_dict()
    if force_json or request.is_json:
        data = request.get_json(force=force_json)
        if not isinstance(data, dict):
            data = {'': data}
    else:
        data = request.form.to_dict()
    return merge_dicts(data, request.args)


class _ReducedViewMixin:
    force_json = False

    def get_request_data(self):
        return get_request_data(self.force_json)


class ReducedView(flask.views.View, _ReducedViewMixin):
    def dispatch_request(self):
        return self.__call__()

    def __call__(self):
        return respond()


class ReducedRestfulView(flask.views.MethodView, _ReducedViewMixin):
    pass


def jsonp(resp, callback):
    return flask.current_app.response_class(
        callback + '(' + flask.json.dumps(resp) + ');\n',
        mimetype='application/javascript'
    )


_datetime_fmt = '%Y-%m-%d %H:%M:%S'


def _json_default(o):
    if isinstance(o, decimal.Decimal):
        return float(o)
    if isinstance(o, datetime.timedelta):
        return o.total_seconds()
    if isinstance(o, datetime.date):
        return o.isoformat()
    if hasattr(o, 'as_json_serializable'):
        return o.as_json_serializable()
    return o


def json_default(o):
    """usage: json.dumps(some_o, default=json_default)"""
    o = _json_default(o)
    if isinstance(o, str):
        return o
    if isinstance(o, datetime.datetime):
        return o.strftime(_datetime_fmt)
    return str(o)


class JSONEncoderPlus(flask.json.JSONEncoder):
    datetime_fmt = _datetime_fmt

    def default(self, o):
        o = _json_default(o)
        if isinstance(o, str):
            return o
        if isinstance(o, datetime.datetime):
            return o.strftime(self.datetime_fmt)
        return super(JSONEncoderPlus, self).default(o)


def infer_mime_type(filename: str, default="text/plain") -> str:
    from joker.flasky.environ import GlobalInterface
    gi = GlobalInterface()
    name, ext = os.path.splitext(filename)
    return gi.mime_types.get(ext or name, default)
