# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 18:42:48 2021

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

from enum import Enum
import json
from flask import make_response


class Error(Enum):

    """

    HTTP Errors

    """

    BAD_REQUEST = ("Bad Request", 400)
    UNAUTHORIZED = ("Unauthorized", 401)
    PAYMENT_REQUIRED = ("Payment Required", 402)
    FORBIDDEN = ("Forbidden", 403)
    NOT_FOUND = ("Not Found", 404)
    METHOD_NOT_ALLOWED = ("Method Not Allowed", 405)


def error_response(error):

    """

    Default returned value

    """

    return (json.dumps({"error": error.value[0]}), error.value[1])


def valid_login(api, user_id, app_name=None):

    """

    Authentificate a user

    """

    if app_name is None:

        app_name = api.server_name

    jwt, xsrf_token = api.index.create_user_auth(user_id, app_name)
    login_response = make_response(
        json.dumps({"auth": "success", "user": user_id, "xsrf-token": xsrf_token})
    )
    login_response.set_cookie("jwt", value=jwt, secure=True, httponly=True)

    return login_response


def invalid_login():

    """

    Default response when user authentication fails

    """

    return (
        json.dumps({"error": Error.UNAUTHORIZED.value[0], "auth": "failure"}),
        Error.UNAUTHORIZED.value[1],
    )
