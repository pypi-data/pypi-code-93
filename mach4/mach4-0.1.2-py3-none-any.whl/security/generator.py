# -*- coding: utf-8 -*-
"""
Created on Sat Jan 16 18:16:51 2021

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

from uuid import uuid4
import hmac
import hashlib
import base64
import os
import jwt


def hs256_encode(content, key):

    """

    Encode a message with HMAC-SHA256 (RFC2104 compliant) algorithm

    """

    return hmac.digest(bytes.fromhex(key), content.encode(), hashlib.sha256).hex()


def sha256_encode(message):

    """

    Encode a message with SHA256 as base64

    """

    return base64.b64encode(hashlib.sha256(message.encode()).digest()).decode()


def uuid():

    """

    Generate a UUID4 (RFC 4122 compliant) as compressed string

    """

    return str(uuid4()).replace("-", "")


def new_uuid(unavailable):

    """

    Generate a UUID and make sure that he is not already used

    """

    new = uuid()
    while new in unavailable:
        new = uuid()
    return new


def key(lenght):

    """

    Generate a random hex key

    """

    return os.urandom(lenght).hex()


def generate_hs256_jwt(payload, sign_key):

    """

    Generate JsonWebToken encrypted with HMAC-SHA256 key

    """

    return jwt.encode(payload, sign_key, "HS256")


def generate_xsrf_token(issued_at, sign_key, user_id):

    """

    Generate pseudo-random XSRF-Token with HMAC-SHA256 key and compressed UUID4 user identifier

    """

    xsrf_token = {"iat": round(issued_at), "sub": user_id}
    xsrf_token = str(xsrf_token).replace(" ", "")

    return hs256_encode(xsrf_token, sign_key)
