import logging
import os
from typing import Optional

from django.http import HttpRequest

from jsm_user_services.services.user import get_session_id_from_bearer_token
from jsm_user_services.support.auth_jwt import get_bearer_authorization_token
from jsm_user_services.support.http_utils import convert_header_to_meta_key
from jsm_user_services.support.local_threading_utils import add_to_local_threading
from jsm_user_services.support.local_threading_utils import remove_from_local_threading
from jsm_user_services.support.string_utils import get_first_value_from_comma_separated_string

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object

logger = logging.getLogger(__name__)

ip_address_meta_key = convert_header_to_meta_key(os.getenv("GUNICORN_IP_ADDRESS_HEADER", "x-original-forwarded-for"))


class JsmJwtService(MiddlewareMixin):
    def process_request(self, request):
        add_to_local_threading("authorization_token", self._get_jwt_token_from_request(request))
        add_to_local_threading("user_ip", self._get_user_ip_from_request(request))
        add_to_local_threading("user_session_id", self._get_user_session_id_from_request(request))

    def process_response(self, request, response):
        remove_from_local_threading("authorization_token")
        remove_from_local_threading("user_ip")
        return response

    @staticmethod
    def _get_jwt_token_from_request(request: HttpRequest) -> Optional[str]:
        """
        Extracts JWT token from a Django request object.
        """
        authorization_value = request.META.get("HTTP_AUTHORIZATION", "")
        return get_bearer_authorization_token(authorization_value)

    @staticmethod
    def _get_user_ip_from_request(request: HttpRequest) -> Optional[str]:
        """
        Retrieve the user ip that made this request from Django HttpRequest object

        When running a service behind Akamai or other CDN solutions, it is expected that this header might contain a string with multiple IPs (comma separated values). In this case, the user's public IP that originated the request is considered to be the first one of this list.
        For reference: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For
        """
        return get_first_value_from_comma_separated_string(request.META.get(ip_address_meta_key, None))

    @staticmethod
    def _get_user_session_id_from_request(request: HttpRequest) -> Optional[str]:
        bearer_token = JsmJwtService._get_jwt_token_from_request(request)
        if not bearer_token:
            return None
        return get_session_id_from_bearer_token(bearer_token)
