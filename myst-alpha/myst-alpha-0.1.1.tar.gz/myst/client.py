from typing import Any, Dict, Optional, Type, TypeVar

import httpx

from myst.auth.credentials import Credentials
from myst.models.base_model import BaseModel
from myst.models.exceptions import MystAPIError, MystClientError, UnauthenticatedError
from myst.models.http_errors import ValidationError
from myst.version import get_package_version

RequestModelType = TypeVar("RequestModelType", bound=BaseModel)
ResponseModelType = TypeVar("ResponseModelType", bound=BaseModel)


class Client:
    """HTTP client for interacting with the Myst API."""

    API_HOST = "https://api.myst.ai"
    API_VERSION = "v1alpha2"

    USER_AGENT_PREFORMAT = "Myst/{api_version} PythonBindings/{package_version}"

    # Increase default timeout, since it's insufficient for some longer inserts/retrievals.
    API_TIMEOUT_SEC = 30

    def __init__(
        self,
        credentials: Optional[Credentials] = None,
        timeout: int = API_TIMEOUT_SEC,
        api_host: str = API_HOST,
    ):
        """A wrapper object providing convenient API access with credentials."""
        # Construct an httpx client so that we can reuse a single TCP connection and configuration.
        self._client = httpx.Client(
            timeout=timeout, headers={"User-Agent": self.user_agent}, base_url=f"{api_host}/{self.API_VERSION}"
        )
        self._credentials = credentials

    def __del__(self) -> None:
        """Cleans up underlying client resources."""
        try:
            self._client.close()
        except Exception:
            # We aren't too concerned with issues that occur while cleaning up connections.
            pass

    def authenticate(self, credentials: Credentials) -> None:
        """Authenticates this client using the given credentials."""
        self._credentials = credentials

    @property
    def user_agent(self) -> str:
        """Gets the `User-Agent` header string to send to the Myst API."""
        # Infer Myst API version and Myst Python client library version for current active versions.
        return self.USER_AGENT_PREFORMAT.format(api_version=self.API_VERSION, package_version=get_package_version())

    def _get_credentials(self) -> Credentials:
        if self._credentials is None:
            raise UnauthenticatedError("No client credentials provided.")

        return self._credentials

    def request(
        self,
        method: str,
        path: str,
        response_class: Type[ResponseModelType],
        params: Optional[Dict[str, Any]] = None,
        request_model: Optional[RequestModelType] = None,
    ) -> ResponseModelType:
        """Executes a request for the given HTTP method and URL, handling JSON serialization and deserialization.

        Args:
            method: HTTP verb to execute, e.g. "GET", "POST", etc.
            path: path relative to the base URL, e.g. "/time_series/"
            response_class: name of the model class to parse the response content into
            params: HTTP query parameters
            request_model: JSON-able model instance to pass in request body

        Raises:
            MystClientError: client error (HTTP 4xx), including further details in the case of 422
            MystAPIError: server error (HTTP 500)

        Returns:
            parsed and validated instance of indicated response class
        """
        # Convert the Pydantic request model into JSON form.
        content = request_model.json() if request_model else None

        # Make the API request.
        response = self._client.request(
            method=method,
            url=path,
            params=params,
            headers={"content-type": "application/json", "Authorization": f"Bearer {self._get_credentials().token}"},
            content=content,
        )

        # Handle the httpx response.
        if response.status_code in (200, 201):
            return response_class.parse_raw(response.content)
        elif response.status_code == 422:
            # Special-case 422 validation errors.
            raise MystClientError(ValidationError.parse_raw(response.content))
        elif 400 <= response.status_code < 500:
            # All other client errors.
            raise MystClientError(response)
        elif response.status_code == 500:
            raise MystAPIError(status_code=response.status_code, message="Internal server error")
        else:
            raise NotImplementedError()
