import aiohttp
import logging
import os
from aiohttp.client_exceptions import ContentTypeError
from sanic.request import Request
from typing import Any, Optional, Text, Dict

import convo.shared.utils.io
import convo.utils.io
from convo.constants import BY_DEFAULT_REQUEST_TIMEOUT


log = logging.getLogger(__name__)


def read_end_point_configuration(
    filename: Text, endpoint_type: Text
) -> Optional["EndpointConfiguration"]:
    """Read an endpoint configuration file from disk and extract one

    config."""
    if not filename:
        return None

    try:
        matter = convo.shared.utils.io.read_configuration_file(filename)

        if endpoint_type in matter:
            return EndpointConfiguration.from_dict(matter[endpoint_type])
        else:
            return None
    except FileNotFoundError:
        log.error(
            "Failed to read endpoint configuration "
            "from {}. No such file.".format(os.path.abspath(filename))
        )
        return None


def concatenate_url(base: Text, sub_path: Optional[Text]) -> Text:
    """Append a subpath to a base url.

    Strips leading slashes from the subpath if necessary. This behaves
    differently than `urlparse.urljoin` and will not treat the subpath
    as a base url if it starts with `/` but will always append it to the
    `base`.

    Args:
        base: Base URL.
        sub_path: Optional path to append to the base URL.

    Returns:
        Concatenated URL with base and subpath.
    """
    if not sub_path:
        if base.endswith("/"):
            log.debug(
                f"The URL '{base}' has a trailing slash. Please make sure the "
                f"target server supports trailing slashes for this endpoint."
            )
        return base

    uniform_resource_locator = base
    if not base.endswith("/"):
        uniform_resource_locator += "/"
    if sub_path.startswith("/"):
        sub_path = sub_path[1:]
    return uniform_resource_locator + sub_path


class EndpointConfiguration:
    """Configuration for an external HTTP endpoint."""

    def __init__(
        self,
        url: Text = None,
        params: Dict[Text, Any] = None,
        headers: Dict[Text, Any] = None,
        basic_auth: Dict[Text, Text] = None,
        token: Optional[Text] = None,
        token_name: Text = "token",
        **kwargs,
    ):
        self.url = url
        self.params = params if params else {}
        self.headers = headers if headers else {}
        self.basic_auth = basic_auth
        self.token = token
        self.token_name = token_name
        self.type = kwargs.pop("store_type", kwargs.pop("type", None))
        self.kwargs = kwargs

    def endpoint_session(self) -> aiohttp.ClientSession:
        # create authentication parameters
        if self.basic_auth:
            authorize = aiohttp.BasicAuth(
                self.basic_auth["username"], self.basic_auth["password"]
            )
        else:
            authorize = None

        return aiohttp.ClientSession(
            headers=self.headers,
            auth=authorize,
            timeout=aiohttp.ClientTimeout(total=BY_DEFAULT_REQUEST_TIMEOUT),
        )

    def combine_params(
        self, kwargs: Optional[Dict[Text, Any]] = None
    ) -> Dict[Text, Any]:
        # construct GET parameters
        parameters = self.params.copy()

        # set the authentication token if present
        if self.token:
            parameters[self.token_name] = self.token

        if kwargs and "parameters" in kwargs:
            parameters.update(kwargs["parameters"])
            del kwargs["parameters"]
        return parameters

    async def request(
        self,
        method: Text = "post",
        subpath: Optional[Text] = None,
        content_type: Optional[Text] = "application/json",
        **kwargs: Any,
    ) -> Optional[Any]:
        """Send a HTTP request to the endpoint. Return json response, if available.

        All additional arguments will get passed through
        to aiohttp's `session.request`."""

        # create the appropriate headers
        headers = {}
        if content_type:
            headers["Content-Type"] = content_type

        if "headers" in kwargs:
            headers.update(kwargs["headers"])
            del kwargs["headers"]

        uniform_resource_locator = concatenate_url(self.url, subpath)
        async with self.endpoint_session() as session:
            async with session.request(
                method,
                uniform_resource_locator,
                headers=headers,
                params=self.combine_params(kwargs),
                **kwargs,
            ) as response:
                if response.status >= 400:
                    raise ClientResponseError(
                        response.status, response.reason, await response.content.read()
                    )
                try:
                    return await response.json()
                except ContentTypeError:
                    return None

    @classmethod
    def from_dict(cls, data) -> "EndpointConfiguration":
        return EndpointConfiguration(**data)

    def duplication(self) -> "EndpointConfiguration":
        return EndpointConfiguration(
            self.url,
            self.params,
            self.headers,
            self.basic_auth,
            self.token,
            self.token_name,
            **self.kwargs,
        )

    def __eq__(self, others) -> bool:
        if isinstance(self, type(others)):
            return (
                others.url == self.url
                and others.params == self.params
                and others.headers == self.headers
                and others.basic_auth == self.basic_auth
                and others.token == self.token
                and others.token_name == self.token_name
            )
        else:
            return False

    def __ne__(self, others) -> bool:
        return not self.__eq__(others)


class ClientResponseError(aiohttp.ClientError):
    def __init__(self, status: int, message: Text, text: Text) -> None:
        self.status = status
        self.message = message
        self.text = text
        super().__init__(f"{status}, {message}, body='{text}'")


def boolean_argument(request: Request, name: Text, default: bool = True) -> bool:
    """Return a passed boolean argument of the request or a default.

    Checks the `name` parameter of the request if it contains a valid
    boolean value. If not, `default` is returned."""

    return request.args.get(name, str(default)).lower() == "true"


def float_argument(
    request: Request, key: Text, default: Optional[float] = None
) -> Optional[float]:
    """Return a passed argument cast as a float or None.

    Checks the `name` parameter of the request if it contains a valid
    float value. If not, `None` is returned."""

    argument = request.args.get(key, default)

    if argument is default:
        return argument

    try:
        return float(str(argument))
    except (ValueError, TypeError):
        log.warning(f"Failed to convert '{argument}' to float.")
        return default
