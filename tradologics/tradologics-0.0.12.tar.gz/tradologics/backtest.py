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


from requests import Response
import zmq
import json


class Backtest:

    def __init__(self, start, end, socket_url):
        self.start = start
        self.end = end
        self.current_bar_info = {
            'datetime': None,
            'resolution': None,
        }
        context = zmq.Context()
        self._socket = context.socket(zmq.REQ)
        self._socket.connect(socket_url)
        self._runtime_events = {}

    def call_eroc_method(self, method, endpoint, **kwargs):
        request = {
            'method': method,
            'url': endpoint,
            'data': {},
            'headers': {
                'start': self.start,
                'end': self.end,
                'datetime': self.current_bar_info.get('datetime'),
                'resolution': self.current_bar_info.get('resolution')
            }
        }

        if 'json' in kwargs:
            request['data'] = kwargs["json"]

        self._socket.send_json(request)
        res = self._socket.recv_json()
        status = res.get('status')
        self._runtime_events = res.get('events')
        del res['status']
        del res['events']
        response = Response()
        state = {
            '_content': json.dumps(res).encode('utf-8'),
            'status_code': status,
            'encoding': 'utf-8'
        }
        response.__setstate__(state)
        return response

    def set_current_bar_info(self, info):
        self.current_bar_info = info

    def get_runtime_events(self):
        return self._runtime_events
