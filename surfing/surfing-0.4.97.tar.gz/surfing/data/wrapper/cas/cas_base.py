from .cas_connection import CassandraConnector
from cassandra import ConsistencyLevel

class CasClient:

    def __init__(self):
        self.session = CassandraConnector().get_session()
        self.conn = CassandraConnector().get_conn()

    def get_columns(self, model, columns):
        columns_format = '{},' * (len(columns) - 1) + '{}'
        columns_format = columns_format.format(*columns)

        cql = "SELECT {} from {}.{}".format(
            columns_format,
            model.__keyspace__,
            model.__table_name__,
        )
        return self.session.execute(cql)

    def get_columns_by_id(self, model, columns, id_column, id_value):
        columns_format = '{},' * (len(columns) - 1) + '{}'
        columns_format = columns_format.format(*columns)

        cql = "SELECT {} from {}.{} WHERE {}=?".format(
            columns_format,
            model.__keyspace__,
            model.__table_name__,
            id_column,
        )
        cql_lookup = self.session.prepare(cql)
        cql_lookup.consistency_level = ConsistencyLevel.ONE

        ret = self.session.execute(cql_lookup, [id_value])
        ret = [i for i in ret]
        if len(ret) < 1:
            return None

        return ret[0]

    def scan_columns_by_id(self, model, columns, id_column, id_value):
        columns_format = '{},' * (len(columns) - 1) + '{}'
        columns_format = columns_format.format(*columns)

        cql = "SELECT {} from {}.{} WHERE {}=?".format(
            columns_format,
            model.__keyspace__,
            model.__table_name__,
            id_column,
        )
        cql_lookup = self.session.prepare(cql)
        cql_lookup.consistency_level = ConsistencyLevel.ONE

        return [i for i in self.session.execute(cql_lookup, [id_value])]


    def get_columns_by_two_ids(self, model, columns, id_column, id_value, id_column2, id_value2):
        columns_format = '{},' * (len(columns) - 1) + '{}'
        columns_format = columns_format.format(*columns)

        cql = "SELECT {} from {}.{} WHERE {}=? AND {}=?".format(
            columns_format,
            model.__keyspace__,
            model.__table_name__,
            id_column,
            id_column2,
        )
        cql_lookup = self.session.prepare(cql)
        cql_lookup.consistency_level = ConsistencyLevel.ONE

        ret = self.session.execute(cql_lookup, [id_value, id_value2])
        ret = [i for i in ret]
        if len(ret) < 1:
            return None

        return ret[0]

    def truncate_table(self, model):
        cql = "TRUNCATE table {}.{}".format(
            model.__keyspace__,
            model.__table_name__
        )
        return self.session.execute(cql)





