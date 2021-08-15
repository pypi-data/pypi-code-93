from http import HTTPStatus
import logging
import ssl

import aiohttp
import certifi
import orjson
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from .errors import AporiaError
from .logging_utils import LOGGER_NAME
from .utils import orjson_serialize_default_handler

logger = logging.getLogger(LOGGER_NAME)


QUERY_MAX_ATTEMPTS = 4
QUERY_TIMEOUT = 10
QUERY_RETRY_INITIAL_SLEEP = 2
DEFAULT_TIMEOUT_SEC = 30
HTTP_502_VERBOSE_ERROR = """The server couldn't handle the rate at which you are sending requests.
Please try one of the following solutions:
    * Reduce the amount of log_* calls per second
    * Upgrade your cluster so it can support a higher load.
"""


class GraphQLClient:
    """Asynchronous graphql client."""

    def __init__(self, token: str, host: str, port: int):
        """Initialize a GraphQLClient instance.

        Args:
            token (str): Authorization token
            host (str): Aporia server address
            port (int): Aporia server port
        """
        logger.debug("Initializing GraphQL client.")
        if not host.startswith("http"):
            host = "https://{}".format(host)

        self.request_url = "{}:{}/v1/controller/graphql".format(host, port)
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())

        self.headers = {
            "Authorization": "Bearer {}".format(token),
            "Content-Type": "application/json",
        }
        self.session = None

    async def open(self):
        """Opens the HTTP session."""
        logger.debug("Creating HTTP session with Aporia server.")
        self.session = aiohttp.ClientSession(headers=self.headers)

    @retry(
        stop=stop_after_attempt(QUERY_MAX_ATTEMPTS),
        wait=wait_exponential(min=QUERY_RETRY_INITIAL_SLEEP),
        retry=retry_if_exception(lambda err: not isinstance(err, AporiaError)),
        reraise=True,
    )
    async def query_with_retries(
        self, query: str, variables: dict, timeout: int = DEFAULT_TIMEOUT_SEC
    ) -> dict:
        """Executes a GraphQL query with retries in case of failure.

        Args:
            query (str): GraphQL query string
            variables (dict): Variables for the query
            timeout (int): Timeout for the entire request, in seconds. Defaults to 5 minutes.

        Returns:
            dict: GraphQL query result
        """
        return await self.query(query, variables, timeout)

    async def query(self, query: str, variables: dict, timeout: int = DEFAULT_TIMEOUT_SEC) -> dict:
        """Executes a GraphQL query and returns the result.

        Args:
            query (str): GraphQL query string
            variables (dict): Variables for the query
            timeout (int): Timeout for the entire request, in seconds. Defaults to 5 minutes.

        Returns:
            dict: GraphQL query result
        """
        logger.debug("Sending GraphQL query: {}, variables: {}".format(query, variables))

        data = self._serialize_request(query, variables)
        # Note: By default, aiohttp uses SSL and verifies the certificate in HTTPS requests
        async with self.session.post(  # type: ignore
            url=self.request_url,
            data=data,
            timeout=aiohttp.ClientTimeout(total=timeout),
            ssl=self.ssl_context,
        ) as response:

            if response.status != HTTPStatus.OK:
                if response.status == HTTPStatus.BAD_REQUEST:
                    errors = (await response.json())["errors"]  # type: ignore
                    raise AporiaError(
                        short_message=errors[0]["message"],
                        verbose_message=errors[0].get("extensions", {}).get("verbose_message"),
                    )

                elif response.status == HTTPStatus.UNAUTHORIZED:
                    raise AporiaError("Authentication failed, please check your token.")

                elif response.status == HTTPStatus.NOT_FOUND:
                    raise AporiaError(
                        "Aporia server not found, please check the 'host' and 'token' "
                        "parameters you passed to aporia.init()"
                    )

                elif response.status == HTTPStatus.METHOD_NOT_ALLOWED:
                    raise AporiaError(
                        "Communication with Aporia server failed, please check your token."
                    )

                elif response.status == HTTPStatus.BAD_GATEWAY:
                    raise AporiaError(
                        short_message="HTTP Gateway received invalid response from server",
                        verbose_message=HTTP_502_VERBOSE_ERROR,
                    )
                else:
                    raise AporiaError("Unexpected HTTP error {}".format(response.status))

            return (await response.json())["data"]  # type: ignore

    @staticmethod
    def _serialize_request(query: str, variables: dict) -> bytes:
        request = {"query": query, "variables": variables}
        try:
            if hasattr(orjson, "OPT_SERIALIZE_NUMPY"):
                data = orjson.dumps(
                    request,
                    option=orjson.OPT_SERIALIZE_NUMPY,  # type: ignore
                    default=orjson_serialize_default_handler,
                )
            else:
                data = orjson.dumps(request, default=orjson_serialize_default_handler)

            return data
        except TypeError as err:
            raise AporiaError(str(err))

    async def close(self):
        """Closes the http session."""
        await self.session.close()
