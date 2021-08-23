import re
from enum import Enum


class AmqpElementConfiguration:
  """
    Clase base de configuracion de un elemento amqp
    como un exchange o una cola
    """

  def __init__(self):
    self.name = None
    self.create = True


class ExhangeType(Enum):
  DIRECT = "direct"
  TOPIC = "topic"


class ExchangeConfiguration(AmqpElementConfiguration):
  """
    Configuracion de un exchange
    """

  def __init__(self):
    AmqpElementConfiguration.__init__(self)
    self.type = ExhangeType.TOPIC

  def set_exchange_direct(self):
    """
        Establece el exchange de tipo direct
        """
    self.type = ExhangeType.DIRECT

  def set_exchange_topic(self):
    """
        Establece el exchange de tipo topic
        """
    self.type = ExhangeType.TOPIC


class QueueConfiguration(AmqpElementConfiguration):
  """
    Configuracion de una cola
    """

  def __init__(self):
    AmqpElementConfiguration.__init__(self)
    self._routingKeys = list()

  def add_routing_key(self, key):
    """
        Añade una clave de enrutamiento de la cola amqp
        :param key: Clave de enrutamiento
        """
    self._routingKeys.append(key)

  def get_routing_keys(self) -> list:
    """
        Devuelve la lista de claves de enrutamiento de la cola
        :return: Lista de claves
        :rtype: list
        """
    return self._routingKeys


class ConnectionParameters:
  """
    Contiene los parametros de conexion al servidor AMQP
    """

  @classmethod
  def create_from_uri(cls, uri: str):
    """
        Factory Method, crea extrae los parametros de la conexion a partir
        de una uri amqp://guest:guest@localhost:5672/
        :param uri: Url de conexion a AMQP
        :return: Propiedades de la conexion
        :rtype: atomic.channels.configuration.ConnectionParameters
        """
    params = ConnectionParameters()
    m = re.search('^amqp:\/\/((\w*):(\w*))?@?(([\w\-\.]*)(:(\d*))?)\/([\w%]*)', uri)
    params.host = m.group(5)

    if m.group(7) is not None and m.group(7) is not '':
      params.port = int(m.group(7))

    if m.group(2) is not None and m.group(2) is not '':
      params.userid = m.group(2)

    if m.group(3) is not None and m.group(3) is not '':
      params.password = m.group(3)

    if m.group(8) is not None and m.group(8) is not '':
      params.virtual_host = m.group(8)

    return params

  def __init__(self):
    self.host = 'localhost'
    self.userid = 'guest'
    self.password = 'guest'
    self.login_method = 'AMQPLAIN'
    self.virtual_host = '/'
    self.port = 5672


class ChannelConfiguration:
  """
    Congiguracion de un canal de comunicacion amqp
    """

  def __init__(self):
    self.uri = None
    self.exchange = ExchangeConfiguration()
    self.queue = QueueConfiguration()
    self.max_threads = 4
    self.heartbeat = 0
    self.prefetch_count = 100
    self.confirm_sent = True
    self.confirm_delivery = True

  def get_connection_parameters(self) -> ConnectionParameters:
    """
        Devuelve los parametros de la conexion
        :return: Parametros de la conexion
        :rtype: atomic.channels.configuration.ConnectionParameters
        """
    return ConnectionParameters.create_from_uri(self.uri)
