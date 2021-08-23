import socket
import threading
from concurrent.futures.thread import ThreadPoolExecutor

from atomic import logger_manager
from atomic.channels.amqp import AmqpConnection, AmqpMessageProperties, AmqpMessage
from atomic.channels.configuration import ChannelConfiguration


class Channel:

  @classmethod
  def create(cls, config: ChannelConfiguration):
    """
        Factory Method para crear channels
        :param config: Configuracion del chanel
        :return:
        """
    conn = AmqpConnection(config)
    channel = Channel(conn, config)
    return channel

  def __init__(self, connection: AmqpConnection, config: ChannelConfiguration):
    self._config = config
    self._connection = connection
    self._connection.on_message_received = self._message_received
    self.on_message_received = None
    self._thread_pool = ThreadPoolExecutor(max_workers=config.max_threads)
    self._thread_consumer = None
    self._is_consumming = False

  def _message_received(self, message: AmqpMessage):
    if self.on_message_received is not None:
      self._thread_pool.submit(self.on_message_received, message)
    #self._connection.ack(message)

  def get_config(self) -> ChannelConfiguration:
    return self._config

  def add_binding(self, routing_key):
    self._config.queue.add_routing_key(routing_key)

  def bind_parent(self, parent_exchange):
    self._connection.bind_parent(parent_exchange)

  def connect(self):
    self._connection.connect()

  def close(self):
    if self._is_consumming:
      self.stop_consuming()
    self._connection.close()

  def publish(self, message: bytes, routing_key: str, properties: AmqpMessageProperties):
    self._connection.publish(message, routing_key, properties)

  def consume(self):
    self._is_consumming = True
    self._thread_consumer = threading.Thread(target=self._worker_consumer)
    self._thread_consumer.start()

  def _worker_consumer(self):
    while self._is_consumming:
      try:
        self._connection.consume()
      except Exception as ex:
        logger_manager.get_logger().error("Error start consuming", ex)
        self._connection.close()
        self._connection.connect()

  #   while self._is_consumming:
  #     try:
  #       self._connection.drain_events(timeout=10)
  #     except socket.timeout:
  #       logger_manager.get_logger().debug("Check consuming status")
  #     except Exception as ex:
  #       logger_manager.get_logger().error("Error Consuming", ex)
  #       self._connection.close()
  #       self._connection.connect()
  #       self._connection.consume()

  #   logger_manager.get_logger().debug("Fin del hilo de consumicion")
  #   self._connection.basic_cancel()

  def stop_consuming(self):
    self._is_consumming = False
    self._connection.basic_cancel()
    self._thread_consumer.join()
    self._thread_pool.shutdown()

  def ack(self, message: AmqpMessage):
    self._connection.ack(message)
