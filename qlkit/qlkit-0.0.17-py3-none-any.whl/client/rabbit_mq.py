#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pika
from ..event import EventsTransfer


class RabbitMqClient:

    def __init__(self, username, password, host, port=5672):
        self.host = str(host)
        self.port = int(port)
        self.crt = pika.PlainCredentials(username, password)
        self.conn = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.host, port=self.port, credentials=self.crt))
        self.channel = self.conn.channel()

    def declare_queue(self, exchange_name: str, queue_name: str,
                      routing_key: str, is_durable: bool=False, is_dead: bool=False,
                      message_ttl: int=30):
        """
        :param exchange_name:
        :param queue_name:
        :param routing_key:
        :param is_durable: 是否持久化该队列
        :param is_dead: if True will create retry_queue, fail_queue
        :param message_ttl: dead-letter-msg ttl(s)
        :return:
        retry_queue: 死信队列，每隔30s把处理失败的message重新放回master_queue重新处理业务
        fail_queue: 重试一定次数之后丢入该丢列，目前只有存储作用
        """
        self.channel.queue_declare(queue=queue_name, durable=is_durable)
        self.channel.queue_bind(queue_name, exchange_name, routing_key)

        # if is_dead:
        #     arguments = {
        #         "x-message-ttl": message_ttl * 1000,
        #         "x-dead-letter-exchange": exchange_name,
        #         "x-dead-letter-routing-key": routing_key,
        #     }
        #     retry_queue = retry_key = queue_name + "_retry"
        #     fail_queue = fail_key = queue_name + "_fail"
        #     self.channel.queue_declare(
        #         queue=retry_queue, durable=is_durable, arguments=arguments)
        #     self.channel.queue_bind(retry_queue, exchange_name, retry_key)
        #
        #     self.channel.queue_declare(queue=fail_queue, durable=is_durable)
        #     self.channel.queue_bind(fail_queue, exchange_name, fail_key)

    def declare_exchange(self, exchange_name, exchange_type="direct"):
        self.channel.exchange_declare(exchange=exchange_name, exchange_type=exchange_type)

    def produce(self, r_key, msg, ex='', transfer: EventsTransfer=None, properties=None):
        """
        :param r_key: exchange 会以这个key为为路由发送消息到队列
        :param msg: json
        :param ex: 指定把消息发到哪个exchange
        :param transfer: 根据队列名序列化信息
        :param properties: 重试的properties带有x-retry-count
        :return:
        """
        if not properties:
            properties = pika.BasicProperties(
                                       delivery_mode=2,  # make message persistent
                                   )
        self.channel.basic_publish(exchange=ex,
                                   routing_key=r_key,
                                   body=transfer.serializer(msg),
                                   properties=properties)

    def set_pos(self, prefetch_count=10):
        """
        :param prefetch_count: 同一时刻，发送多少个信息给worker
        """
        self.channel.basic_qos(prefetch_count=prefetch_count)

    def close(self):
        """
        当投递大量消息的时候，调用close可确保缓冲区的消息已经投递到RabbitMQ
        """
        self.conn.close()

