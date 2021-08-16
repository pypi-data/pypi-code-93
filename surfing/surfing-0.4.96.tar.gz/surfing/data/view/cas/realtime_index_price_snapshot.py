from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from ...wrapper.cas.cas_connection import CassandraConnector
from ...wrapper.cas.constants import CAS_KEY_SPACE

CassandraConnector().get_conn()

class RealtimeIndexPriceSnapshot(Model):
    __table_name__ = 'realtime_index_price_snapshot'
    __keyspace__ = CAS_KEY_SPACE
    __connection__ = 'surfing'

    ts = columns.DateTime(primary_key=True)                   # 数据时间
    index_prices = columns.Map(columns.Text, columns.Double)         # 指数点位


    def to_dict(self):
        return {
            'ts': self.ts,
            'index_prices': self.index_prices
        }


