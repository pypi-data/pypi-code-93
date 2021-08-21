# -*- coding: utf-8 -*-
"""
Created on Sat Jan 16 18:48:39 2021

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

import time
import random
import json
import jwt
from mach4.security import generator
from mach4.security.event import EventType

class Key:

    """

    Storage of information such as number of uses or time of creation

    """

    def __init__(self, key_index, key_value, issued_at, user_count):

        """

        Initialise object

        """

        self.key_index = key_index
        self.key_value = key_value
        self.issued_at = issued_at
        self.user_count = user_count

    def get_issued_at(self):

        return self.issued_at

    def get_user_count(self):

        return self.user_count

    def get_key_index(self):

        return self.key_index

    def get_key_value(self):

        return self.key_value

    def add_user(self):

        """

        Declare the association of a user to this key

        """

        self.user_count += 1

    def export(self):

        """

        Export the key as JSON string (does not contain the number of users)

        """

        key = {
            "key_index": self.key_index,
            "key_value": self.key_value,
            "issued_at": self.issued_at,
        }
        return json.dumps(key)


class KeyIndex:

    """

    Encoding keys index

    """

    def __init__(self, server_name, max_user_per_keys, keys_time_out, users_time_out, debug=False):

        """

        Initialise object

        """

        self.token_list = []
        self.jwt_keys = {}
        self.xsrf_keys = {}
        self.jwt_rapid_access = []
        self.xsrf_rapid_access = []
        self.server_name = server_name
        self.default_max_user_jwt = max_user_per_keys
        self.default_max_user_xsrf = max_user_per_keys
        self.keys_time_out = keys_time_out
        self.users_time_out = users_time_out
        self.debug = debug
        self.event = {}
    
    def register_event(self, event_type, event_handler):
        
        """
        
        Register a function to be called back when event happens
        
        """
        
        if not event_type in self.event:
            
            self.event[event_type] = []
        
        self.event[event_type].append(event_handler)
        
    def call_event(self, event_type, event_params):
        
        """
        
        Call back all registered function to a specific event
        
        """
        
        if event_type in self.event:
            
            event_handlers = self.event.values()
            
            for event_handler in event_handlers:
                
                event_handler(event_type, event_params)
    
    def add_jwt_key(
        self,
        key_index=None,
        key_value=generator.key(1024),
        issued_at=round(time.time() * 1000),
        user_count=0,
        call_event=True
    ):

        """

        Add JWT HMAC-SHA256 key into index

        """

        if key_index is None:
            key_index = generator.new_uuid(self.jwt_keys.keys())

        self.jwt_keys[key_index] = Key(key_index, key_value, issued_at, user_count)
        if self.debug:

            print("Created JWT HMAC-SHA256 key " + key_index)
        
        if call_event:
            
            self.call_event(EventType.ADD_JWT_KEY, (key_index, key_value))
        
        return (key_index, key_value)

    def add_xsrf_keys(
        self,
        key_index=None,
        key_value=generator.key(1024),
        issued_at=round(time.time() * 1000),
        user_count=0,
        call_event=True
    ):

        """

        Add XSRF HMAC-SHA256 key into index

        """

        if key_index is None:
            key_index = generator.new_uuid(self.xsrf_keys.keys())

        self.xsrf_keys[key_index] = Key(key_index, key_value, issued_at, user_count)

        if self.debug:

            print("Created XSRF HMAC-SHA256 key " + key_index)
        
        if call_event:
            
            self.call_event(EventType.ADD_XSRF_KEY, (key_index, key_value))
        
        return (key_index, key_value)

    def get_jwt_key(self, key_index):

        """

        Get JWT HMAC-SHA256 signature key from his key_index (compressed uuid4)

        """

        if not key_index in self.jwt_keys:

            return None

        return self.jwt_keys[key_index].key_value

    def get_xsrf_key(self, key_index):

        """

        Get XSRF-Token HMAC-SHA256 signature key from his key_index (compressed uuid4)

        """

        if not key_index in self.xsrf_keys:

            return None

        return self.xsrf_keys[key_index].key_value

    def create_user_auth(
        self, user_id, app_name, not_before=round(time.time() * 1000)
    ):

        """

        Validate a user's authentification with a JWT and a XSRF-Token

        """

        if len(self.jwt_rapid_access) == 0 or len(self.xsrf_rapid_access) == 0:

            self.refresh_keys()

        jwt_key = self.jwt_rapid_access[
            random.randint(0, len(self.jwt_rapid_access) - 1)
        ]
        xsrf_key = self.xsrf_rapid_access[
            random.randint(0, len(self.xsrf_rapid_access) - 1)
        ]

        token_id = generator.new_uuid(self.token_list)
        self.token_list.append(token_id)

        now = round(time.time() * 1000)

        jwt_payload = {}

        jwt_payload["iss"] = self.server_name
        jwt_payload["sub"] = user_id
        jwt_payload["aud"] = app_name
        jwt_payload["exp"] = now + self.users_time_out
        jwt_payload["nbf"] = not_before
        jwt_payload["iat"] = now
        jwt_payload["jti"] = token_id
        jwt_payload["jtk"] = jwt_key
        jwt_payload["dtk"] = xsrf_key

        json_web_token = generator.generate_hs256_jwt(
            jwt_payload, self.get_jwt_key(jwt_key)
        )
        xsrf_token = generator.generate_xsrf_token(
            now, self.get_xsrf_key(xsrf_key), user_id
        )

        return (json_web_token, xsrf_token)

    def refresh_keys(self):

        """

        Delete all outdated keys and refresh Rapid Access dictionnary

        """

        # Make sure that there are at least 5 keys available
        if len(self.jwt_rapid_access) < 5:

            self.add_jwt_key()

        if len(self.xsrf_rapid_access) < 5:

            self.add_xsrf_keys()

        # Definition of work variables
        max_user_jwt = self.default_max_user_jwt
        max_user_xsrf = self.default_max_user_xsrf

        jwt_rapid_access = []
        xsrf_rapid_access = []

        jwt_delete = []
        xsrf_delete = []

        jwt_keys = self.jwt_keys.copy()
        xsrf_keys = self.xsrf_keys.copy()

        for key in jwt_keys.values():

            if key.get_issued_at() + self.keys_time_out < round(time.time() * 1000):

                if key.get_issued_at() + self.keys_time_out < round(time.time() * 1000):
                    # Keep this key longer preventing late attribution error
                    jwt_delete.append(key.get_key_index())

                if key.key_index in jwt_rapid_access:
                    # Set key as unavailable
                    jwt_rapid_access.remove(key.get_key_index())

                if self.debug:

                    print("Removed JWT HMAC-SHA256 key " + key.get_key_index())

            elif (key.get_issued_at() + self.keys_time_out < round(time.time() * 1000) + self.users_time_out) and (key.get_key_index() in jwt_rapid_access):

                jwt_rapid_access.remove(key.get_key_index())

            elif key.get_user_count() < max_user_jwt:

                jwt_rapid_access.append(key.key_index)

        for key in xsrf_keys.values():

            if key.get_issued_at() + self.keys_time_out < round(time.time() * 1000):

                if key.get_issued_at() + self.keys_time_out < round(
                    time.time() * 1000
                ):
                    # Keep this key longer preventing late attribution error
                    xsrf_delete.append(key.get_key_index())

                if key.key_index in xsrf_rapid_access:
                    # Set key as unavailable
                    xsrf_rapid_access.remove(key.get_key_index())

                if self.debug:

                    print("Removed XSRF-Token HMAC-SHA256 key " + key.get_key_index())

            elif key.get_issued_at() + self.keys_time_out < round(time.time() * 1000) + self.users_time_out and key.get_key_index() in xsrf_rapid_access:

                xsrf_rapid_access.remove(key.get_key_index())

            elif key.get_user_count() < max_user_xsrf:

                xsrf_rapid_access.append(key.key_index)

        # Deletion of keys registered as outdated
        for key_index in jwt_delete:

            del jwt_keys[key_index]

        for key_index in xsrf_delete:

            del xsrf_keys[key_index]

        # Updating the keys in the index
        self.jwt_rapid_access = jwt_rapid_access
        self.xsrf_rapid_access = xsrf_rapid_access

        self.jwt_keys = jwt_keys
        self.xsrf_keys = xsrf_keys


def check_auth(json_web_token, xsrf_token, user_id, index):

    """

    Check authentification of a user

    """

    try:
        payload = None
        jwt_key = None

        payload = jwt.decode(json_web_token, options={"verify_signature": False})
        jwt_key = index.get_jwt_key(payload.get("jtk"))

        if jwt_key is None or payload is None:

            return False

        if generator.generate_hs256_jwt(payload, jwt_key) != json_web_token:

            return False

        not_before = 0
        expiration = 0

        not_before = int(payload.get("nbf"))
        expiration = int(payload.get("exp"))

        if (
            not_before > round(time.time() * 1000)
            or expiration < round(time.time() * 1000)
            or payload.get("sub") != user_id
        ):

            return False

        # JWT OK

        xsrf_key = index.get_xsrf_key(payload.get("dtk"))

        if (
            generator.generate_xsrf_token(payload.get("iat"), xsrf_key, user_id)
            != xsrf_token
        ):

            return False

        # XSRF TOKEN OK

        return True
    except:
        return False
