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

from flask import Flask as _flask, Response as _response
from datetime import datetime as _datetime


def start(strategy, endpoint="strategy",
          host="0.0.0.0", port=5000, debug=False):
    a = _FlaskAppWrapper(__name__)
    a.add_endpoint(endpoint, handler=strategy)
    a.run(debug=debug, host=host, port=port)


class _EndpointAction(object):

    def __init__(self, action):
        self.action = action
        self.response = _response(status=200, headers={})

    def __call__(self, *args, **kargs):
        try:
            res = self.action(*args, **kargs)
            return res, 200
        except Exception as err:
            msg = 'Error: {}'.format(err)
            print('{}: {}'.format(str(_datetime.now()).split('.')[0], msg))
            return msg, 500


class _FlaskAppWrapper(object):
    app = None

    def __init__(self, name):
        self.name = name
        self.app = _flask(name)

    def run(self, host, port, debug):
        self.app.run(host, port, debug)

    def add_endpoint(self, endpoint=None, handler=None):
        self.app.add_url_rule(
            endpoint, "strategy", _EndpointAction(handler), methods=["POST"])
