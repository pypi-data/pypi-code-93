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
from mach4.utils import Colors

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

    def __init__(self, server_name, max_user_per_keys, keys_time_out, users_time_out, debug):

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
        self.bug_count = 0
        
        self.refresh_keys()
    
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
        user_count=0,
        call_event=True
    ):

        """

        Add JWT HMAC-SHA256 key into index

        """
        
        key_value = generator.key(1024)
        issued_at = round(time.time() * 1000)

        if key_index is None:
            key_index = generator.new_uuid(self.jwt_keys.keys())
        
        self.jwt_keys[key_index] = Key(key_index, key_value, issued_at, user_count)
        self.debug.log("Security", "{}Created JWT HMAC-SHA256 key {}.".format(Colors.YELLOW, key_index))
        if call_event:
            
            self.call_event(EventType.ADD_JWT_KEY, (key_index, key_value))
        
        return (key_index, key_value)

    def add_xsrf_key(
        self,
        key_index=None,
        user_count=0,
        call_event=True
    ):

        """

        Add XSRF HMAC-SHA256 key into index

        """
        
        key_value=generator.key(1024)
        issued_at=round(time.time() * 1000)

        if key_index is None:
            key_index = generator.new_uuid(self.xsrf_keys.keys())

        self.xsrf_keys[key_index] = Key(key_index, key_value, issued_at, user_count)

        self.debug.log("Security", "{}Created XSRF HMAC-SHA256 key {}.".format(Colors.YELLOW, key_index))
        
        if call_event:
            
            self.call_event(EventType.ADD_XSRF_KEY, (key_index, key_value))
        
        return (key_index, key_value)

    def get_jwt_key(self, key_index):

        """

        Get JWT HMAC-SHA256 signature key from his key_index (compressed uuid4)

        """

        if not key_index in self.jwt_keys:

            return None

        return self.jwt_keys[key_index]

    def get_xsrf_key(self, key_index):

        """

        Get XSRF-Token HMAC-SHA256 signature key from his key_index (compressed uuid4)

        """

        if not key_index in self.xsrf_keys:

            return None

        return self.xsrf_keys[key_index]

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
            jwt_payload, self.get_jwt_key(jwt_key).get_key_value()
        )
        xsrf_token = generator.generate_xsrf_token(
            now, self.get_xsrf_key(xsrf_key).get_key_value(),
            user_id
        )

        return (json_web_token, xsrf_token)

    def refresh_keys(self):

        """

        Delete all outdated keys and refresh Rapid Access dictionnary

        """
        
        # Make sure that there are at least 5 keys available
        
        while len(self.jwt_rapid_access) < 5:

            index = self.add_jwt_key()[0]
            self.jwt_rapid_access.append(index)

        while len(self.xsrf_rapid_access) < 5:

            index = self.add_xsrf_key()[0]
            self.xsrf_rapid_access.append(index)
        
        
        # Removing unavailable keys from available keys list
        
        for jwt_available_key_index in self.jwt_rapid_access.copy():
            
            if self.bug_count == 20:
                
                return True
            
            jwt_available_key = self.get_jwt_key(jwt_available_key_index) # Getting the key's details
            
            if jwt_available_key is None:
                
                self.jwt_rapid_access.remove(jwt_available_key_index) # Removing the unavailable key from available keys list
                
                self.debug.log("Security", Colors.RED + "Removed anonymous JWT key {}.".format(jwt_available_key_index))
            
            elif (round(time.time() * 1000) + self.users_time_out) >= (jwt_available_key.get_issued_at() + self.keys_time_out) or jwt_available_key.get_user_count() >= self.default_max_user_jwt: # Key will be outdated before token expiration or max users number reached
                
                self.jwt_rapid_access.remove(jwt_available_key_index) # Removing the unavailable key from available keys list
                new_jwt_key_index = self.add_jwt_key()[0] # Creating a replacing key
                self.jwt_rapid_access.append(new_jwt_key_index) # Setting the replacing key as available
        
        for xsrf_available_key_index in self.xsrf_rapid_access.copy():
            
            xsrf_available_key = self.get_xsrf_key(xsrf_available_key_index) # Getting the key's details
            
            if xsrf_available_key is None:
                
                self.xsrf_rapid_access.remove(xsrf_available_key_index) # Removing the unavailable key from available keys list
                
                self.debug.log("Security", Colors.RED + "Removed anonymous key {}.".format(xsrf_available_key_index))
            
            elif (round(time.time() * 1000) + self.users_time_out) >= (xsrf_available_key.get_issued_at() + self.keys_time_out) or xsrf_available_key.get_user_count() >= self.default_max_user_xsrf: # Key will be outdated before token expiration or max users number reached
                
                self.xsrf_rapid_access.remove(xsrf_available_key_index) # Removing the unavailable key from available keys list
                new_xsrf_key_index = self.add_xsrf_key()[0] # Creating a replacing key
                self.xsrf_rapid_access.append(new_xsrf_key_index) # Setting the replacing key as available
        
        
        # Deleting outdated keys
        
        for jwt_key_index in self.jwt_keys.copy():
            
            jwt_key = self.jwt_keys[jwt_key_index]
            
            if jwt_key.get_issued_at() + self.keys_time_out <= round(time.time() * 1000):
                
                del self.jwt_keys[jwt_key.key_index]
                
                self.debug.log("Security",  Colors.YELLOW + "Removed outdated JWT HMAC-SHA256 key {}.".format(jwt_key_index))
        
        for xsrf_key_index in self.xsrf_keys.copy():
            
            xsrf_key = self.xsrf_keys[xsrf_key_index]
            
            if xsrf_key.get_issued_at() + self.keys_time_out <= round(time.time() * 1000):
                
                del self.xsrf_keys[xsrf_key.key_index]
                
                self.debug.log("Security", Colors.YELLOW + "Removed outdated XSRF HMAC-SHA256 key {}.".format(xsrf_key_index))
                


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
