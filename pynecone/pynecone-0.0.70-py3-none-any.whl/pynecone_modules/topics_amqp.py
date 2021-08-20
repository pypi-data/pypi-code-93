import pika
from pynecone import BrokerProvider, TopicProvider, ConsumerProvider, ProducerProvider, TaskCmd


class AMQPConsumer(ConsumerProvider):

    def __init__(self, cfg, name):
        self.cfg = cfg
        self.name = name

    def consume(self, args):
        credentials = pika.PlainCredentials(self.cfg['client_key'],
                                            self.cfg['client_secret'])
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(self.cfg['host'],
                                      self.cfg['port'],
                                      self.cfg['path'],
                                      credentials))
        channel = connection.channel()
        channel.queue_declare(queue=self.name)
        channel.basic_consume(queue=self.name,
                              on_message_callback=self.callback(args))
        channel.start_consuming()

    @classmethod
    def callback(cls, args):
        return lambda channel, method, properties, body: TaskCmd.get_handler(args.script,
                                                                             args.method)({'channel': channel,
                                                                                        'method': method,
                                                                                        'properties': properties,
                                                                                        'body': body,
                                                                                        'args': args})


class AMQPProducer(ProducerProvider):

    def __init__(self, cfg, name):
        self.cfg = cfg
        self.name = name

    def produce(self, message):
        credentials = pika.PlainCredentials(self.cfg['client_key'],
                                            self.cfg['client_secret'])
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(self.cfg['host'],
                                      self.cfg['port'],
                                      self.cfg['path'],
                                      credentials))
        connection.channel().basic_publish(exchange=self.cfg['exchange'],
                                           routing_key=self.name,
                                           body=message)


class AMQPTopic(TopicProvider):

    def __init__(self, cfg, name):
        self.cfg = cfg
        self.name = name

    def get_consumer(self):
        return AMQPConsumer(self.cfg, self.name)

    def get_producer(self):
        return AMQPProducer(self.cfg, self.name)


class Module(BrokerProvider):

    def __init__(self, **kwargs):
        self.cfg = kwargs

    def get_topic(self, name):
        return AMQPTopic(self.cfg, name)

