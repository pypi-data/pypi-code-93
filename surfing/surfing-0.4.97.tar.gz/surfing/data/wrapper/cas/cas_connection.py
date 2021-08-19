from cassandra.cluster import Cluster
from cassandra.cqlengine import connection
from cassandra.auth import PlainTextAuthProvider
from ....util.config import SurfingConfigurator
from ....util.singleton import Singleton


class CassandraConnector(metaclass=Singleton):

    def __init__(self):
        self.conf = SurfingConfigurator().get_cassandra_setting()
        self.session = None
        self.connection = None

    def init_conn(self):
        if not self.session or not self.connection:
            auth_provider = PlainTextAuthProvider(
                username=self.conf.username,
                password=self.conf.password,
            )
            cluster = Cluster(
                self.conf.hosts,
                auth_provider=auth_provider,
            )
            self.session = cluster.connect()
            self.connection = connection.register_connection('surfing', session=self.session)
            # self.connection = connection.register_connection('', session=self.session, default=True)

    def get_conn(self):
        self.init_conn()
        return self.connection

    def get_session(self):
        self.init_conn()
        return self.session
