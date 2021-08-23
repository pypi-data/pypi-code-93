from __future__ import annotations
import json
from atomic.channels.amqp import AmqpMessage, AmqpMessageProperties
from atomic.channels.channel import Channel
from atomic.channels.configuration import ChannelConfiguration

from atomic import logger_manager


class Context:
  """
    Contiene la informacion del contexto de ejecución del mensaje
    """

  def __init__(self, properties: AmqpMessageProperties):
    """
        Crea una instancia del contexto
        :param properties: Propiedades del contexto
        """
    self.properties = properties

  def get_headers(self) -> dict:
    """
        Devuelve el diccionario de las cabeceras
        :return: Diccionario
        :rtype: dict
        """
    return self.properties.headers

  def get_item(self, key: str) -> str:
    """
        Devuelve el elemento en funcion de su clave, si la clave no existe devuelve None
        :param key: Clave del elemento
        :return: Cadena con el elemento o None
        :rtype: str
        """
    return self.properties.headers[key] if key in self.properties.headers else None

  def add_header(self, key: str, value: str):
    """
        Añade o actualiza una cabecera en el contexto
        :param key: Clave de la cabecera
        :param value: Valor de la cabecera
        """
    self.properties.headers[key] = value

  def add_header(self, headers: dict):
    """
        Añade o actualiza una cabecera en el contexto
        :param headers: diccionario de cabeceras
        """
    self.properties.headers.update(headers)

  def has_header(self, key: str) -> bool:
    """Indica si esta presente la cabecera en el contexto

    :param key: clave de la cabecera
    :type key: str
    :return: Cierto si exite, falso en caso contrario
    :rtype: bool
    """
    return key in self.properties.headers


class ContextFactory:
  """
    Factoria para la creacion de contextos
    """

  @classmethod
  def create_from_amqp_message(cls, message: AmqpMessage) -> Context:
    """
        Crea una instancia del contexto a partir del mensaje que ha llegado
        :param message:
        :return:
        """
    properties = AmqpMessageProperties.create()
    properties.headers = message.properties.headers
    properties.correlation_id = message.properties.correlation_id
    properties.app_id = message.properties.app_id

    return Context(properties)

  @classmethod
  def create_empty(cls) -> Context:
    """
        Crea una instancia del contexto vacia
        :return: Contexto
        :rtype: atomic.particles.Context
        """
    properties = AmqpMessageProperties.create()

    return Context(properties)

  @classmethod
  def create_from_headers(cls, headers: dict) -> Context:
    """
        Crea una instancia del contexto a partir de las cabeceras
        :param headers: diccionario con las cabeceras del mensaje
        :return:
        """
    context = cls.create_empty()
    context.add_headers(headers)
    return context


class Accelerator:
  """
    Publicador de mensajes
    """

  def __init__(self, name: str, channel: Channel):
    self._channel = channel
    self.name = name

  def connect(self):
    """
        Realiza la conexion del canal
        """
    logger_manager.get_logger().debug("Service - Conectando Canal de envio")
    self._channel.connect()

  def launch(self, message: str, routing_key: str, context: Context = None):
    """
        Publica un mensaje en el canal
        :param routing_key: Clave de enrutamiento
        :param message: Cuerpo del mensaje
        :param context: Contexto del mensaje
        """
    if context is None:
      context = ContextFactory.create_empty()

    logger_manager.get_logger().debug("Service - Publicando Mensaje")
    encoding = context.properties.content_encoding if context.properties.content_encoding is not None else 'utf-8'
    self._channel.publish(bytes(message, encoding), routing_key, context.properties)

  def close(self):
    """
        Cierra la conexion del canal
        """
    self._channel.close()


class AcceleratorFactory:
  """
    Factory de publicadores
    """

  @classmethod
  def create(cls, name: str, config: ChannelConfiguration) -> Accelerator:
    """
        Crea una instancia de un publicador
        :param name: Accelerator name
        :param config: Configuracion del publicador
        :return:
        """
    channel = Channel.create(config)
    return Accelerator(name, channel)


class Particle(Accelerator):
  """
    Clase de Servicio
    """

  def __init__(self, name: str, channel_sender: Channel, channel_receiver: Channel, quark_manager: QuarkManager):
    Accelerator.__init__(self, name, channel_sender)
    self.channel_receiver = channel_receiver
    self.channel_receiver.on_message_received = self._message_received
    self.quark_manager = quark_manager
    """
    type: atomic.quarks.QuarkManager
    """

  def run(self):
    self.connect()
    logger_manager.get_logger().debug("Particle - Run %s", self.name)
    self.channel_receiver.consume()

  def stop(self):
    logger_manager.get_logger().debug("Service - Stop - Waiting for channel")
    self.channel_receiver.stop_consuming()
    self.close()

  def connect(self):
    Accelerator.connect(self)
    logger_manager.get_logger().debug("Service - Conectando Canal de recepcion")
    self.channel_receiver.connect()
    if self.channel_receiver.get_config().exchange.name != self._channel.get_config().exchange.name:
      self.channel_receiver.bind_parent(self._channel.get_config().exchange.name)

  def close(self):
    Accelerator.close(self)
    self.channel_receiver.close()

  def _send_error(self, message: bytes, ex: Exception):
    message_error = dict()
    message_error['description'] = str(ex)
    message_error['message'] = message
    str_error = json.dumps(message_error)
    self._channel.publish(bytes(str_error, 'utf-8'), 'Message.Error', AmqpMessageProperties.create())

  def _message_received(self, message: AmqpMessage):
    try:
      logger_manager.get_logger().debug("Service - Received Message")
      encoding = message.properties.content_encoding \
          if message.properties.content_encoding is not None else 'utf-8'

      message_str = str(message.body, encoding=encoding)
      quark_class = self.quark_manager.get_quark(message.frame.routing_key)
      if quark_class is not None:
        quark = quark_class()
        quark.initialize(self, ContextFactory.create_from_amqp_message(message), message_str)
        quark.interact()
      else:
        logger_manager.get_logger().warning("Quark Manager: No existe quark para el tipo: %s",
                                            message.frame.routing_key)

    except Exception as ex:
      logger_manager.get_logger().error("Particle - Error al procesar el mensaje", exc_info=ex)
      self._send_error(message.body, ex)
    finally:
      self.channel_receiver.ack(message)


class ParticleFactory:
  """
    Factoria para las particulas
    """

  @classmethod
  def create(cls, name: str, config_sender: ChannelConfiguration, config_receiver: ChannelConfiguration,
             quark_manager: QuarkManager) -> Particle:
    """
        Crea una instancia de un servicio
        :param handler_manager: controlador de los handlers de los mensajes
        :param config_receiver: configuracion del receptor
        :param config_sender: configuracion del publicador
        :param service_id: identificador del servicio
        :param service_type: tipo del servicio
        :return: Particle
        :rtype: atomic.particles.Particle
        """
    channel_sender = Channel.create(config_sender)
    channel_receiver = Channel.create(config_receiver)
    return Particle(name, channel_sender, channel_receiver, quark_manager)
