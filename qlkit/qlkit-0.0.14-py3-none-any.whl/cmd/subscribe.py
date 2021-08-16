#!/usr/bin/env python
# -*- coding: utf-8 -*-
import traceback
from . import Server
from ..config import DEFAULT_CONFIG
from ..event import EventsTransfer
from ..client.rabbit_mq import RabbitMqClient
from .. import log


class SubscribeServer(Server):
    def __init__(self, mq_client: RabbitMqClient, config: dict = None):
        self.mq_client = mq_client
        self.config = config if config else DEFAULT_CONFIG

    # TODO SubscribeServer start
    def start(self):
        pass

    # TODO SubscribeServer graceful_stop
    def graceful_stop(self):
        pass

    # TODO SubscribeServer handle_term_signal
    def handle_term_signal(self):
        pass

    def run_forever(self):
        self.mq_client.channel.start_consuming()


def run_subscribe_server_forever(server: SubscribeServer):
    """
    Run gRPC server as daemon process.
    While received SIGTERM signals, it will shutdown gracefully.
    :return:
    """
    logger = log._get_root_logger()
    server.start()
    logger.info("subscribe server start")

    # def handle_signal_term(*_):
    #     logger.info(
    #         f"gRPC server received term signal, will shutdown "
    #         f"after {server.config['grpc_graceful_shutdown']} seconds"
    #     )
    #     server.graceful_stop()
    #     logger.info("gRPC server terminated")
    #
    # signal.signal(signal.SIGTERM, handle_signal_term)

    server.run_forever()


def add_subscriber_to_server(
        server: SubscribeServer,
        routing_key: str,
        exchange_name: str,
        queue_name: str,
        func: "function",
        transfer: EventsTransfer
):

    server.mq_client.channel.basic_consume(
        routing_key, __worker_wrapper(exchange_name, queue_name, func, transfer))


def __worker_wrapper(exchange_name: str, queue_name: str,
                     bz_func: "function", transfer: EventsTransfer):
    logger = log._get_root_logger("subscriber")

    def func(ch, method, properties, body):
        logger.info("exchange %s queue %s Received %r" % (exchange_name, queue_name, body))
        try:
            json_dict = transfer.deserializer(body)
            error = bz_func(json_dict)
        except Exception:
            error = traceback.print_exc()

        # if error:
        #     if not properties.headers or properties.headers['x-death'][0]['count'] <= 3:
        #         retry_queue = queue_name + "_retry"
        #         ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
        #         mq_client.produce(retry_queue, body, exchange_name, properties)
        #         logger.warning("exchange %s queue %s rejected %s" % (exchange_name, queue_name, error))
        #     else:
        #         retry_queue = queue_name + "_fail"
        #         ch.basic_ack(delivery_tag=method.delivery_tag)
        #         mq_client.produce(retry_queue, body, exchange_name, properties)
        #         logger.warning("exchange %s queue %s time out" % (exchange_name, queue_name))
        # else:
        #     logger.info("exchange %s queue %s done" % (exchange_name, queue_name))
        #     ch.basic_ack(delivery_tag=method.delivery_tag)

        if error:
            logger.info("exchange %s queue %s done" % (exchange_name, queue_name))
        else:
            logger.warning("exchange %s queue %s rejected %s" % (exchange_name, queue_name, error))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    return func
