# -*- coding: utf-8 -*-

"""
Created on Sun Aug 22 14:18:29 2021

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

class ClientError(Enum):

    """

    HTTP Client Errors (4xx)

    """

    BAD_REQUEST = ("Bad Request", 400)
    UNAUTHORIZED = ("Unauthorized", 401)
    PAYMENT_REQUIRED = ("Payment Required", 402)
    FORBIDDEN = ("Forbidden", 403)
    NOT_FOUND = ("Not Found", 404)
    METHOD_NOT_ALLOWED = ("Method Not Allowed", 405),
    NOT_ACCEPTABLE = ("Not Acceptable", 406),
    PROXY_AUTHENTICATION_REQUIRED = ("Proxy Authentication Required", 407),
    REQUEST_TIMEOUT = ("Request Timeout", 408),
    CONFLICT = ("Conflict", 409)