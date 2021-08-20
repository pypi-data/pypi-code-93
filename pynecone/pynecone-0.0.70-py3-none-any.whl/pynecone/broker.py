from abc import abstractmethod
from pynecone import ProtoShell, ProtoCmd, ModuleProvider


class BrokerProvider(ModuleProvider):

    @abstractmethod
    def get_topic(self, name):
        pass


class Broker(ProtoShell):

    class Create(ProtoShell):

        def __init__(self):
            super().__init__('create', [], 'create a broker')

        def add_arguments(self, parser):
            parser.add_argument('name', help="specifies the name of the broker to be created")

    class List(ProtoCmd):

        def __init__(self):
            super().__init__('list',
                             'list brokers')

    class Delete(ProtoCmd):

        def __init__(self):
            super().__init__('delete',
                             'delete a broker')

        def add_arguments(self, parser):
            parser.add_argument('name', help="specifies the name of the broker to be deleted")

    class Get(ProtoCmd):

        def __init__(self):
            super().__init__('get',
                             'get broker')

        def add_arguments(self, parser):
            parser.add_argument('name', help="specifies the name of the broker to be retrieved")

    def __init__(self):
        super().__init__('broker', [Broker.Create(), Broker.List(), Broker.Delete(), Broker.Get()], 'broker shell')

