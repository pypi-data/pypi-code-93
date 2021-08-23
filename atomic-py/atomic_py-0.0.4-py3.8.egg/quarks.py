from __future__ import annotations
from atomic.particles import Context, Accelerator


def quark(key):

  def decorator(f):
    QuarkManager.get_instance().add_quark(key, f)
    return f

  return decorator


class QuarkManager:
  """
    Controla los quarks de los mensajes
    """
  _instance = None

  @classmethod
  def get_instance(cls) -> QuarkManager:
    if cls._instance is None:
      cls._instance = QuarkManager()
    return cls._instance

  def __init__(self):
    self.__quarks = dict()

  def add_quark(self, key, class_type):
    self.__quarks[key] = class_type

  def get_quark(self, key):
    """
        Devuelve el putero a la clase del quark que controla el tipo de mensaje
        :param key: Clave de enrutamiento
        :return:
        """
    return self.__quarks[key] if key in self.__quarks else None

  def get_routing_keys(self):
    """
        Devuelve la lista de routing keys de los quarks
        :return: routing key list
        """
    return self.__quarks.keys()

  def clear(self):
    self.__quarks.clear()

  def clone(self):
    quark_manager = QuarkManager()
    for key in self.get_routing_keys():
      value = self.get_quark(key)
      quark_manager.add_quark(key, value)
    return quark_manager


class BaseQuark:
  """
    Clase base para los quarks
    """

  def __init__(self):
    self.__message = None
    """
        :rtype: dict
        """
    self.__accelerator = None
    """
        :rtype: atomic.particles.Accelerator
        """
    self.__context = None
    """
        :rtype: atomic.particles.Context
        """

  def initialize(self, accelerator: Accelerator, context: Context, message: str):
    """
        Inicializa el quark con los parametros del mensaje amqp
        :param publisher: Publicador
        :param context: Contexto del mensaje
        :param message: Mensaje Amqp
        :return:
        """
    self.__message = message
    self.__accelerator = accelerator
    self.__context = context

  def _get_message(self):
    """
        Devuelve el mensaje
        :return: Mensaje
        """
    return self.__message

  def _get_header(self, key: str) -> str:
    """
        Devuelve la cabecera asociada a la clave
        :param key: Clave de la cabecera
        :return: Valor de la cabecera
        :rtype: str
        """
    return self.__context.get_item(key)

  def _get_headers(self) -> dict:
    """Devuelve las cabeceras como diccionario

    :return: Cabeceras del mensaje
    :rtype: dict
    """
    return self.__context

  def _has_header(self, key: str) -> bool:
    """Indica si la cabecera existe

    :param key: Clave de la cabecera
    :type key: str
    :return: True si existe, False en caso contrario
    :rtype: bool
    """
    return self.__context.has_header(key)

  def _add_header(self, key: str, value: str):
    """
        Añade una cabecera o la actualiza
        :param key: Clave de la cabecera
        :param value: Valor de la cabecera
        """
    self.__context.add_header(key, value)

  def interact(self):
    pass

  def launch(self, message, routing_key: str):
    """
        Publica un mensaje en el broker
        :param message: Mensaje a enviar en string
        :param routing_key: Clave de enrutamiento
        """
    self.__accelerator.launch(message, routing_key, self.__context)
