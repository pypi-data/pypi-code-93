from kafka.admin import KafkaAdminClient, NewTopic
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import kafka_errors
import traceback
import json
import datetime
import calendar


def default(obj):
    if isinstance(obj, datetime.datetime):
        if obj.utcoffset() is not None:
            obj = obj - obj.utcoffset()
        return calendar.timegm(obj.timetuple()) + obj.microsecond / 1000000.0
    raise TypeError("%r is not JSON serializable" % obj)


class BaseKafka:
    def __init__(self, bootstrap_servers):
        """

        :param bootstrap_servers: 'host[:port]' string (or list of 'host[:port]' strings) that the consumer should contact to bootstrap initialcluster metadata. This does not have to be the full node list.It just needs to have at least one broker that will respond to a Metadata API Request. Default port is 9092. If no servers are specified, will default to localhost:9092.
        """
        self.bootstrap_servers = bootstrap_servers
        self.consumers = {}
        self.producers = {}
        self.group = {}
        self.started_consumers = []
        self.stopped_consumers = []

    def create_topics(self, topics: list):
        """

        :param topics:
        :return:
        """
        client = KafkaAdminClient(bootstrap_servers=self.bootstrap_servers)
        client.create_topics(new_topics=topics)

    @staticmethod
    def get_new_topic(name, num_partitions, **configs):
        return NewTopic(name=name, num_partitions=num_partitions, **configs)

    def create_consumer(self, topic, **kwargs):
        c = KafkaConsumer(
            topic,  # 指定消费者的消费的topic
            bootstrap_servers=self.bootstrap_servers,
            # group_id='group1',  # 确定消费者的group，一旦已经有一个有group的消费者消费，同group的消费者不会再消费这条数据 如果更改了group，则会从最新的offset开始消费
            key_deserializer=lambda v: v.decode(),
            value_deserializer=lambda v: json.loads(v),
            **kwargs)
        self.consumers[c.config['client_id']] = c
        return c

    def create_producer(self):
        p = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            key_serializer=str.encode,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'))  # Serialize json messages
        self.producers[p.config['client_id']] = p
        return p

    # def create_producer(self, indent):
    #     p = KafkaProducer(
    #         bootstrap_servers=self.bootstrap_servers,
    #         key_serializer=str.encode,
    #         value_serializer=lambda v: json.dumps(v, default=default, sort_keys=False,
    #                                               indent=indent, encoding="utf-8"))
    #     # Serialize json messages
    #     self.producers[p.config['client_id']] = p
    #     return p

    @staticmethod
    def use_consumer(consumer):
        for message in consumer:
            # TODO
            print("receive, key: {}, value: {}".format(message.key, message.value))

    @staticmethod
    def use_producer(producer, topic, dic):
        future = producer.send(
            topic,
            key='count_num',  # 同一个key值，会被送至同一个分区,可以不指定
            value=dic)
        # print("sending {}".format(dic))
        try:
            res = future.get(timeout=10)  # 监控是否发送成功
            return res

        except kafka_errors:  # 发送失败抛出kafka_errors
            traceback.format_exc()

    def get_one_producer(self, client_id=None):
        if client_id and client_id in self.producers:
            return self.producers[client_id]
        elif len(self.producers) != 0:
            return self.producers[list(self.producers)[0]]
        else:
            return self.create_producer()
