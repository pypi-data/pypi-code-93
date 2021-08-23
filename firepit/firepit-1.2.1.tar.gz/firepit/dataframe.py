from firepit import get_storage
from firepit.exceptions import UnknownViewname
from firepit.query import Aggregation
from firepit.query import Count
from firepit.query import CountUnique
from firepit.query import Filter
from firepit.query import Group
from firepit.query import InvalidComparisonOperator
from firepit.query import InvalidQuery
from firepit.query import Join
from firepit.query import Limit
from firepit.query import Offset
from firepit.query import Order
from firepit.query import Predicate
from firepit.query import Projection
from firepit.query import Query
from firepit.query import Table
from firepit.query import Unique


class Series:
    """Series interface to a SQL column"""
    def __init__(self, column, df):
        self.df = df
        self.column = column

    def _agg(self, op):
        query = Query()
        query.append(Table(self.df.table))
        query.append(Aggregation([(op, self.column, 'result')]))
        result = self.df.store.run_query(query).fetchall()
        return result[0]['result']
        
    def count(self):
        return self._agg('COUNT')

    def nunique(self):
        query = Query()
        query.append(Table(self.df.table))
        query.append(Projection([self.column]))
        query.append(CountUnique())
        result = self.df.store.run_query(query).fetchall()
        count = result[0]["count"]
        return count

    def min(self):
        return self._agg('MIN')

    def max(self):
        return self._agg('MAX')

    def sum(self):
        return self._agg('SUM')
    

class DataFrame:
    """DataFrame interface to a SQL table/view"""
    def __init__(self, table, store, session=None):
        if table not in store.views():
            raise UnknownViewname(table)
        self.table = table
        if isinstance(store, str):
            store = get_storage(store, session)
        self.store = store
        self.session = session

    def __getitem__(self, key):
        if key not in self.store.columns(self.table):
            raise KeyError(key)
        return Series(key, self)

    def __getattr__(self, attr):
        if attr == "columns":
            return self.store.columns(self.table)
        elif attr == "index":
            return range(self.store.count(self.table))
        elif attr == "shape":
            return (len(self.store.columns(self.table)),
                    self.store.count(self.table))
        #NOPE:super().__getattr__(attr)
