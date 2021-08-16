import functools
import threading

import pika
from pika.exchange_type import ExchangeType

from aide_sdk.logger.logger import LogManager
from aide_sdk.messaging.config import QueueConfiguration

logger = LogManager._get_audit_logger()


class ModelPublisher(threading.Thread):
    def __init__(self, queue_config: QueueConfiguration):
        super().__init__()
        self.queue_config = queue_config
        self._connection = None
        self._channel = None
        self._stopping = False

    def connect(self):
        """This method connects to RabbitMQ, returning the connection handle.
        When the connection is established, the on_connection_open method
        will be invoked by pika.
        :rtype: pika.SelectConnection
        """
        logger.info('Connecting to %s', self.queue_config.host)

        credentials = pika.PlainCredentials(
            username=self.queue_config.username,
            password=self.queue_config.password)

        connection_params = pika.ConnectionParameters(
            host=self.queue_config.host,
            port=self.queue_config.port,
            credentials=credentials)

        return pika.SelectConnection(
            parameters=connection_params,
            on_open_callback=self._on_connection_open,
            on_open_error_callback=self._on_connection_open_error,
            on_close_callback=self._on_connection_closed)

    def _on_connection_open(self, _unused_connection):
        """This method is called by pika once the connection to RabbitMQ has
        been established. It passes the handle to the connection object in
        case we need it, but in this case, we'll just mark it unused.
        :param pika.SelectConnection _unused_connection: The connection
        """
        logger.info('Connection opened')
        self.open_channel()

    def _on_connection_open_error(self, _unused_connection, err):
        """This method is called by pika if the connection to RabbitMQ
        can't be established.
        :param pika.SelectConnection _unused_connection: The connection
        :param Exception err: The error
        """
        logger.error('Connection open failed, reopening in 5 seconds: %s', err)
        self._connection.ioloop.call_later(5, self._connection.ioloop.stop)

    def _on_connection_closed(self, _unused_connection, reason):
        """This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.
        :param pika.connection.Connection connection: The closed connection obj
        :param Exception reason: exception representing reason for loss of
            connection.
        """
        self._channel = None
        if self._stopping:
            self._connection.ioloop.stop()
        else:
            logger.warning('Connection closed, reopening in 5 seconds: %s',
                           reason)
            self._connection.ioloop.call_later(5, self._connection.ioloop.stop)

    def open_channel(self):
        """This method will open a new channel with RabbitMQ by issuing the
        Channel.Open RPC command. When RabbitMQ confirms the channel is open
        by sending the Channel.OpenOK RPC reply, the on_channel_open method
        will be invoked.
        """
        logger.info('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        """This method is invoked by pika when the channel has been opened.
        The channel object is passed in so we can make use of it.
        Since the channel is now open, we'll declare the exchange to use.
        :param pika.channel.Channel channel: The channel object
        """
        logger.info('Channel opened')
        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange(self.queue_config.output_exchange)

    def add_on_channel_close_callback(self):
        """This method tells pika to call the on_channel_closed method if
        RabbitMQ unexpectedly closes the channel.
        """
        logger.info('Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reason):
        """Invoked by pika when RabbitMQ unexpectedly closes the channel.
        Channels are usually closed if you attempt to do something that
        violates the protocol, such as re-declare an exchange or queue with
        different parameters. In this case, we'll close the connection
        to shutdown the object.
        :param pika.channel.Channel channel: The closed channel
        :param Exception reason: why the channel was closed
        """
        logger.warning('Channel %i was closed: %s', channel, reason)
        self._channel = None
        if not self._stopping:
            self._connection.close()

    def setup_exchange(self, exchange_name):
        """Setup the exchange on RabbitMQ by invoking the Exchange.Declare RPC
        command. When it is complete, the on_exchange_declareok method will
        be invoked by pika.
        :param str|unicode exchange_name: The name of the exchange to declare
        """
        logger.info('Declaring exchange %s', exchange_name)
        cb = functools.partial(
            self.on_exchange_declareok, userdata=exchange_name)
        self._channel.exchange_declare(
            exchange=exchange_name,
            durable=True,
            exchange_type=ExchangeType.direct,
            callback=cb)

    def on_exchange_declareok(self, _unused_frame, userdata):
        """Invoked by pika when RabbitMQ has finished the Exchange.Declare RPC
        command.
        :param pika.Frame.Method unused_frame: Exchange.DeclareOk
        response frame
        :param str|unicode userdata: Extra user data (exchange name)
        """
        logger.info('Exchange declared: %s', userdata)
        self.setup_queue(self.queue_config.queue)

    def setup_queue(self, queue_name):
        """Setup the queue on RabbitMQ by invoking the Queue.Declare RPC
        command. When it is complete, the on_queue_declareok method will
        be invoked by pika.
        :param str|unicode queue_name: The name of the queue to declare.
        """
        logger.info('Declaring queue %s', queue_name)
        self._channel.queue_declare(queue=queue_name, durable=True,
                                    arguments={"x-queue-type": "quorum"},
                                    callback=self.on_queue_declareok)

    def on_queue_declareok(self, _unused_frame):
        """Method invoked by pika when the Queue.Declare RPC call made in
        setup_queue has completed. In this method we will bind the queue
        and exchange together with the routing key by issuing the Queue.Bind
        RPC command. When this command is complete, the on_bindok method will
        be invoked by pika.
        :param pika.frame.Method method_frame: The Queue.DeclareOk frame
        """
        logger.info('Binding %s to %s', self.queue_config.output_exchange,
                    self.queue_config.queue)
        self._channel.queue_bind(
            self.queue_config.queue,
            self.queue_config.output_exchange,
            routing_key=self.queue_config.output_routing_key,
            callback=self.on_bindok)

    def on_bindok(self, _unused_frame):
        """This method is invoked by pika when it receives the Queue.BindOk
        response from RabbitMQ. Since we know we're now setup and bound, it's
        time to start publishing."""
        logger.info('Queue bound')

    def _publish_message(self, message, correlation_id: str):
        if self._channel is None or not self._channel.is_open:
            logger.error('Could not publish message. '
                         'Channel closed. collaboration_id %s', correlation_id)
            return

        properties = pika.BasicProperties(content_type='application/json')

        self._channel.basic_publish(self.queue_config.output_exchange,
                                    self.queue_config.output_routing_key,
                                    message,
                                    properties)

        logger.info('Published message %s, collaboration_id %s', message, correlation_id)

    def publish_message(self, message, correlation_id: str):
        logger.info('Scheduled message for publishing: %s, collaboration_id %s',
                    message, correlation_id)
        cb = functools.partial(self._publish_message, message, correlation_id)
        self._connection.ioloop.add_callback_threadsafe(cb)

    def run(self):
        while not self._stopping:
            self._connection = None

            try:
                self._connection = self.connect()
                self._connection.ioloop.start()
            except KeyboardInterrupt:
                self.stop()
                if self._connection is not None and not self._connection.is_closed:
                    self._connection.ioloop.start()

        logger.info('Stopped')

    def stop(self):
        logger.info('Stopping')
        self._stopping = True
        self.close_channel()
        self.close_connection()

    def close_channel(self):
        """Invoke this command to close the channel with RabbitMQ by sending
        the Channel.Close RPC command.
        """
        if self._channel is not None:
            logger.info('Closing the channel')
            self._channel.close()

    def close_connection(self):
        """This method closes the connection to RabbitMQ."""
        if self._connection is not None:
            logger.info('Closing connection')
            self._connection.close()
