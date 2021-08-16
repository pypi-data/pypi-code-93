from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from ...wrapper.cas.cas_connection import CassandraConnector
from ...wrapper.cas.constants import CAS_KEY_SPACE

CassandraConnector().get_conn()

class FundEstimatedNav(Model):
    __table_name__ = 'fund_estimated_nav'
    __keyspace__ = CAS_KEY_SPACE
    __connection__ = 'surfing'

    fund_id = columns.Text(primary_key=True)            # 基金ID
    timestamps = columns.List(columns.DateTime())       # 预估数据时间
    unit_net_values = columns.List(columns.Double)      # 预估净值
    acc_net_values = columns.List(columns.Double)       # 预估累计净值
    adjusted_net_values = columns.List(columns.Double)  # 预估后复权净值

    def to_dict(self):
        return {
            'fund_id': self.fund_id,
            'timestamps': self.timestamps,
            'unit_net_values': self.unit_net_values,
            'acc_net_values': self.acc_net_values,
            'adjusted_net_values': self.adjusted_net_values
        }


