from abc import abstractmethod
from pynecone import ModuleProvider, ProtoShell


class TopicProvider(ModuleProvider):

    @abstractmethod
    def get_consumer(self):
        pass

    @abstractmethod
    def get_producer(self):
        pass


class ConsumerProvider(ModuleProvider):

    @abstractmethod
    def consume(self, args):
        pass


class ProducerProvider(ModuleProvider):

    @abstractmethod
    def produce(self, message):
        pass


class TaskProvider(ModuleProvider):

    @abstractmethod
    def run(self, *args, **kwargs):
        pass


class Topic(ProtoShell):

    def __init__(self):
        super().__init__('topic', [], 'manage topics')