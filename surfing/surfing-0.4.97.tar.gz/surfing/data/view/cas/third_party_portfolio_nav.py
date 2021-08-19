from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from ...wrapper.cas.cas_connection import CassandraConnector
from ...wrapper.cas.constants import CAS_KEY_SPACE

CassandraConnector().get_conn()


class ThirdPartyPortfolioNav(Model):

    __table_name__ = 'third_party_portfolio_nav'
    __keyspace__ = CAS_KEY_SPACE
    __connection__ = 'surfing'

    po_id = columns.Text(primary_key=True)  # 组合ID
    date = columns.List(columns.Text)  # 日期
    nav = columns.List(columns.Double)  # 组合净值

    def to_dict(self):
        return {
            'po_id': self.po_id,
            'date': self.date,
            'nav': self.nav,
        }
