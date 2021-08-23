import logging
import os
import time
import traceback
from typing import Any, Callable, Dict

import jwt
from fastapi import Request, Response
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRoute
from fastapi.security.utils import get_authorization_scheme_param
from jwt.jwks_client import PyJWKClient
from starlette.datastructures import FormData

route_logger = logging.getLogger("RouteLogger")
route_logger.addHandler(logging.NullHandler())
route_logger.setLevel(os.environ.get("LOG_LEVEL"))


class LoggedRoute(APIRoute):
    jwks_client = PyJWKClient(os.environ.get("AUTH_JWKS_URL"))
    """A custom implementation of APIRoute class that handles logging of requests.
    Logs include info about request status, method, path, time taken, and also 
    tenant name and external ID for traceability. 

    Args:
        APIRoute (class): fastapi.routing.APIRoute class
    """

    def decode_token(self, token: str) -> Dict[str, Any]:
        """Decode an authentication jwt token

            Args:
                token (str): the encoded token string

            Returns:
                Dict[str, Any]: a decoded token dictionary
            """
        ALGORITHM = os.environ.get("AUTH_ALGORITHM")
        AUDIENCE = os.environ.get("AUTH_AUDIENCE")

        signing_key = self.jwks_client.get_signing_key_from_jwt(token)
        decoded_token = jwt.decode(
            token, signing_key.key, audience=AUDIENCE, algorithms=[ALGORITHM]
        )

        return decoded_token

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            """Custom route handler that logs request information.

            Args:
                request (Request): a FastAPI request

            Raises:
                Exception: If the authentication token cannot be decoded.
                Exception: If the authentication scheme is not bearer token.

            Returns:
                Response: a FastAPI Response
            """

            tenant_name = "N/A"
            external_id = "N/A"

            start_time = time.perf_counter()
            try:
                response: Response = await original_route_handler(request)
                finish_time = time.perf_counter()

                overall_status = "successful" if response.status_code < 400 else "failed"
                status_code = response.status_code
            except Exception as e:
                finish_time = time.perf_counter()

                overall_status = "failed"
                status_code = e.status_code if hasattr(e, "status_code") else 400
                raise
            finally:
                execution_time = finish_time - start_time

                # Obtain the tenant name if they have been authenticated.
                auth_header = request.headers.get("Authorization", None)
                if(auth_header):
                    scheme, param = get_authorization_scheme_param(auth_header)
                    if scheme.lower() != "bearer":
                        raise HTTPException(401,
                                            "Authentication scheme is not using bearer token.")

                    try:
                        decoded_token = self.decode_token(param)
                    except Exception as e:
                        traceback.print_exc()
                        raise HTTPException(status_code=401, detail=repr(e))

                    tenant_name = decoded_token.get('tenantname', tenant_name)

                form: FormData = await request.form()

                if "file" not in form.keys():
                    # Obtain the external ID from the request body if available.
                    if await request.body():
                        body = await request.json()

                        external_id = body.get('ExternalID', external_id)

                route_logger.info(f"Request {overall_status}, {request.method} {request.url.path}, "
                                  f"status code={status_code}, tenant={tenant_name}, "
                                  f"externalID={external_id} took={execution_time:0.4f}s")

            return response

        return custom_route_handler
