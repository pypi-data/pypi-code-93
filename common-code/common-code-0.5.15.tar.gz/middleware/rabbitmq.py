import pika
import json


def rabbitMQ_decorator(function):
    def wrapper(obj, *args, **kwargs):
        assert hasattr(obj, "conn"), "No connection to rabbitMQ server"
        assert hasattr(obj, "channel"), "obj has no property of channel"
        return function(obj, *args, **kwargs)

    return wrapper


class RabbitMQ:
    def conn_and_channel(self, host=None, port=None, virtual_host=None, username=None, password=None):
        credentials = pika.PlainCredentials(username, password)  # mq用户名和密码
        # 虚拟队列需要指定参数 virtual_host，如果是默认的可以不填。
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host, port=port, virtual_host=virtual_host, credentials=credentials)
        )
        channel = connection.channel()
        self.conn = (connection,)
        self.channel = channel
        return connection, channel

    @rabbitMQ_decorator
    def declare_queue_and_bind_dead_letter_queue(
        self,
        exchange,
        queue,
        dead_letter_exchange,
        dead_letter_queue,
        routing_key=None,
        dead_letter_routing_key=None,
        exchange_type="direct",
        dead_letter_exchange_type="direct",
        ttl=None,
        auto_delete=False,
        durable=False,
        dead_letter_auto_delete=False,
        dead_letter_durable=False,
    ):
        """
        创建异常交换器和队列，用于存放没有正常处理的消息。
        :return:
        """
        assert exchange, "exchange is None!!!"
        assert queue, "queue is None!!!"
        # assert routing_key, 'routing_key is None!!!'
        assert exchange_type, "routing_key is None!!!"
        assert dead_letter_exchange, "dead_letter_exchange is None!!!"
        assert dead_letter_queue, "dead_letter_queue is None!!!"
        # assert dead_letter_routing_key, 'dead_letter_routing_key is None!!!'
        assert dead_letter_exchange_type, "routing_key is None!!!"
        assert not (dead_letter_exchange_type != "fanout" and (not dead_letter_routing_key)), (
            "dead_letter_exchange_type = " + dead_letter_exchange_type + " but dead_letter_routing_key is None!!!"
        )
        arguments = {}
        if dead_letter_exchange:
            # 设置死信转发的exchange，延迟结束后指向的交换机(死信收容交换机)
            arguments["x-dead-letter-exchange"] = dead_letter_exchange
        if dead_letter_routing_key:
            arguments["x-dead-letter-routing-key"] = dead_letter_routing_key
        if ttl:
            # 消息的存活时间，消息过期后会被指向(死信收容交换机)收入死信队列
            arguments["x-message-ttl"] = ttl

        self.declare_and_bind(
            dead_letter_exchange,
            dead_letter_queue,
            dead_letter_routing_key,
            exchange_type=dead_letter_exchange_type,
            auto_delete=dead_letter_auto_delete,
            durable=dead_letter_durable,
        )
        self.declare_and_bind(
            exchange,
            queue,
            routing_key,
            exchange_type=exchange_type,
            auto_delete=auto_delete,
            arguments=arguments,
            durable=durable,
        )

    @rabbitMQ_decorator
    def declare_and_bind_ttl_queue(
        self,
        exchange,
        queue,
        ttl=10000,
        routing_key="",
        exchange_type="direct",
        auto_delete=True,
        arguments=None,
        durable=False,
    ):
        assert exchange, "exchange is None!!!"
        assert queue, "queue is None!!!"
        assert ttl, "ttl is None!!!"
        arguments = {}
        arguments["x-message-ttl"] = ttl
        self.declare_and_bind(
            exchange,
            queue,
            routing_key,
            exchange_type=exchange_type,
            auto_delete=auto_delete,
            arguments=arguments,
            durable=durable,
        )

    @rabbitMQ_decorator
    def declare_exchange_and_queue(
        self, exchange, queue, exchange_type="direct", auto_delete=True, arguments=None, durable=False
    ):
        assert exchange, "exchange is None!!!"
        assert queue, "queue is None!!!"
        self.channel.exchange_declare(exchange=exchange, exchange_type=exchange_type)
        self.channel.queue_declare(queue=queue, auto_delete=auto_delete, arguments=arguments, durable=durable)

    @rabbitMQ_decorator
    def declare_and_bind(
        self, exchange, queue, routing_key="", exchange_type="direct", auto_delete=True, arguments=None, durable=False
    ):
        self.declare_exchange_and_queue(
            exchange, queue, exchange_type=exchange_type, auto_delete=auto_delete, arguments=arguments, durable=durable
        )
        self.channel.queue_bind(queue, exchange, routing_key)


class Producter(RabbitMQ):
    @rabbitMQ_decorator
    def basic_publish(self, exchange, routing_key, body):
        body = json.dumps(body) if isinstance(body, dict) or isinstance(body, list) else body
        self.channel.basic_publish(exchange=exchange, routing_key=routing_key, body=body)


class Consumer(RabbitMQ):
    # 定义一个回调函数来处理消息队列中的消息，这里是打印出来
    @rabbitMQ_decorator
    def callback(self, ch, method, properties, body):
        try:
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            pass

    @rabbitMQ_decorator
    def start_consume(
        self, queue, on_message_callback, auto_ack=False, exclusive=False, consumer_tag=None, arguments=None
    ):
        self.channel.basic_consume(
            queue,
            on_message_callback,
            auto_ack=auto_ack,
            exclusive=exclusive,
            consumer_tag=consumer_tag,
            arguments=arguments,
        )
        self.channel.start_consuming()
