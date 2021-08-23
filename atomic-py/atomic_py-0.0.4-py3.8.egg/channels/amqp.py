import socket
import functools
import pika

from atomic import logger_manager

from atomic.channels.configuration import ChannelConfiguration
from atomic.exceptions import ConnectionException
import threading


class AmqpMessageProperties:
  """
    Propiedades de los mensajes amqp
    """

  def __init__(self):
    self.content_type = 'application/json'
    self.content_encoding = 'utf-8'
    self.headers = dict()
    self.delivery_mode = 2
    self.priority = 0
    self.correlation_id = None
    self.reply_to = None
    self.expiration = None
    self.app_id = None
    self.message_id = None

  def to_dict(self):
    """
        Convierte la propiedades en un objeto del tipo pika BasicProperties
        para el envio del mensaje
        :return: pika.BasicProperties
        """
    properties = dict()
    if self.content_type is not None:
      properties['content_type'] = self.content_type

    if self.content_encoding is not None:
      properties['content_encoding'] = self.content_encoding

    if self.headers is not None and len(self.headers) > 0:
      properties['headers'] = self.headers

    properties['delivery_mode'] = self.delivery_mode
    properties['priority'] = self.priority

    if self.correlation_id is not None:
      properties['correlation_id'] = self.correlation_id

    if self.reply_to is not None:
      properties['reply_to'] = self.reply_to

    if self.expiration is not None:
      properties['expiration'] = self.expiration

    if self.app_id is not None:
      properties['app_id'] = self.app_id

    if self.message_id is not None:
      properties['message_id'] = self.message_id

    return properties

  def to_pika_basic_properties(self):
    prop = pika.BasicProperties(
        content_type=self.content_type,
        content_encoding=self.content_encoding,
        headers=self.headers,
        delivery_mode=self.delivery_mode,
        priority=self.priority,
        correlation_id=self.correlation_id,
        reply_to=self.reply_to,
        expiration=self.expiration,
        app_id=self.app_id,
        message_id=self.message_id)
    return prop

  @classmethod
  def from_basic_properties(cls, properties):
    """
        Crea una instancia de AmqpMessageProperties a partir de las BasicProperties
        recibidas
        :param properties: propiedades
        :return:
        """
    amp = AmqpMessageProperties()
    amp.content_encoding = properties.content_encoding
    amp.message_id = properties.message_id
    amp.reply_to = properties.reply_to
    amp.app_id = properties.app_id
    amp.expiration = properties.expiration
    amp.correlation_id = properties.correlation_id
    amp.priority = properties.priority
    amp.headers = properties.headers
    amp.content_type = properties.content_type

    return amp

  @classmethod
  def create(cls):
    properties = AmqpMessageProperties()
    properties.delivery_mode = 2
    return properties


class AmqpMesageFrame:

  @classmethod
  def from_message_frame(cls, frame):
    """
        Crea una instance de AmqpMessageFrame a partir de las propiedades
        del mensaje que se ha recibido
        :param frame: Basic.Deliver
        :return: AmqpMessageFrame
        """
    amf = AmqpMesageFrame()
    amf.exchange = frame.exchange
    amf.consumer_tag = frame.consumer_tag
    amf.delivery_tag = frame.delivery_tag
    amf.routing_key = frame.routing_key
    amf.redelivered = frame.redelivered
    return amf

  def __init__(self):
    self.consumer_tag = None
    self.delivery_tag = None
    self.routing_key = None
    self.exchange = None
    self.redelivered = None


class AmqpMessage:

  @classmethod
  def create_from_message(cls, method_frame, header_frame, body):
    """
        Crea una instancia de AmqpMessage a partir del mensaje recibido
        :param message:
        :return:
        :rtype: atomic.channels.amqp.AmqpMessage
        """
    amf = AmqpMesageFrame.from_message_frame(method_frame)
    amp = AmqpMessageProperties.from_basic_properties(header_frame)
    return AmqpMessage(amf, amp, body, amf.routing_key)

  def __init__(self, frame: AmqpMesageFrame, properties: AmqpMessageProperties, body: bytes, routing_key: str):
    self.frame = frame
    self.properties = properties
    self.body = body
    self.routing_key = routing_key


class AmqpConnection:
  """
    Conexion a amqp
    """

  def __init__(self, configuration: ChannelConfiguration):
    self._configuration = configuration
    """
        :type: channels.configuration.ChannelConfiguration
        """
    self._connection = None
    self._isConnected = False
    self._channel = None
    self._closing = False
    self._consuming = False
    self._consumer_tag = None
    self._channel_send = None
    self._mutex = threading.Lock()
    self._mutex_ack = threading.Lock()

    self.on_message_received = None

  def connect(self):
    """
        Realiza la conexion con el host
        """

    if self._isConnected:
      return

    self._isConnected = False

    while not self._closing:
      try:
        logger_manager.get_logger().info('Conectando a %s', self._configuration.uri)
        self._connect_point()
        self._isConnected = True
        return
      except Exception as ex:
        logger_manager.get_logger().error("Error al conectar: %s", ex)
        logger_manager.get_logger().error("Intentado reconectar... Host: %s", self._configuration.uri)

  def _connect_point(self):
    try:
      if self._connection is not None and self._connection.is_open:
        self._connection.close()

      parameters = pika.URLParameters(self._configuration.uri)
      parameters.heartbeat = self._configuration.heartbeat

      logger_manager.get_logger().debug('Creando conexion')

      self._connection = pika.BlockingConnection(parameters=parameters)

      logger_manager.get_logger().debug('Creando channel')
      self._channel = self._connection.channel(1)
      self._channel_send = self._connection.channel(2)

      if self._configuration.exchange.create:
        logger_manager.get_logger().debug('Creando exchange')
        self._channel.exchange_declare(
            self._configuration.exchange.name, self._configuration.exchange.type.value, durable=True, auto_delete=False)

      if self._configuration.queue.create and self._configuration.queue.name is not None:
        logger_manager.get_logger().debug('Creando cola')
        self._channel.queue_declare(queue=self._configuration.queue.name, durable=True, auto_delete=False)

        for key in self._configuration.queue.get_routing_keys():
          self._channel.queue_bind(
              queue=self._configuration.queue.name, exchange=self._configuration.exchange.name, routing_key=key)
      self._channel.basic_qos(0, self._configuration.prefetch_count, False)
      if self._configuration.confirm_sent:
        self._channel_send.confirm_delivery()

    except Exception as ex:
      logger_manager.get_logger().error('Error Creando conexion', ex)
      raise ConnectionException(ex)

  def bind_parent(self, parent_exchange):
    for key in self._configuration.queue.get_routing_keys():
      self._channel.exchange_bind(self._configuration.exchange.name, parent_exchange, routing_key=key)

  def close(self):
    """
        Cierra la conexion del channel
        """
    logger_manager.get_logger().info('Cerrando conexion')
    self._closing = True
    if self._isConnected:
      try:
        self._channel.close()
      except Exception as ex:
        logger_manager.get_logger().info("Error al cerrar: %s", ex)

      try:
        self._channel_send.close()
      except Exception as ex:
        logger_manager.get_logger().info("Error al cerrar: %s", ex)

      try:
        self._connection.close()
      except Exception as ex:
        logger_manager.get_logger().info("Error al cerrar: %s", ex)

      self._connection = None

    self._closing = False
    self._isConnected = False

  def publish(self, message: bytes, routing_key: str, amqp_message_properties: AmqpMessageProperties):
    """
        Publica un mensaje en el amqp
        :param amqp_message_properties: Propiedades del mensaje
        :param message: Cadena con el mensaje
        :param routing_key: Clave de enrutamiento del mensaje
        """
    self._mutex.acquire()
    while not self._closing:
      try:
        properties = amqp_message_properties.to_pika_basic_properties()
        self._channel_send.basic_publish(
            self._configuration.exchange.name,
            routing_key,
            message,
            properties,
            mandatory=self._configuration.confirm_delivery)
        break
      except pika.exceptions.UnroutableError as unroute_exception:
        logger_manager.get_logger().warn("No es posible enrutar el mensaje %s" % routing_key)
        break
      except Exception as ex:
        logger_manager.get_logger().error("Error de conexion al enviar el mensaje %s" % ex)
        self.close()
        self.connect()

    self._mutex.release()

  def consume(self):
    self._consuming = True
    self._consumer_tag = self._channel.basic_consume(self._configuration.queue.name, self.__read_message)
    logger_manager.get_logger().info("Start Consuming %s", self._consumer_tag)
    self._channel.start_consuming()

  def drain_events(self, timeout):
    # self._connection.drain_events(timeout=timeout)
    pass

  # def __read_message(self, message):
  def __read_message(self, channel, method_frame, header_frame, body):
    logger_manager.get_logger().debug("Message Received %s", str(body, encoding='utf-8'))
    amqp_message = AmqpMessage.create_from_message(method_frame, header_frame, body)
    self.on_message_received(amqp_message)

  def ack(self, message: AmqpMessage):
    """
        Realiza el ack del mensaje en el servidor amqp
        :param message: Mensaje del que se realiza el ack
        """

    try:
      self._mutex_ack.acquire()
      cb = functools.partial(self._ack_message, self._channel, message.frame.delivery_tag)
      self._connection.add_callback_threadsafe(cb)
    except Exception as ex:
      logger_manager.get_logger().error("Error al enviar el ack", ex)
    finally:
      self._mutex_ack.release()

  def _ack_message(self, channel, delivery_tag):
    channel.basic_ack(delivery_tag=delivery_tag, multiple=False)

  def basic_cancel(self):
    self._consuming = False
    # self._channel.basic_cancel(self._consumer_tag)
    cb = functools.partial(self._basic_cancel, self._channel, self._consumer_tag)
    self._connection.add_callback_threadsafe(cb)

  def _basic_cancel(self, channel, consumer_tag):
    channel.stop_consuming(consumer_tag)
