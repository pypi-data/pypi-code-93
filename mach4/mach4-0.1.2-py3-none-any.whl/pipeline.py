# -*- coding: utf-8 -*-

"""
Created on Tue Jan 19 21:10:49 2021

Copyright 2021 Cyriaque Perier

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


from flask import request, Flask
from .refresh import Refresh
from mach4 import response
from mach4 import security

MACH4_VERSION = "0.1.1-DEV"


class Route:

    """

    Routing rule for a request

    """

    def __init__(self, uri, handler, auth_required, accept_method):

        """

        Initialise object

        """

        self.uri = uri
        self.handler = handler
        self.auth_required = auth_required
        self.accept_method = accept_method


class API:

    """

    Main class of application programming interface

    """

    def __init__(
        self,
        server_name,
        app_version,
        name,
        debug=False,
        default_return=response.error_response,
        users_time_out=1800000,
        keys_time_out=3600000,
        max_user_per_keys=50,
        deep_diag=False,
    ):

        """

        Initialise object
        @name must be set as __name__

        """

        self.app_version = app_version
        self.server_name = server_name
        self.wsgi = Flask(name)
        self.debug = debug
        self.deep_diag = False
        self.default_return = default_return
        self.routing = {}
        self.index = security.KeyIndex(
            server_name, max_user_per_keys, keys_time_out, users_time_out, debug
        )

        self.refresh = Refresh()
        self.refresh.add_function(self.index.refresh_keys)
        self.refresh.start()

        self.wsgi.before_request(self.before_request)
        self.wsgi.after_request(self.after_request)

    def add_route(
        self, uri, handler, auth_required=False, accept_method=["GET", "POST"]
    ):

        """

        Add route in the route manager

        """

        self.routing[uri] = Route(uri, handler, auth_required, accept_method)
        self.wsgi.add_url_rule(uri, uri[1:], handler, methods=accept_method)

    def before_request(self):

        """

        Function performed before any requests

        """

        uri = request.path

        if not uri in self.routing:

            return self.default_return(response.Error.NOT_FOUND)

        if not request.method in self.routing[uri].accept_method:
            print(self.routing[uri].accept_method)
            print(request.method)
            return self.default_return(response.Error.METHOD_NOT_ALLOWED)

        if self.routing[uri].auth_required:

            user_id = request.args.get("user")
            jwt = request.cookies.get("jwt")
            xsrf_token = request.headers.get("xsrf-token")

            if not security.check_auth(jwt, xsrf_token, user_id, self.index):

                return self.default_return(response.Error.UNAUTHORIZED)

    def after_request(self, response):

        """

        Function performed after any requests

        """

        response.headers["server"] = "Mach4"

        return response
