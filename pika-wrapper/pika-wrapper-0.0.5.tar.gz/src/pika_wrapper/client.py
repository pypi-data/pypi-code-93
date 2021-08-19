import functools
import json
import logging
import time
import threading
import random

from typing import Dict, Callable

import pika
from pika.spec import Basic
import pika.channel
import pika.adapters.blocking_connection
from pika.exchange_type import ExchangeType
from pika.adapters.blocking_connection import BlockingChannel


PAUSE = 1
MAX_PUBLISH_ATTEMPT = 10

# -------------- <add_logger> -------------- #
logger = logging.getLogger('pika_clients')
# -------------- </add_logger> -------------- #


class Exchange:
    is_declared: bool = False

    def __init__(self,
                 exchange: str = '',
                 exchange_type: ExchangeType = ExchangeType.direct,
                 passive: bool = False,
                 durable: bool = False,
                 auto_delete: bool = False,
                 internal: bool = False,
                 arguments: dict = None,
                 #  callback = None
                 ) -> None:
        self.exchange = exchange
        self.exchange_type = exchange_type
        self.passive = passive
        self.durable = durable
        self.auto_delete = auto_delete
        self.internal = internal
        self.arguments = arguments
        # self.callback = callback


class Queue:
    is_declared = False
    exchange: Exchange = None
    queue: str = ''

    def __init__(self,
                 name: str = '',
                 passive: bool = False,
                 durable: bool = False,
                 exclusive: bool = False,
                 auto_delete: bool = False,
                 arguments: dict = None,
                 #  callback = None,
                 ) -> None:
        self.name = name
        self.passive = passive
        self.exclusive = exclusive
        self.durable = durable
        self.exclusive = exclusive
        self.auto_delete = auto_delete
        self.arguments = arguments
        # self.callback = callback

        if not self.name:
            self.exclusive = True


class Client:
    channel: pika.channel.Channel
    queues: Dict[str, Queue]
    exchanges: Dict[str, Exchange]

    def __init__(self,
                 parameters: pika.URLParameters,
                 prefetch_count: int = 0
                 ) -> None:
        self.parameters = parameters
        self.prefetch_count = prefetch_count
        self.queues = {}
        self.exchanges = {}

    def connect(self):
        logger.info(f'    [*]    Pika trying connect')
        while True:
            try:
                self.connection = pika.BlockingConnection(self.parameters)
            except Exception as ex:
                logger.error(f'    [*]    Pika lost connection - "{ex}"')
                self.__pause()
            else:
                break
        logger.info('    [*]    Pika connected.')
        self.open_channel()
        self.set_qos()
        self.collect_queues()
        self.collect_exchanges()
        self.queues_bind()

    @property
    def is_connected(self):
        return self.connection.is_open

    def disconnect(self):
        try:
            self.connection.close()
        except Exception as ex:
            logger.error(
                f'    [*]    Unsuccessful attempt to close the pika connection - "{ex}"')

        for queue_name, queue in self.queues.items():
            queue.is_declared = False

        for exchange_name, exchange in self.exchanges.items():
            exchange.is_declared = False

        logger.info('    [*]    Pika disconnected.')

    def queue_delete(self, queue: Queue):
        try:
            self.channel.queue_delete(queue=queue.queue)
        except Exception as ex:
            logger.warning(
                f'    [*]    Unsuccessful delete queue "{queue.queue}" - {ex}')
        else:
            logger.info(f'    [*]    Success delete queue "{queue.queue}"')

    def exchange_delete(self, exchange: Exchange):
        try:
            self.channel.exchange_delete(exchange=exchange.exchange)
        except Exception as ex:
            logger.warning(
                f'    [*]    Unsuccessful delete exchange "{exchange.exchange}" - {ex}')
        else:
            logger.info(
                f'    [*]    Success delete exchange "{exchange.exchange}"')

    def open_channel(self):
        try:
            self.channel = self.connection.channel()
        except Exception as ex:
            logger.error(f'    [*]    Channel closed - "{ex}"')
            self.reconnect()
        else:
            logger.info('    [*]    Channel is opened.')

    def set_qos(self):
        try:
            self.channel.basic_qos(prefetch_count=self.prefetch_count)
        except Exception as ex:
            logger.error(f'    [*]    set basic_qos - "{ex}"')
            self.reconnect()
        else:
            logger.info(
                f'    [*]    set prefetch_count = "{self.prefetch_count}".')

    def setup_queue(self, queue: Queue) -> str:

        result = self.channel.queue_declare(
            queue=queue.name,
            passive=queue.passive,
            durable=queue.durable,
            exclusive=queue.exclusive,
            auto_delete=queue.auto_delete,
            arguments=queue.arguments,
            # callback=queue.callback
        )

        queue.queue = result.method.queue
        queue.is_declared = True

        if not queue.exchange:
            queue.exchange = Exchange()

        if (queue.exchange.exchange not in self.exchanges) and (queue.exchange.exchange != ''):
            self.exchanges[queue.exchange.exchange] = queue.exchange

    def collect_queues(self):
        for queue_name, queue in self.queues.items():
            if not queue.is_declared:
                try:
                    self.setup_queue(queue)
                except Exception as ex:
                    logger.error(
                        f'    [*]    Unsuccessful attempt setup queue "{queue.name}" - "{ex}"')
                    self.reconnect()
                else:
                    logger.info(
                        f'    [*]    Queue "{queue}" declared'
                    )

    def setup_exchange(self, exchange: Exchange):
        if exchange.exchange != '':
            self.channel.exchange_declare(
                exchange=exchange.exchange,
                exchange_type=exchange.exchange_type.value,
                passive=exchange.passive,
                durable=exchange.durable,
                auto_delete=exchange.auto_delete,
                internal=exchange.internal,
                arguments=exchange.arguments,
                # callback=exchange.callback
            )
        exchange.is_declared = True

    def collect_exchanges(self):
        for exchange_name, exchange in self.exchanges.items():
            if not exchange.is_declared:
                try:
                    self.setup_exchange(exchange)
                except Exception as ex:
                    logger.error(
                        f'    [*]    Unsuccessful attempt setup exchange "{exchange.exchange}" - "{ex}"')
                    self.reconnect()
                else:
                    logger.info(
                        f'    [*]    Exchange "{exchange}" declared'
                    )

    def queues_bind(self):
        for queue_name, queue in self.queues.items():
            if queue.exchange.exchange != '':
                try:
                    self.channel.queue_bind(
                        queue=queue.queue, exchange=queue.exchange.exchange
                    )
                except Exception as ex:
                    logger.error(
                        f'    [*]    Unseccesful attempt bind queue "{queue.name}" to exchange "{queue.exchange}" - "{ex}"'
                    )
                    self.reconnect()
                else:
                    logger.info(
                        f'    [*]    Queue "{queue.name}" binded to exchange "{queue.exchange}"'
                    )

    def reconnect(self):
        self.disconnect()
        self.__pause()
        self.connect()

    def __pause(self,
                multiplier: float = PAUSE
                ):
        time.sleep(random.random() * multiplier)

    def publish(self,
                body: bytes,
                queue: Queue = None,
                exchange: Exchange = None,
                attempt: int = 0,
                properties: pika.BasicProperties = pika.BasicProperties(),
                ) -> bool:

        if attempt > MAX_PUBLISH_ATTEMPT:
            return False

        if not self.is_connected:
            self.connect()

        if not queue and not exchange:
            return False

        if queue:
            if not queue.is_declared:
                self.setup_queue(queue=queue)
            _queue = queue.queue
            _exchange = ''
        elif exchange:
            if not exchange.is_declared:
                self.setup_exchange(exchange=exchange)
            _queue = ''
            _exchange = exchange.exchange

        try:
            self.channel.basic_publish(
                body=body,
                routing_key=_queue,
                exchange=_exchange,
                properties=properties
            )
        except Exception as ex:
            logger.error(
                f'    [*]    Unseccesful attempt publish message to queue "{_queue}", exchange "{_exchange}" - "{ex}"'
            )
            if self.channel.is_closed:
                self.reconnect()
            attempt += 1
            return self.publish(body=body,
                                queue=queue,
                                exchange=exchange,
                                attempt=attempt,
                                properties=properties
                                )
        else:
            logger.info(
                f'    [*]    Seccesful attempt publish message to queue "{queue}", exchange "{exchange}")'
            )
        return True

    @staticmethod
    def __threaded_callback(channel: BlockingChannel,
                            method: Basic.Deliver,
                            properties: pika.BasicProperties,
                            body: bytes,
                            connection: pika.BlockingConnection,
                            callback: Callable = None,
                            reply_to: str = ''
                            ):
#_____________________________________
        def __ack_message(channel: BlockingChannel,
                          delivery_tag
                          ) -> None:
            '''
            callback для передачи в threadsafe для правильного формирования
            acknowledgement в отдельном треде
            '''
            if channel.is_open:
                channel.basic_ack(delivery_tag)
            else:
                logger.warning(
                    f'    [*]    Channel {channel} is closed, there is no way to send a acknowledgement')
                pass

        def ack_threadsafe(delivery_tag: int):
            callback_threadsafe = functools.partial(
                __ack_message, channel, delivery_tag)
            connection.add_callback_threadsafe(callback_threadsafe)

#_____________________________________
        def __nack_message(channel: BlockingChannel,
                          delivery_tag
                          ) -> None:
            '''
            callback для передачи в threadsafe для правильного формирования
            negative_acknowledgement в отдельном треде
            '''
            if channel.is_open:
                channel.basic_nack(delivery_tag)
            else:
                logger.warning(
                    f'    [*]    Channel {channel} is closed, there is no way to send a acknowledgement')
                pass

        def nack_threadsafe(delivery_tag: int):
            callback_threadsafe = functools.partial(
                __nack_message, channel, delivery_tag)
            connection.add_callback_threadsafe(callback_threadsafe)
#_____________________________________

        def __reply_message(channel: BlockingChannel,
                            body: str,
                            queue: str,
                            properties: pika.BasicProperties = None
                            ):
            if queue:
                try:
                    channel.basic_publish(
                        exchange='',
                        routing_key=queue,
                        body=body,
                        properties=properties
                    )
                except Exception as ex:
                    logger.error(
                        f'    [*]    Unsuccessful attempt __reply_message - "{ex}"')
                else:
                    logger.info(
                        '    [*]    Successful attempt __reply_message')

        def reply_threadsafe(body: str):
            callback_threadsafe = functools.partial(
                __reply_message,
                channel=channel,
                body=body,
                queue=properties.reply_to or reply_to,
                properties=pika.BasicProperties(
                    correlation_id=properties.correlation_id
                ),
            )
            connection.add_callback_threadsafe(callback_threadsafe)
#_____________________________________

        def thread_wrapper(channel: BlockingChannel,
                           method: Basic.Deliver,
                           properties: pika.BasicProperties,
                           body: bytes,
                           callback: Callable = None,
                           reply_to: str = ''
                           ):

            # !!!!!!!!!!!!!!!!!!
            # Тут исполняется целевая функция
            try:
                success = callback(
                    body=body,
                    reply_threadsafe=reply_threadsafe
                )
            except Exception as ex:
                logger.error(f'    [*]    failed callback - "{ex}"')
                success = False
            # !!!!!!!!!!!!!!!!!!

            # Если callback вернул False, или упал, вернем сообщение в очередь
            if success == False:
                nack_threadsafe(method.delivery_tag)
            else:
                ack_threadsafe(method.delivery_tag)
#_____________________________________

        thread = threading.Thread(
            target=thread_wrapper,
            args=(
                channel,
                method,
                properties,
                body,
                callback,
                reply_to
            )
        )
        thread.start()

    def setup_consumer(self,
                       queue: Queue,
                       callback: Callable = None,
                       reply_to_queue: Queue = None
                       ):

        if not self.is_connected:
            self.connect()

        if reply_to_queue:
            if not reply_to_queue.is_declared:
                self.setup_queue(reply_to_queue)
            reply_to = reply_to_queue.queue
        else:
            reply_to = ''

        on_message_callback = functools.partial(self.__threaded_callback,
                                                callback=callback or self.callback,
                                                connection=self.connection,
                                                reply_to=reply_to
                                                )

        try:
            self.channel.basic_consume(
                queue=queue.queue,
                on_message_callback=on_message_callback
            )
        except Exception as ex:
            logger.error(
                f'    [*]    setup consume - "{ex}"'
            )
            self.reconnect()

    def start_consuming(self):
        self.channel.start_consuming()

    @staticmethod
    def callback(body: bytes,
                 reply_threadsafe: Callable = None
                 ) -> str:

        if reply_threadsafe:
            reply_threadsafe(body=json.dumps(
                {
                    'status': 'in_progress',
                    'body': body
                }
            ).encode()
            )

        time.sleep(1)

        if reply_threadsafe:
            reply_threadsafe(body=json.dumps(
                {
                    'status': 'Ok',
                    'body': body
                }
            ).encode()
            )
            
        return True
