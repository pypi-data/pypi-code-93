from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from ...wrapper.cas.cas_connection import CassandraConnector
from ...wrapper.cas.constants import CAS_KEY_SPACE

CassandraConnector().get_conn()


class TagMethodIndexLevel(Model):
    __table_name__ = 'tag_method_index_level'
    __keyspace__ = CAS_KEY_SPACE
    __connection__ = 'surfing'

    index_id = columns.Text(primary_key=True)                       # 指数ID
    data = columns.List(columns.Map(columns.Text, columns.Text))    # 数据
    update_time = columns.DateTime()                                # 更新时间

    def to_dict(self):
        return {
            'index_id': self.index_id,
            'data': self.data,
            'update_time': self.update_time,
        }


