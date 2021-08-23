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
from mach4 import security
from mach4 import utils
from mach4.debug import Debug

MACH4_VERSION = "0.2.0-DEV"


class Route:

    """

    Routing rule for a request

    """

    def __init__(self, uri, handler, auth_required, accept_method, captcha_required, custom_captcha_instance):

        """

        Initialise object

        """

        self.uri = uri
        self.handler = handler
        self.auth_required = auth_required
        self.accept_method = accept_method
        self.captcha_required = captcha_required
        self.custom_captcha_instance = custom_captcha_instance


class API:

    """

    Main class of application programming interface

    """

    def __init__(
        self,
        server_name,
        app_version,
        name,
        default_captcha_instance=None,
        debug=False,
        default_return=utils.error_response,
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
        self.default_captcha_instance = default_captcha_instance
        self.debug = Debug(debug)
        self.deep_diag = False
        self.default_return = default_return
        self.routing = {}
        self.index = security.KeyIndex(
            server_name, max_user_per_keys, keys_time_out, users_time_out, self.debug
        )

        self.refresh = utils.Refresh()
        self.refresh.add_function(self.index.refresh_keys)
        self.refresh.start()

        self.wsgi.before_request(self.before_request)
        self.wsgi.after_request(self.after_request)

    def add_route(
        self, uri, handler, auth_required=False, accept_method=["GET", "POST"], captcha_required=False, custom_captcha_instance=None
    ):

        """

        Add route in the route manager

        """

        self.routing[uri] = Route(uri, handler, auth_required, accept_method, captcha_required, custom_captcha_instance)
        self.wsgi.add_url_rule(uri, uri[1:], handler, methods=accept_method)

    def before_request(self):

        """

        Function performed before any requests

        """

        uri = request.path # Getting request URI

        if not uri in self.routing:

            return self.default_return(utils.ClientError.NOT_FOUND)
        
        
        # Method checking
        
        if not request.method in self.routing[uri].accept_method: # If used method isn't allowed
            
            return self.default_return(utils.ClientError.METHOD_NOT_ALLOWED) # Send HTTP 405 Error
        
        
        # Captcha checking
        
        if self.routing[uri].captcha_required: # If captcha is required for this route
            
            captcha_instance = self.default_captcha_instance # Getting default captcha instance
            
            if not self.routing[uri].custom_captcha_instance is None: # If there is a custom captcha instance for this route
                
                captcha_instance = self.routing[uri].custom_captcha_instance # Getting custom captcha instance
            
            # Storing useful datas
            captcha_response = request.form.get("h-captcha-response")
            remote_ip = request.remote_addr
            
            captcha_validity = captcha_instance.verify(captcha_response, remote_ip=remote_ip) # Dialing with HCaptcha servers
            
            if not captcha_validity:
                
                return self.default_return(utils.ClientError.CONFLICT) # Send HTTP 409 Error
        
        
        # Auth checking
        
        if self.routing[uri].auth_required: # If authentification is required for this route
            
            # Storing useful datas
            user_id = request.args.get("user")
            jwt = request.cookies.get("jwt")
            xsrf_token = request.headers.get("xsrf-token")

            if not security.check_auth(jwt, xsrf_token, user_id, self.index): # If signatures can't be validated

                return self.default_return(utils.ClientError.UNAUTHORIZED) # Send HTTP 401 Error

    def after_request(self, response):

        """

        Function performed after any requests

        """

        response.headers["server"] = "Mach4"

        return response
