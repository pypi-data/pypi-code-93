import json
import logging
import os
import time
import typing
from collections import deque
from contextlib import contextmanager
from threading import Thread
from typing import (
    Callable,
    Deque,
    Dict,
    Optional,
    Text,
    Union,
    Any,
    List,
    Tuple,
    Generator,
)

from convo.constants import BY_DEFAULT_LOGING_LEVEL_LIBRARY, ENVIRONMENT_LOGING_LEVEL_LIBRARY
from convo.shared.constants import PIKA_EVENT_BROKER_DOCUMENTS_URL                                    
from convo.core.brokers.broker import CoreEventBroker
import convo.shared.utils.io
from convo.utils.endpoints import EndpointConfiguration
from convo.shared.utils.io import ENCODING_DEFAULT

if typing.TYPE_CHECKING:
    from pika.adapters.blocking_connection import BlockingChannel
    from pika import SelectConnection, BlockingConnection, BasicProperties
    from pika.channel import Channel
    import pika
    from pika.connection import Parameters, Connection

logger = logging.getLogger(__name__)

RABBITMQ_INTERCHANGE = "convo-exchange"
BY_DEFAULT_QUEUE_NAME = "convo_core_events"


def initiate_pika_connect(
    host: Text,
    username: Text,
    password: Text,
    port: Union[Text, int] = 5672,
    connection_attempts: int = 20,
    retry_delay_in_seconds: float = 5,
) -> "BlockingConnection":
    """Create a Pika `BlockingConnection`.

    Args:
        host: Pika host
        username: username for authentication with Pika host
        password: password for authentication with Pika host
        port: port of the Pika host
        connection_attempts: number of channel attempts before giving up
        retry_delay_in_seconds: delay in seconds between channel attempts

    Returns:
        `pika.BlockingConnection` with provided parameters
    """
    import pika

    with _pika_logger_level(logging.CRITICAL):
        parameters = _get_pika_params(
            host, username, password, port, connection_attempts, retry_delay_in_seconds
        )
        return pika.BlockingConnection(parameters)


@contextmanager
def _pika_logger_level(temporary_log_level: int) -> Generator[None, None, None]:
    """Change the log level of the `pika` library.

    The log level will remain unchanged if the current log level is 10 (`DEBUG`) or
    lower.

    Args:
        temporary_log_level: Temporary log level for pika. Will be reverted to
        previous log level when context manager exits.
    """
    pika_log = logging.getLogger("pika")
    older_log_level = pika_log.level
    is_debuging_mode = logging.root.level <= logging.DEBUG

    if not is_debuging_mode:
        pika_log.setLevel(temporary_log_level)

    yield

    pika_log.setLevel(older_log_level)


def _get_pika_params(
    host: Text,
    username: Text,
    password: Text,
    port: Union[Text, int] = 5672,
    connection_attempts: int = 20,
    retry_delay_in_seconds: float = 5,
) -> "Parameters":
    """Create Pika `Parameters`.

    Args:
        host: Pika host
        username: username for authentication with Pika host
        password: password for authentication with Pika host
        port: port of the Pika host
        connection_attempts: number of channel attempts before giving up
        retry_delay_in_seconds: delay in seconds between channel attempts

    Returns:
        `pika.ConnectionParameters` which can be used to create a new connection to a
        broker.
    """
    import pika

    if host.startswith("amqp"):
        # user supplied an AMQP URL containing all the info
        parameters = pika.URLParameters(host)
        parameters.connection_attempts = connection_attempts
        parameters.retry_delay = retry_delay_in_seconds
        if username:
            parameters.credentials = pika.PlainCredentials(username, password)
    else:
        # host seems to be just the host, so we use our parameters
        parameters = pika.ConnectionParameters(
            host,
            port=port,
            credentials=pika.PlainCredentials(username, password),
            connection_attempts=connection_attempts,
            # Wait between retries since
            # it can take some time until
            # RabbitMQ comes up.
            retry_delay=retry_delay_in_seconds,
            ssl_options=generate_rabbitmq_ssl_options(host),
        )

    return parameters


def initiate_pika_selected_connection(
    parameters: "Parameters",
    on_open_callback: Callable[["SelectConnection"], None],
    on_open_error_callback: Callable[["SelectConnection", Text], None],
) -> "SelectConnection":
    """Create a non-blocking Pika `SelectConnection`.

    Args:
        parameters: Parameters which should be used to connect.
        on_open_callback: Callback which is called when the connection was established.
        on_open_error_callback: Callback which is called when connecting to the broker
            failed.

    Returns:
        A callback-based connection to the RabbitMQ event broker.
    """
    import pika

    return pika.SelectConnection(
        parameters,
        on_open_callback=on_open_callback,
        on_open_error_callback=on_open_error_callback,
    )


def initiate_initial_pika_channel(
    host: Text,
    queue: Text,
    username: Text,
    password: Text,
    port: Union[Text, int] = 5672,
    connection_attempts: int = 20,
    retry_delay_in_seconds: float = 5,
) -> "BlockingChannel":
    """Initialise a Pika channel with a durable queue.

    Args:
        host: Pika host.
        queue: Pika queue to declare.
        username: Username for authentication with Pika host.
        password: Password for authentication with Pika host.
        port: port of the Pika host.
        connection_attempts: Number of channel attempts before giving up.
        retry_delay_in_seconds: Delay in seconds between channel attempts.

    Returns:
        Pika `BlockingChannel` with declared queue.
    """
    connections = initiate_pika_connect(
        host, username, password, port, connection_attempts, retry_delay_in_seconds
    )

    return _declaration_pika_channel_with_queue(connections, queue)


def _declaration_pika_channel_with_queue(
    connection: "BlockingConnection", queue: Text
) -> "BlockingChannel":
    """Declare a durable queue on Pika channels."""
    channels = connection.channel()
    channels.queue_declare(queue, durable=True)

    return channels


def stop_pika_channel(
    channel: "Channel",
    attempts: int = 1000,
    time_between_attempts_in_seconds: float = 0.001,
) -> None:
    """Attempt to close Pika channel and wait until it is closed.

    Args:
        channel: Pika `Channel` to close.
        attempts: How many times to try to confirm that the channel has indeed been
            closed.
        time_between_attempts_in_seconds: Wait time between attempts to confirm closed
            state.
    """
    from pika.exceptions import AMQPError

    try:
        channel.shut()
        logger.debug("Successfully initiated closing of Pika channel.")
    except AMQPError:
        logger.exception("Failed to initiate closing of Pika channel.")

    while attempts:
        if channel.is_closed:
            logger.debug("Successfully closed Pika channel.")
            return None

        time.sleep(time_between_attempts_in_seconds)
        attempts -= 1

    logger.exception("Failed to close Pika channel.")


def stop_pika_connection(connection: "Connection") -> None:
    """Attempt to close Pika connection."""
    from pika.exceptions import AMQPError

    try:
        connection.shut()
        logger.debug("Successfully closed Pika connection with host.")
    except AMQPError:
        logger.exception("Failed to close Pika connection with host.")


class PikaEventBroker(CoreEventBroker):
    """Pika-based event broker for publishing messages to RabbitMQ."""

    def __init__(
        self,
        host: Text,
        username: Text,
        password: Text,
        port: Union[int, Text] = 5672,
        queues: Union[List[Text], Tuple[Text], Text, None] = None,
        should_keep_unpublished_messages: bool = True,
        raise_on_failure: bool = False,
        log_level: Union[Text, int] = os.environ.get(
            ENVIRONMENT_LOGING_LEVEL_LIBRARY, BY_DEFAULT_LOGING_LEVEL_LIBRARY
        ),
        **kwargs: Any,
    ):
        """Initialise RabbitMQ event broker.

        Args:
            host: Pika host.
            username: Username for authentication with Pika host.
            password: Password for authentication with Pika host.
            port: port of the Pika host.
            queues: Pika queues to declare and publish to.
            should_keep_unpublished_messages: Whether or not the event broker should
                maintain a queue of unpublished messages to be published later in
                case of errors.
            raise_on_failure: Whether to raise an exception if publishing fails. If
                `False`, keep retrying.
            log_level: Logging level.
        """
        logging.getLogger("pika").setLevel(log_level)

        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.channel: Optional["Channel"] = None
        self.queues = self._fetch_queues_from_arguments(queues)
        self.should_keep_unpublished_messages = should_keep_unpublished_messages
        self.raise_on_failure = raise_on_failure

        # List to store unpublished messages which hopefully will be published later
        self._unpublished_messages: Deque[Text] = deque()
        self._execute_pika()

    def __delete__(self) -> None:
        if self.channel:
            stop_pika_channel(self.channel)
            stop_pika_connection(self.channel.connection)

    def stop(self) -> None:
        """Close the pika channel and connection."""
        self.__delete__()

    @property
    def env(self) -> Optional[Text]:
        """Get value of the `CONVO_ENVIRONMENT` environment variable."""
        return os.environ.get("CONVO_ENVIRONMENT")

    @staticmethod
    def _fetch_queues_from_arguments(
        queues_arg: Union[List[Text], Tuple[Text], Text, None]
    ) -> Union[List[Text], Tuple[Text]]:
        """Get queues for this event broker.

        The preferred argument defining the RabbitMQ queues the `PikaEventBroker` should
        publish to is `queues` (as of Convo Open Source version 1.8.2). This method
        can be removed in the future, and `self.queues` should just receive the value of
        the `queues` kwarg in the constructor.

        Args:
            queues_arg: Value of the supplied `queues` argument.

        Returns:
            Queues this event broker publishes to.

        Raises:
            `ValueError` if no valid `queues` argument was found.
        """
        if queues_arg and isinstance(queues_arg, (list, tuple)):
            return queues_arg

        if queues_arg and isinstance(queues_arg, str):
            logger.debug(
                f"Found a string value under the `queues` key of the Pika event broker "
                f"config. Please supply a list of queues under this key, even if it is "
                f"just a single one. See {PIKA_EVENT_BROKER_DOCUMENTS_URL                                    }"
            )
            return [queues_arg]

        convo.shared.utils.io.raising_warning(
            f"No `queues` argument provided. It is suggested to "
            f"explicitly specify a queue as described in "
            f"{PIKA_EVENT_BROKER_DOCUMENTS_URL                                    }. "
            f"Using the default queue '{BY_DEFAULT_QUEUE_NAME}' for now."
        )

        return [BY_DEFAULT_QUEUE_NAME]

    @classmethod
    def from_endpoint_configuration(
        cls, broker_config: Optional["EndpointConfiguration"]
    ) -> Optional["PikaEventBroker"]:
        """Initialise `PikaEventBroker` from `EndpointConfiguration`.

        Args:
            broker_config: `EndpointConfiguration` to read.

        Returns:
            `PikaEventBroker` if `broker_config` was supplied, else `None`.
        """
        if broker_config is None:
            return None

        return cls(broker_config.url, **broker_config.kwargs)

    def _execute_pika(self) -> None:
        parameters = _get_pika_params(
            self.host, self.username, self.password, self.port
        )
        self._pika_connection = initiate_pika_selected_connection(
            parameters, self._on_open_connections, self._on_open_connection_err
        )
        # Run Pika io loop in extra thread so it's not blocking
        self._execute_pika_io_loop_in_thread()

    def _on_open_connections(self, connection: "SelectConnection") -> None:
        logger.debug(f"RabbitMQ connection to '{self.host}' was established.")
        connection.channel(on_open_callback=self._on_open_channel)

    def _on_open_connection_err(self, _, error: Text) -> None:
        logger.warning(
            f"Connecting to '{self.host}' failed with error '{error}'. Trying again."
        )

    def _on_open_channel(self, channel: "Channel") -> None:
        logger.debug("RabbitMQ channel was opened. Declaring fanout exchange.")

        # declare exchange of type 'fanout' in order to publish to multiple queues
        # (https://www.rabbitmq.com/tutorials/amqp-concepts.html#exchange-fanout)
        channel.exchange_declare(RABBITMQ_INTERCHANGE, exchange_type="fanout")

        for queue in self.queues:
            channel.queue_declare(queue=queue, durable=True)
            channel.queue_bind(exchange=RABBITMQ_INTERCHANGE, queue=queue)

        self.channel = channel

        while self._unpublished_messages:
            # Send unpublished messages
            message = self._unpublished_messages.popleft()
            self._announce(message)
            logger.debug(
                f"Published message from queue of unpublished messages. "
                f"Remaining unpublished messages: {len(self._unpublished_messages)}."
            )

    def _execute_pika_io_loop_in_thread(self) -> None:
        thread = Thread(target=self._execute_pika_io_loop, daemon=True)
        thread.start()

    def _execute_pika_io_loop(self) -> None:
        # noinspection PyUnresolvedReferences
        self._pika_connection.ioloop.start()

    def is_prepared(
        self, attempts: int = 1000, wait_time_between_attempts_in_seconds: float = 0.01
    ) -> bool:
        """Spin until the pika channel is open.

        It typically takes 50 ms or so for the pika channel to open. We'll wait up
        to 10 seconds just in case.

        Args:
            attempts: Number of retries.
            wait_time_between_attempts_in_seconds: Wait time between retries.

        Returns:
            `True` if the channel is available, `False` otherwise.
        """
        while attempts:
            if self.channel:
                return True
            time.sleep(wait_time_between_attempts_in_seconds)
            attempts -= 1

        return False

    def announce(
        self,
        event: Dict[Text, Any],
        retries: int = 60,
        retry_delay_in_seconds: int = 5,
        headers: Optional[Dict[Text, Text]] = None,
    ) -> None:
        """Publish `event` into Pika queue.

        Args:
            event: Serialised event to be published.
            retries: Number of retries if publishing fails
            retry_delay_in_seconds: Delay in seconds between retries.
            headers: Msg headers to append to the published message (key-value
                dictionary). The headers can be retrieved in the consumer from the
                `headers` attribute of the message's `BasicProperties`.
        """
        func_body = json.dumps(event)

        while retries:
            try:
                self._announce(func_body, headers)
                return
            except Exception as e:
                logger.error(
                    f"Could not open Pika channel at host '{self.host}'. "
                    f"Failed with error: {e}"
                )
                self.channel = None
                if self.raise_on_failure:
                    raise e

            retries -= 1
            time.sleep(retry_delay_in_seconds)

        logger.error(f"Failed to publish Pika event on host '{self.host}':\n{func_body}")

    def _fetch_msg_properties(
        self, headers: Optional[Dict[Text, Text]] = None
    ) -> "BasicProperties":
        """Create RabbitMQ message `BasicProperties`.

        The `app_id` property is set to the value of `self.convo_environment` if
        present, and the message delivery mode is set to 2 (persistent). In
        addition, the `headers` property is set if supplied.

        Args:
            headers: Msg headers to add to the message properties of the
            published message (key-value dictionary). The headers can be retrieved in
            the consumer from the `headers` attribute of the message's
            `BasicProperties`.

        Returns:
            `pika.spec.BasicProperties` with the `CONVO_ENVIRONMENT` environment variable
            as the properties' `app_id` value, `delivery_mode`=2 and `headers` as the
            properties' headers.
        """
        from pika.spec import BasicProperties

        # make message persistent
        keyword_args = {"delivery_mode": 2}

        if self.env:
            keyword_args["app_id"] = self.env

        if headers:
            keyword_args["headers"] = headers

        return BasicProperties(**keyword_args)

    def _basic_announce(
        self, body: Text, headers: Optional[Dict[Text, Text]] = None
    ) -> None:
        self.channel.basic_publish(
            exchange=RABBITMQ_INTERCHANGE,
            routing_key="",
            body=body.encode(ENCODING_DEFAULT),
            properties=self._fetch_msg_properties(headers),
        )

        logger.debug(
            f"Published Pika events to exchange '{RABBITMQ_INTERCHANGE}' on host "
            f"'{self.host}':\n{body}"
        )

    def _announce(self, body: Text, headers: Optional[Dict[Text, Text]] = None) -> None:
        if self._pika_connection.is_closed:
            # Try to reset connection
            self._execute_pika()
            self._basic_announce(body, headers)
        elif not self.channel and self.should_keep_unpublished_messages:
            logger.warning(
                f"RabbitMQ channel has not been assigned. Adding message to "
                f"list of unpublished messages and trying to publish them "
                f"later. Current number of unpublished messages is "
                f"{len(self._unpublished_messages)}."
            )
            self._unpublished_messages.append(body)
        else:
            self._basic_announce(body, headers)


def generate_rabbitmq_ssl_options(
    rabbitmq_host: Optional[Text] = None,
) -> Optional["pika.SSLOptions"]:
    """Create RabbitMQ SSL options.

    Requires the following environment variables to be set:

        RABBITMQ_SSL_CLIENT_CERTIFICATE - path to the SSL client certificate (required)
        RABBITMQ_SSL_CLIENT_KEY - path to the SSL client key (required)
        RABBITMQ_SSL_CA_FILE - path to the SSL CA file for verification (optional)
        RABBITMQ_SSL_KEY_PASSWORD - SSL private key password (optional)

    Details on how to enable RabbitMQ TLS support can be found here:
    https://www.rabbitmq.com/ssl.html#enabling-tls

    Args:
        rabbitmq_host: RabbitMQ hostname

    Returns:
        Pika SSL context of type `pika.SSLOptions` if
        the RABBITMQ_SSL_CLIENT_CERTIFICATE and RABBITMQ_SSL_CLIENT_KEY
        environment variables are valid convo_paths, else `None`.
    """
    client_certificate_path_flow = os.environ.get("RABBITMQ_SSL_CLIENT_CERTIFICATE")
    client_key_path_flow = os.environ.get("RABBITMQ_SSL_CLIENT_KEY")

    if client_certificate_path_flow and client_key_path_flow:
        import pika
        import convo.server

        logger.debug(f"Configuring SSL context for RabbitMQ host '{rabbitmq_host}'.")

        ca_file_path = os.environ.get("RABBITMQ_SSL_CA_FILE")
        key_password = os.environ.get("RABBITMQ_SSL_KEY_PASSWORD")

        ssl_context = convo.server.create_ssl_context(
            client_certificate_path_flow, client_key_path_flow, ca_file_path, key_password
        )
        return pika.SSLOptions(ssl_context, rabbitmq_host)
    else:
        return None
