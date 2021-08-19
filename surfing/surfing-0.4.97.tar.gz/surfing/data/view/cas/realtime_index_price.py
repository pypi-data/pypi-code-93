from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from ...wrapper.cas.cas_connection import CassandraConnector
from ...wrapper.cas.constants import CAS_KEY_SPACE

CassandraConnector().get_conn()

class RealtimeIndexPrice(Model):
    __table_name__ = 'realtime_index_price'
    __keyspace__ = CAS_KEY_SPACE
    __connection__ = 'surfing'

    index_id = columns.Text(primary_key=True)           # 指数ID
    timestamps = columns.List(columns.DateTime())       # 数据时间
    prices = columns.List(columns.Double)               # 指数点位


    def to_dict(self):
        return {
            'index_id': self.index_id,
            'timestamps': self.timestamps,
            'prices': self.prices
        }


