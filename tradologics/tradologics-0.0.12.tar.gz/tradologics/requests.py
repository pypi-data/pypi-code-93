#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Tradologics Python SDK
# https://tradologics.com
#
# Copyright 2020-2021 Tradologics, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from .backtest import Backtest
import requests as _requests

_BASE_URL = "https://api.tradologics.com/beta"
_TOKEN = None
_DEFAULT_TIMEOUT = 5
_SOCKET_URL = "tcp://0.0.0.0:3003"

_IS_BACKTEST = False
_BACKTEST = None


def set_token(token):
    global _TOKEN
    _TOKEN = token


def _set_backtest_mode(start, end):
    global _IS_BACKTEST
    global _BACKTEST
    _IS_BACKTEST = True
    _BACKTEST = Backtest(start, end, _SOCKET_URL)


def _set_current_bar_info(info):
    _BACKTEST.set_current_bar_info(info)


def _get_runtime_events():
    return _BACKTEST.get_runtime_events()


def _process_request(method, url, **kwargs):
    global _IS_BACKTEST

    if "://" in url:
        return _requests.request(method, url, **kwargs)

    if "timeout" not in kwargs:
        kwargs["timeout"] = _DEFAULT_TIMEOUT

    if "headers" not in kwargs:
        if not _TOKEN and not _IS_BACKTEST:
            raise Exception("Please use `set_token(...)` first.")
        kwargs["headers"] = {
            "Authorization": "Bearer {token}".format(token=_TOKEN)
        }

    if _IS_BACKTEST:
        return _BACKTEST.call_eroc_method(method, url, **kwargs)
    else:
        url = f"{_BASE_URL}/{url.strip('/')}"
        return _requests.request(method, url, **kwargs)


def request(method, url, **kwargs):
    return _process_request(method, url, **kwargs)


def get(url, **kwargs):
    return _process_request('GET', url, **kwargs)


def post(url, **kwargs):
    return _process_request('POST', url, **kwargs)


def patch(url, **kwargs):
    return _process_request('PATCH', url, **kwargs)


def put(url, **kwargs):
    return _process_request('PUT', url, **kwargs)


def delete(url, **kwargs):
    return _process_request('DELETE', url, **kwargs)


def options(url, **kwargs):
    return _process_request('OPTIONS', url, **kwargs)


def head(url, **kwargs):
    return _process_request('HEAD', url, **kwargs)


class Session(_requests.Session):
    def _process_request(self, method, url, **kwargs):
        return _process_request(method, url, **kwargs)

    def request(self, method, url, **kwargs):
        return self._process_request(method, url, **kwargs)

    def get(self, url, **kwargs):
        return self._process_request('GET', url, **kwargs)

    def post(self, url, **kwargs):
        return self._process_request('POST', url, **kwargs)

    def patch(self, url, **kwargs):
        return self._process_request('PATCH', url, **kwargs)

    def put(self, url, **kwargs):
        return self._process_request('PUT', url, **kwargs)

    def delete(self, url, **kwargs):
        return self._process_request('DELETE', url, **kwargs)

    def options(self, url, **kwargs):
        return self._process_request('OPTIONS', url, **kwargs)

    def head(self, url, **kwargs):
        return self._process_request('HEAD', url, **kwargs)
