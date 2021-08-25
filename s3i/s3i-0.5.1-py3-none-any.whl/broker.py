import sys
import os
import functools
import ssl
import logging
import pika
import pika.exceptions
import abc
import requests
import urllib
import time
import asyncio
from pika.credentials import ExternalCredentials
from s3i.exception import raise_error_from_response, raise_error_from_s3ib_amqp, S3IBrokerRESTError, S3IBrokerAMQPError
from pika.adapters.asyncio_connection import AsyncioConnection

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)


class BrokerMetaClass(metaclass=abc.ABCMeta):
    """
    Meta class for S³I Broker which is not allowed to be instantiated
    """

    @abc.abstractmethod
    def send(self, receiver_endpoints, msg, encrypted=False):
        """
        Sends an S3I-B message

        :param receiver_endpoints: endpoints of the receivers
        :type receiver_endpoints: list of str
        :param msg: message to be sent
        :type msg: str
        :param encrypted: if true, message will be sent encrypted, otherwise not.
        :type encrypted: bool

        """

    @abc.abstractmethod
    def receive_once(self, queue):
        """
        Receive one S3I-B message and do not wait for more messages.

        :param queue: queue which starts a listener in order to receive a single message
        :type queue: str
        """


class BrokerREST(BrokerMetaClass):
    """
    Class Broker REST contains functions to connect to S3I Broker via HTTP REST API, and send and receive messages

    """

    def __init__(self, token, url="https://broker.s3i.vswf.dev/"):
        """
        Constructor

        :param token: Access Token issued from S³I IdentityProvider
        :type token: str
        :param url: url of S³I Broker API
        :type url: str

        """
        self._token = token
        self._url = url
        self.headers = {'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + self.token}
        self.headers_encrypted = {'Content-Type': 'application/pgp-encrypted',
                                  'Authorization': 'Bearer ' + self.token}

    @property
    def token(self):
        """Returns the JWT currently in use.

        :returns: JWT-Token
        :rtype: str

        """
        return self._token

    @token.setter
    def token(self, new_token):
        """Sets the value of the object's token property to new_token.

        :param new_token: JWT
        :type new_token: str
        """
        self._token = new_token

    def send(self, receiver_endpoints, msg, encrypted=False):
        """
        Send a S³I-B message via S³I Broker API
        :param receiver_endpoints: endpoints of the receivers
        :type receiver_endpoints: list of str
        :param msg: message to be sent
        :type msg: str
        :param encrypted: if true, message will be sent encrypted, otherwise not.
        :type encrypted: bool

        """
        end_points_encoded = []
        for receiver_endpoint in receiver_endpoints:
            encoded = urllib.parse.quote(receiver_endpoint, safe="")
            end_points_encoded.append(encoded)

        endpoints = ",".join(end_points_encoded)
        url = "{}{}".format(self._url, endpoints)
        headers = self.headers
        if encrypted:
            headers = self.headers_encrypted
        response = requests.post(url=url, headers=headers, data=msg)
        raise_error_from_response(response, S3IBrokerRESTError, 201)

    def receive_once(self, queue):
        """
        Receive one S3I-B message and do not wait for more messages.

        :param queue: queue which starts a listener in order to receive a single message
        :type queue: str
        :return: received S3I-B message
        """

        queue_encoded = urllib.parse.quote(queue, safe="")
        url = "{}{}".format(self._url, queue_encoded)
        response = requests.get(url=url, headers=self.headers)
        response_json = raise_error_from_response(response, S3IBrokerRESTError, 200)
        return response_json


class Broker(BrokerMetaClass):
    """
    Class Broker contains functions to connect to S3I Broker via AMQP, and send and receive messages, using Pika library

    """
    CONTENT_TYPE = "application/json"
    HOST = "rabbitmq.s3i.vswf.dev"

    def __init__(self, auth_form, content_type=CONTENT_TYPE,
                 username=None, password=None, x509_path=None,
                 host=HOST):
        """
        Constructor
        :param auth_form: method to authentication against Broker. 'Username/Password' and 'X509' are valid
        :param content_type: accepted content type of messages. By default 'application/json'
        :param username: Username used for plain authentication. For OAuth2 can be empty
        :param password: Password used for plain authentication. For OAuth2 must be access token
        :param x509_path: Local path for X509 certificate, if 'X509' is chosen as 'auth_form'
        :param host: Host url of Broker
        """

        self.__auth_form = auth_form
        self.__username = username
        self.__password = password
        self.__content_type = content_type
        self.__x509_path = x509_path
        self.__host = host

        self._queue = None
        self._callback = None

        self.receiver = None
        self.receiver_once = None
        self.publisher = None

        self._reconnect_delay = 0

    def receive(self, queue, callback=None):
        """
        Starts consuming to receive messages with a callback function. You need to acknowledge the message in callback.

        :param queue: endpoint (queue) of receiver defined in S3I Broker,
        :type queue: str
        :param callback: callback function
        """
        self._queue = queue
        self._callback = callback

        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)

        self.receiver = AsyncReceiver(
            connection_parameter=self.build_conn_par(),
            queue=self._queue, callback=self._callback)
        while True:
            try:
                self.receiver.run()
            except KeyboardInterrupt:
                self.receiver.stop()
                break
            self.maybe_reconnect()

    def maybe_reconnect(self, token=None):
        """
        Try to reconnect to the Broker, if the connection is aborted.
        :param token: new token
        :return: None
        """
        self.__password = token
        if self.receiver.should_reconnect:
            self.receiver.stop()
            reconnect_delay = self._get_reconnect_delay()
            LOGGER.info('Reconnecting after %d seconds', reconnect_delay)
            time.sleep(reconnect_delay)
            self.receiver = AsyncReceiver(
                connection_parameter=self.build_conn_par(),
                queue=self._queue, callback=self._callback)

    def _get_reconnect_delay(self):
        """
        Get a delay for reconnection, by default 0 sec.
        :return: reconnect delay
        """
        if self.receiver.was_consuming:
            self._reconnect_delay = 0
        else:
            self._reconnect_delay += 1
        if self._reconnect_delay > 30:
            self._reconnect_delay = 30
        return self._reconnect_delay

    def receive_once(self, queue):
        """
        Receives message once via AMQP

        :param queue: endpoint (queue) of receiver defined in S3I Broker
        :type queue: str
        :return: message body
        :rtype: bytearray
        """
        self.receiver_once = BrokerOnceReceiver(connection_parameter=self.build_conn_par())
        return self.receiver_once.receive_once(queue=queue)

    def send(self, receiver_endpoints, msg, encrypted=False):
        """
        Sends a message via AMQP

        :param receiver_endpoints: endpoints (queues) of receivers
        :type receiver_endpoints: list
        :param msg: message
        :type msg: str
        :param encrypted: whether the message is sent encrypted. TODO
        :type encrypted: bool


        """
        if not isinstance(receiver_endpoints, list):
            raise S3IBrokerAMQPError(error_msg="receiver endpoints must be list")
        self.publisher = BrokerOncePublisher(connection_parameter=self.build_conn_par())
        self.publisher.send(receiver_endpoints, msg)

    def build_conn_par(self):
        """
        Authentication at S3I Broker has two different methods
        X.509: Authentication with X.509 certificate which includes the user information or \n
        Username/Password: the corresponding user must have been registered in S3I Broker. To authenticate with an access token, using Username/Password \n
        :return: connection parameters for the S3I Broker; used in function buildConn(self, connpara)
        :rtype: pika connectionParameters, refer to ConnectionParameters_

        """

        auth_list = ["X509", "Username/Password"]
        try:
            auth_list.index(self.__auth_form)
        except ValueError as e:
            sys.exit("[x] invalid authentication form, please check")
        else:
            if self.__auth_form == "Username/Password":
                credentials = pika.PlainCredentials(
                    username=self.__username, password=self.__password)
                conn_par = pika.ConnectionParameters(
                    host=self.__host, virtual_host='s3i', credentials=credentials)
                return conn_par
            elif self.__auth_form == "X509":
                ca_cer_path = os.path.join(
                    self.__x509_path, "ca_certificate.pem")
                context = ssl.create_default_context(cafile=ca_cer_path)
                client_cer_path = os.path.join(
                    self.__x509_path, "client_certificate.pem")
                client_key_path = os.path.join(
                    self.__x509_path, "client_key.pem")
                context.load_cert_chain(client_cer_path, client_key_path)
                ssl_options = pika.SSLOptions(context, self.__host)
                conn_par = pika.ConnectionParameters(port=5671, host=self.__host, ssl_options=ssl_options,
                                                     virtual_host='s3i', credentials=ExternalCredentials())
                return conn_par


class AsyncReceiver:
    """
    Class contains functions for a asynchronous Broker consumer
    """
    def __init__(self, connection_parameter, queue, callback):
        """
        Constructor

        :param connection_parameter: connection parameter, built via function 'build_conn_par' in Class 'Broker'
        :param queue: message queue
        :param callback: callback function for message receiving
        """
        self._connection_parameter = connection_parameter
        self._connection = None
        self._channel = None

        self._closing = False
        self._consuming = False
        self._consumer_tag = None

        self.should_reconnect = False
        self.was_consuming = False

        self._queue = queue
        self._callback = callback
        self._prefetch_count = 1

    @property
    def connection_parameter(self):
        return self._connection_parameter

    @connection_parameter.setter
    def connection_parameter(self, value):
        self._connection_parameter = value

    @property
    def connection(self):
        return self._connection

    @connection.setter
    def connection(self, value):
        self._connection = value

    @property
    def consuming(self):
        return self._consuming

    @consuming.setter
    def consuming(self, value):
        self._consuming = value

    @property
    def consumer_tag(self):
        return self._consumer_tag

    def connect(self):
        """This method connects to RabbitMQ, returning the connection handle.
        When the connection is established, the on_connection_open method
        will be invoked by pika.
        :rtype: pika.adapters.asyncio_connection.AsyncioConnection
        """
        LOGGER.info('Connecting to S3I Broker Receiver')
        return AsyncioConnection(
            parameters=self.connection_parameter,
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_open_error,
            on_close_callback=self.on_connection_closed)

    def close_connection(self):
        """
        This method disconnects to RabbitMQ
        :return: None
        """
        self._consuming = False
        if self._connection.is_closing or self._connection.is_closed:
            LOGGER.info('Connection is closing or already closed')
        else:
            LOGGER.info('Closing connection')
            self._connection.close()

    def on_connection_open(self, _unused_connection):
        """This method is called by pika once the connection to RabbitMQ has
        been established. It passes the handle to the connection object in
        case we need it, but in this case, we'll just mark it unused.
        :param pika.adapters.asyncio_connection.AsyncioConnection _unused_connection:
           The connection
        """
        LOGGER.info('Connection opened')
        self.open_channel()

    def on_connection_open_error(self, _unused_connection, err):
        """This method is called by pika if the connection to RabbitMQ
        can't be established.
        :param pika.adapters.asyncio_connection.AsyncioConnection _unused_connection:
           The connection
        :param Exception err: The error
        """
        LOGGER.error('Connection open failed: %s', err)
        self.reconnect()

    def on_connection_closed(self, _unused_connection, reason):
        """This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.
        :param pika.connection.Connection connection: The closed connection obj
        :param Exception reason: exception representing reason for loss of
            connection.
        """
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            LOGGER.warning('Connection closed, reconnect necessary: %s', reason)
            self.reconnect()

    def reconnect(self):
        """Will be invoked if the connection can't be opened or is
        closed. Indicates that a reconnect is necessary then stops the
        ioloop.
        """
        self.should_reconnect = True
        self.stop()

    def open_channel(self):
        """Open a new channel with RabbitMQ by issuing the Channel.Open RPC
        command. When RabbitMQ responds that the channel is open, the
        on_channel_open callback will be invoked by pika.
        """
        LOGGER.info('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        """This method is invoked by pika when the channel has been opened.
        The channel object is passed in so we can make use of it.
        Since the channel is now open, we'll declare the exchange to use.
        :param pika.channel.Channel channel: The channel object
        """
        LOGGER.info('Channel opened')
        self._channel = channel
        self.add_on_channel_close_callback()
        self.set_qos()

    def add_on_channel_close_callback(self):
        """This method tells pika to call the on_channel_closed method if
        RabbitMQ unexpectedly closes the channel.
        """
        LOGGER.info('Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reason):
        """Invoked by pika when RabbitMQ unexpectedly closes the channel.
        Channels are usually closed if you attempt to do something that
        violates the protocol, such as re-declare an exchange or queue with
        different parameters. In this case, we'll close the connection
        to shutdown the object.
        :param pika.channel.Channel: The closed channel
        :param Exception reason: why the channel was closed
        """
        LOGGER.warning('Channel %i was closed: %s', channel, reason)
        self.close_connection()

    def set_qos(self):
        """This method sets up the consumer prefetch to only be delivered
        one message at a time. The consumer must acknowledge this message
        before RabbitMQ will deliver another one. You should experiment
        with different prefetch values to achieve desired performance.
        """
        self._channel.basic_qos(
            prefetch_count=self._prefetch_count, callback=self.on_basic_qos_ok)

    def on_basic_qos_ok(self, _unused_frame):
        """Invoked by pika when the Basic.QoS method has completed. At this
        point we will start consuming messages by calling start_consuming
        which will invoke the needed RPC commands to start the process.
        :param pika.frame.Method _unused_frame: The Basic.QosOk response frame
        """
        LOGGER.info('QOS set to: %d', self._prefetch_count)
        self.start_consuming()

    def start_consuming(self):
        """This method sets up the consumer by first calling
        add_on_cancel_callback so that the object is notified if RabbitMQ
        cancels the consumer. It then issues the Basic.Consume RPC command
        which returns the consumer tag that is used to uniquely identify the
        consumer with RabbitMQ. We keep the value to use it when we want to
        cancel consuming. The on_message method is passed in as a callback pika
        will invoke when a message is fully received.
        """
        LOGGER.info('Issuing consumer related RPC commands')
        self.add_on_cancel_callback()
        if self._callback is None:
            self._callback = self.on_message
        self._consumer_tag = self._channel.basic_consume(
            self._queue, self._callback)
        self.was_consuming = True
        self._consuming = True

    def add_on_cancel_callback(self):
        """Add a callback that will be invoked if RabbitMQ cancels the consumer
        for some reason. If RabbitMQ does cancel the consumer,
        on_consumer_cancelled will be invoked by pika.
        """
        LOGGER.info('Adding consumer cancellation callback')
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

    def on_consumer_cancelled(self, method_frame):
        """Invoked by pika when RabbitMQ sends a Basic.Cancel for a consumer
        receiving messages.
        :param pika.frame.Method method_frame: The Basic.Cancel frame
        """
        LOGGER.info('Consumer was cancelled remotely, shutting down: %r',
                    method_frame)
        if self._channel:
            self._channel.close()

    def on_message(self, _unused_channel, basic_deliver, properties, body):
        """Invoked by pika when a message is delivered from RabbitMQ. The
        channel is passed for your convenience. The basic_deliver object that
        is passed in carries the exchange, routing key, delivery tag and
        a redelivered flag for the message. The properties passed in is an
        instance of BasicProperties with the message properties and the body
        is the message that was sent.
        :param pika.channel.Channel _unused_channel: The channel object
        :param pika.Spec.Basic.Deliver: basic_deliver method
        :param pika.Spec.BasicProperties: properties
        :param bytes body: The message body
        """
        LOGGER.info('Received message # %s from %s: %s',
                    basic_deliver.delivery_tag, properties.app_id, body)
        self.acknowledge_message(basic_deliver.delivery_tag)

    def acknowledge_message(self, delivery_tag):
        """Acknowledge the message delivery from RabbitMQ by sending a
        Basic.Ack RPC method for the delivery tag.
        :param int delivery_tag: The delivery tag from the Basic.Deliver frame
        """
        LOGGER.info('Acknowledging message %s', delivery_tag)
        self._channel.basic_ack(delivery_tag)

    def stop_consuming(self):
        """Tell RabbitMQ that you would like to stop consuming by sending the
        Basic.Cancel RPC command.
        """
        if self._channel:
            LOGGER.info('Sending a Basic.Cancel RPC command to RabbitMQ')
            cb = functools.partial(
                self.on_cancelok, userdata=self._consumer_tag)
            self._channel.basic_cancel(self._consumer_tag, cb)

    def on_cancelok(self, _unused_frame, userdata):
        """This method is invoked by pika when RabbitMQ acknowledges the
        cancellation of a consumer. At this point we will close the channel.
        This will invoke the on_channel_closed method once the channel has been
        closed, which will in-turn close the connection.
        :param pika.frame.Method _unused_frame: The Basic.CancelOk frame
        :param str|unicode userdata: Extra user data (consumer tag)
        """
        self._consuming = False
        LOGGER.info(
            'RabbitMQ acknowledged the cancellation of the consumer: %s',
            userdata)
        self.close_channel()

    def close_channel(self):
        """Call to close the channel with RabbitMQ cleanly by issuing the
        Channel.Close RPC command.
        """
        LOGGER.info('Closing the channel')
        self._channel.close()

    def run(self):
        """Run the example consumer by connecting to RabbitMQ and then
        starting the IOLoop to block and allow the AsyncioConnection to operate.
        """
        self._connection = self.connect()
        self._connection.ioloop.run_forever()

    def stop(self):
        """Cleanly shutdown the connection to RabbitMQ by stopping the consumer
        with RabbitMQ. When RabbitMQ confirms the cancellation, on_cancelok
        will be invoked by pika, which will then closing the channel and
        connection. The IOLoop is started again because this method is invoked
        when CTRL-C is pressed raising a KeyboardInterrupt exception. This
        exception stops the IOLoop which needs to be running for pika to
        communicate with RabbitMQ. All of the commands issued prior to starting
        the IOLoop will be buffered but not processed.
        """
        if not self._closing:
            self._closing = True
            LOGGER.info('Stopping')
            if self._consuming:
                self.stop_consuming()
                try:
                    self._connection.ioloop.run_forever()
                except RuntimeError:
                    pass
            else:
                self._connection.ioloop.stop()
            LOGGER.info('Stopped')


class BrokerOncePublisher:
    """
    Class contains functions for a message publisher
    """
    def __init__(self, connection_parameter):
        """
        Constructor

        :param connection_parameter: connection parameter, built via 'build_conn_par' in the class 'Broker'
        """
        self._connection_parameter = connection_parameter
        self._connection = None
        self._channel = None

    @property
    def connection_parameter(self):
        return self._connection_parameter

    @connection_parameter.setter
    def connection_parameter(self, value):
        self._connection_parameter = value

    def connect(self):
        """
        This method connects to RabbitMQ via BlockingConnection

        :return: None
        """
        self._connection = raise_error_from_s3ib_amqp(pika.BlockingConnection, S3IBrokerAMQPError,
                                                      self._connection_parameter)
        self._channel = raise_error_from_s3ib_amqp(self._connection.channel, S3IBrokerAMQPError)
        self._channel.confirm_delivery()

    def send(self, receiver_endpoints, msg):
        """
        This method sends a message to one or more endpoints (queues). After the sending, the connection will be aborted

        :param receiver_endpoints: queues of receivers
        :type receiver_endpoints: list
        :param msg: message
        :return: None
        """
        self.connect()
        if self._channel is None or not self._channel.is_open:
            raise S3IBrokerAMQPError(error_msg="Broker Channel is not open")
        for endpoint in receiver_endpoints:
            raise_error_from_s3ib_amqp(self._channel.basic_publish, S3IBrokerAMQPError, exchange="demo.direct",
                                       routing_key=endpoint,
                                       properties=pika.BasicProperties(content_type="application/json",
                                                                       delivery_mode=2),
                                       body=msg, mandatory=True)
        self.stop_publish()

    def stop_publish(self):
        """
        This method disconnects to RabbitMQ

        :return: None
        """
        if self._channel:
            self._channel.close()
        if self._connection:
            if self._connection.is_closed:
                return
            self._connection.close()


class BrokerOnceReceiver:
    """
    Class contains functions for a broker receiver, which only receives one message before disconnecting
    """
    def __init__(self, connection_parameter):
        """
        Constructor

        :param connection_parameter: Connection parameter, built via 'built_conn_par' in the class 'Broker'
        """
        self._connection_parameter = connection_parameter
        self._channel = None
        self._connection = None

    @property
    def connection_parameter(self):
        return self._connection_parameter

    @connection_parameter.setter
    def connection_parameter(self, value):
        self._connection_parameter = value

    def connect(self):
        """
        This method connects to RabbitMQ via Blocking connection
        :return: None
        """
        self._connection = raise_error_from_s3ib_amqp(pika.BlockingConnection, S3IBrokerAMQPError,
                                                      self._connection_parameter)
        self._channel = raise_error_from_s3ib_amqp(self._connection.channel, S3IBrokerAMQPError)

    def receive_once(self, queue):
        """
        This method receive only one message before disconnecting

        :param queue: endpoint of the receiver
        :return: message body
        :rtype: bytearray
        """
        self.connect()
        method_frame, header_frame, body = raise_error_from_s3ib_amqp(self._channel.basic_get, S3IBrokerAMQPError,
                                                                      queue)
        if method_frame:
            raise_error_from_s3ib_amqp(self._channel.basic_ack, S3IBrokerAMQPError, method_frame.delivery_tag)
        self.stop_receive()
        return body

    def stop_receive(self):
        """
        This method disconnects to RabbitMQ

        :return: None
        """
        if self._channel:
            self._channel.close()
        if self._connection:
            if self._connection.is_closed:
                return
            self._connection.close()


