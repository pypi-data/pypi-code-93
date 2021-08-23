import logging
import os
from importlib import import_module
from typing import Optional

from flask import Flask
from flask import request

from jsm_user_services.support.auth_jwt import get_bearer_authorization_token
from jsm_user_services.support.local_threading_utils import add_to_local_threading
from jsm_user_services.support.local_threading_utils import remove_from_local_threading
from jsm_user_services.support.string_utils import get_first_value_from_comma_separated_string

logger = logging.getLogger(__name__)

ip_address_meta_key = os.getenv("GUNICORN_IP_ADDRESS_HEADER", "x-original-forwarded-for")


class JsmJwtService:
    def __init__(self, app: Optional[Flask] = None):
        """
        Initialize the JsmJwtService middleware if the flask application (`app`) is given. Otherwise, you'll
        have the option to initialize it later.

        Examples:
        - Initialize as soon as possible:

        ```
        from flask import Flask
        from jsm_user_services.flask.middleware import JsmJwtService

        app = Flask(__name__)
        JsmJwtService(app)
        ```

        - Postpone initialization:

        ```
        from flask import Flask
        from jsm_user_services.flask.middleware import JsmJwtService

        app, middleware = Flask(__name__), JsmJwtService()
        middleware.init_app(app)
        ```
        """

        self.app = app

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        @app.before_request
        def add_infos_to_local_threading():
            add_to_local_threading("authorization_token", self._get_jwt_token_from_request())
            add_to_local_threading("user_ip", self._get_user_ip_from_request())
            add_to_local_threading("user_session_id", self._get_user_session_id_from_request())

        @app.after_request
        def remove_infos_from_local_threading(response: Flask.response_class) -> Flask.response_class:
            remove_from_local_threading("authorization_token")
            remove_from_local_threading("user_ip")
            remove_from_local_threading("user_session_id")
            return response

    @staticmethod
    def _get_jwt_token_from_request() -> Optional[str]:
        """
        Extracts JWT token from a Flask request object.
        """
        authorization_value = request.headers.get("Authorization", "")
        return get_bearer_authorization_token(authorization_value)

    @staticmethod
    def _get_user_ip_from_request() -> Optional[str]:
        """
        Retrieve the user ip that made this request from Flask request object

        When running a service behind Akamai or other CDN solutions, it is expected that this header might contain a string with multiple IPs (comma separated values). In this case, the user's public IP that originated the request is considered to be the first one of this list.
        For reference: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For
        """
        return get_first_value_from_comma_separated_string(request.headers.get(ip_address_meta_key))

    @staticmethod
    def _get_user_session_id_from_request() -> Optional[str]:
        bearer_token = JsmJwtService._get_jwt_token_from_request()
        if not bearer_token:
            return None

        user = import_module("jsm_user_services.services.user")
        return user.get_session_id_from_bearer_token(bearer_token)
