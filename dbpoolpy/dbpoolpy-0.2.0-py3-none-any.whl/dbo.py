import os
import time
import abc
import datetime
import traceback
from .utils import DBFunc
from .utils import timesql
from . import pager
from contextlib import contextmanager
from typing import Union, List, Tuple, Dict

class BaseO:

    def field2sql(self, field:str):
        ''' 字段名解析
        情况：'id','a.id','id as i', 'a.id as ai'
        '''
        # return '`%s`' % field.strip().replace('.', '`.`').replace(' as ', '` as `')
        return field
    
    def fields2sql(self, fields:Union[str, List[str], Tuple[str]]):
        ''' 解析fields
        情况： 'id, a.name, imlf.phone as ip', 
               ['id', 'a.name', 'imlf.phone as ip'], 
               ('id', 'a.name', 'imlf.phone as ip')
        '''
        # if isinstance(fields, str):
        #     fields = fields.strip()
        #     if fields == '*':
        #         return fields
        #     fields = fields.split(',')
        # return ','.join([self.field2sql(field) for field in fields])
        if isinstance(fields, str):
            return fields
        else: 
            return ','.join(list(fields))


    def table2sql(self, table:str):
        ''' 字段名解析
        情况：'graphs','imlf.graphs','graphs as g', 'imlf.graphs as ig'
        '''
        return '`%s`' % table.strip().replace('.', '`.`').replace(' as ', '` as `')
    
    def tables2sql(self, tables:Union[str, List[str], Tuple[str]]):
        ''' 解析tables
        情况： 'graphs, imlf.nodes, imlf.graphs as ig', 
               ['graphs', 'imlf.nodes', 'imlf.graphs as ig'], 
               ('graphs', 'imlf.nodes', 'imlf.graphs as ig')
        '''
        if isinstance(tables, str):
            tables = tables.split(',')
        return ','.join([self.table2sql(table) for table in tables])
    
    def key2sql(self, k:str) -> str:
        ''' where中的key转sql语句
        情况：'name', 'a.name'
        '''
        return '`%s`' % k.strip().replace('.', '`.`')

    def value2sql(self, v):
        ''' where中value为非tuple时
        情况: 'value', 'value "name"'
        '''
        if isinstance(v, str):
            return "'%s'" % self._dbo.escape(v)
        elif isinstance(v, (int, float)):
            return str(v)
        elif v == None:
            return 'NULL'
        else:
            return "'%s'" % str(v)

    def where_value_tuple2sql(self, v:tuple) -> str:
        ''' where中value为tuple时
        情况：('in', ['12', 1])
              ('not in', ['12', 1])
              ('between', ['time1', 'time2'])
              ('like', '%time1%')
              ('like', 'time1%')
        '''
        assert len(v) == 2
        op, item = v
        assert isinstance(op, str)
        op = op.strip()
        if op.endswith('in'):
            assert isinstance(item, (list, tuple, set))
            return op + ' (%s)' % ','.join([self.value2sql(x) for x in item])
        elif op == 'between':
            assert isinstance(item, (list, tuple, set)) and len(item) == 2
            return op + ' %s and %s' % (self.value2sql(item[0]), self.value2sql(item[1]))
        else:
            assert isinstance(item, str)
            return op + ' %s' % self.value2sql(item)

    def where2sql(self, where:dict):
        '''where值解析'''
        kv = lambda k,v: self.key2sql(k)+' '+self.where_value_tuple2sql(v) \
            if isinstance(v, tuple) else self.key2sql(k)+'='+self.value2sql(v)
        return ' and '.join([kv(k, v) for k, v in where.items()])

    def on2sql(self, where:Dict[str, str]):
        '''where值解析'''
        kv = lambda k,v: self.key2sql(k)+'='+self.key2sql(v)
        return ' and '.join([kv(k, v) for k, v in where.items()])

    def values2sql(self, values:dict):
        '''values值解析'''
        kv = lambda k, v:self.key2sql(k)+'='+self.value2sql(v)
        return ','.join([kv(k, v) for k, v in values.items()])

    def other2sql(self, other:Union[tuple, str]):
        if isinstance(other, str):
            return other
        else:
            assert len(other) == 2
            op, item = other
            assert isinstance(op, str)
            op = op.strip()
            if op.endswith('limit'):
                if isinstance(item, int):
                    return op + ' %s' % item
                else:
                    assert isinstance(item, (list, tuple, set)) and len(item) == 2
                    return op+' %s,%s' % (tuple(item))
            elif op == 'order by':
                if isinstance(item, str):
                    return op+' %s' % self.key2sql(item)
                else:
                    assert isinstance(item, (list, tuple, set)) and len(item) == 2
                    assert item[-1] in ['asc', 'desc']
                    return op+ ' %s %s' % (self.key2sql(item[0]), item[1])
            elif op == 'group by':
                if isinstance(item, str):
                    return op+' %s' % self.key2sql(item)
                else:
                    assert isinstance(item, (list, tuple, set))
                    return op+' %s' % ','.join([self.key2sql(i) for i in item])
            elif op == 'sql':
                assert isinstance(item, str)
                return item
    
    def values2insert(self, values:dict) -> str:
        '''insert中的values转sql'''
        keys = list(values.keys())
        return '(%s) values (%s)' % (
            ','.join([self.key2sql(k) for k in keys]), 
            ','.join([self.value2sql(values[k]) for k in keys])
        )

    def valueslist2insert(self, values_list:List[dict]) -> str:
        '''批量insert转sql'''
        keys = list(values_list[0].keys())
        return '(%s) values (%s)' % (
            ','.join([self.key2sql(k) for k in keys]),
            '),('.join(
                [','.join([self.value2sql(values[k]) for k in keys]) for values in values_list]
            )
        )
        
class WhereMixin:
    def where(self, **kwargs):
        self._where = kwargs
        return self

class ValuesMixin:
    def values(self, **kwargs):
        self._values = kwargs
        return self

class OtherMixin:
    def other(self, other):
        self._other = other
        return self


class SelectO(BaseO, WhereMixin, OtherMixin):
    def __init__(
        self, 
        dbo,
        tables, 
        fields='*', 
        join_type='inner',
        join_table=None,
        on=None,
        where=None, 
        group_by=None, 
        order_by=None, 
        limit=None, 
        other=None):
        self._dbo = dbo
        self._tables = tables
        self._fields = fields
        self._join_type = join_type
        self._join_table = join_table
        self._on = on
        self._where = where
        self._group_by = group_by
        self._order_by = order_by
        self._limit = limit
        self._other = other


    def sql(self):
        sql = "select %s from %s" % (
            self.fields2sql(self._fields), 
            self.tables2sql(self._tables)
        )
        if self._join_table and self._on:
            sql += " %s join %s on %s" % (
                self._join_type,
                self.table2sql(self._join_table),
                self.on2sql(self._on)
            )
        if self._where:
            sql += " where %s" % self.where2sql(self._where)
        if self._group_by:
            sql += " group by %s" % self.fields2sql(self._group_by)
        if self._order_by:
            sql += " order by %s" % self.fields2sql(self._order_by)
        if self._limit:
            sql += " limit %s" % self.fields2sql(self._limit)
        if self._other:
            sql += ' %s' % self.other2sql(self._other)
        return sql

    def fields(self, *args):
        self._fields = args
        return self

    def join(self, table, on, join_type=None):
        assert isinstance(on, dict), "'on' must be dict"
        self._on = on
        self._join_table = table
        if join_type:
            self._join_type = join_type
        return self
    
    def left_join(self, table, on):
        return self.join(table, on, join_type='left')

    def right_join(self, table, on):
        return self.join(table, on, join_type='right')

    def group_by(self, *args):
        self._group_by = args
        return self

    def order_by(self, *args):
        assert len(args) <= 2, "'order_by' accept 1 or 2 parameters"
        self._order_by = args
        return self

    def limit(self, *args):
        assert len(args) <= 2, "'limit' accept 1 or 2 parameters"
        self._limit = (str(i) for i in args)
        return self

    def all(self, isdict=True):
        sql = self.sql()
        return self._dbo.query(sql, None, isdict=isdict)

    def first(self, isdict=True):
        sql = self.sql()
        if sql.find('limit') == -1:
            sql += ' limit 1'
        return self._dbo.get(sql, None, isdict=isdict)


class InsertO(BaseO, ValuesMixin, OtherMixin):
    def __init__(self, dbo, table, values=None, many=None, other=None):
        self._dbo = dbo
        self._table = table
        self._values = values
        self._many = many
        self._other = other
    
    def many(self, _dict_list):
        self._many = _dict_list
        return self

    def sql(self):
        assert not (self._values and self._many), \
            "'values' and 'many' cannot exist at the same time"
        assert self._values or self._many, \
            "'values' or 'many' must be used"
        sql = 'insert into %s %s' % (
            self.table2sql(self._table), 
            self.values2insert(self._values) if self._values else self.valueslist2insert(self._many)
            )
        if self._other:
            sql += ' %s' % self.other2sql(self._other)
        return sql
    
    def execute(self):
        sql = self.sql()
        self._dbo.execute(sql)
    
    def from_select(self):
        # TODO
        return self


class UpdateO(BaseO, WhereMixin, ValuesMixin, OtherMixin):
    def __init__(self, dbo, table, where=None, values=None, other=None):
        self._dbo = dbo
        self._table = table
        self._where = where
        self._values = values
        self._other = other
    
    def sql(self):
        sql = 'update %s set %s' % (
            self.table2sql(self._table), 
            self.values2sql(self._values)
            )
        if self._where:
            sql += " where %s" % self.where2sql(self._where)
        if self._other:
            sql += ' %s' % self.other2sql(self._other)
        return sql

    def execute(self):
        sql = self.sql()
        self._dbo.execute(sql)

class DeleteO(BaseO, WhereMixin, OtherMixin):
    def __init__(self, dbo, table, where=None, other=None):
        self._dbo = dbo
        self._table = table
        self._where = where
        self._other= other

    def sql(self):
        sql = 'delete from %s' % self.table2sql(self._table)
        if self._where:
            sql += " where %s" % self.where2sql(self._where)
        if self._other:
            sql += ' %s' % self.other2sql(self._other)
        return sql

    def execute(self):
        sql = self.sql()
        self._dbo.execute(sql)

class DBO:
    def __init__(self):
        self._conn = None

    def format_timestamp(self, ret, cur):
        '''将字段以_time结尾的格式化成datetime'''
        if not ret:
            return ret
        index = []
        for d in cur.description:
            if d[0].endswith('_time'):
                index.append(cur.description.index(d))

        res = []
        for i, t in enumerate(ret):
            if i in index and isinstance(t, int):
                res.append(datetime.datetime.fromtimestamp(t))
            else:
                res.append(t)
        return res

    #执行命令
    @timesql
    def execute(self, sql, param=None):
        '''执行单个sql命令'''
        with self.connect_cur() as cur:
            if param:
                if not isinstance(param, (dict, tuple, set)):
                    param = tuple([param])
                ret = cur.execute(sql, param)
            else:
                ret = cur.execute(sql)
            return ret

    @timesql
    def executemany(self, sql, param):
        '''调用executemany执行多条命令'''
        with self.connect_cur() as cur:
            if param:
                if not isinstance(param, (dict, tuple, set)):
                    param = tuple([param])
                ret = cur.executemany(sql, param)
            else:
                ret = cur.executemany(sql)
            return ret

    @timesql
    def query(self, sql, param=None, isdict=True, hashead=False):
        '''sql查询，返回查询结果
        sql: 要执行的sql语句
        param: 要传入的参数
        isdict: 返回值格式是否为dict, 默认True
        hashead: 如果isdict为Fasle, 返回的列表中是否包含列标题
        '''
        with self.connect_cur() as cur:
            if not param:
                cur.execute(sql)
            else:
                if not isinstance(param, (dict, tuple, set)):
                    param = tuple([param])
                cur.execute(sql, param)
            res = cur.fetchall()
            res = [self.format_timestamp(r, cur) for r in res]
            if res and isdict:
                ret = []
                xkeys = [i[0] for i in cur.description]
                for item in res:
                    ret.append(dict(zip(xkeys, item)))
            else:
                ret = res
                if hashead:
                    xkeys = [i[0] for i in cur.description]
                    ret.insert(0, xkeys)
            return ret

    @timesql
    def get(self, sql, param=None, isdict=True):
        '''sql查询，只返回一条
        sql: sql语句
        param: 传参
        isdict: 返回值是否是dict
        '''
        with self.connect_cur() as cur:
            if param:
                if not isinstance(param, (dict, tuple, set)):
                    param = tuple([param])
                cur.execute(sql, param)
            else:
                cur.execute(sql)
            res = cur.fetchone()
            res = self.format_timestamp(res, cur)
            if res and isdict:
                xkeys = [i[0] for i in cur.description]
                return dict(zip(xkeys, res))
            else:
                return res

    def escape(self, s):
        return s

    def select(self, tables, **kwargs):
        return SelectO(self, tables, **kwargs)

    def insert(self, table, **kwargs):
        return InsertO(self, table, **kwargs)

    def update(self, table, **kwargs):
        return UpdateO(self, table, **kwargs)

    def delete(self, table, **kwargs):
        return DeleteO(self, table, **kwargs)

    @abc.abstractmethod
    @contextmanager
    def connect_cur(self):
        cur = None
        try:
            yield cur
        except:
            pass
        finally:
            pass

    def select_page(self, sql, pagecur=1, pagesize=20, count_sql=None, maxid=-1, isdict=True):
        page = pager.db_pager(self, sql, pagecur, pagesize, count_sql, maxid)
        if isdict:
            page.todict()
        else:
            page.tolist()
        return page

class TestPool():
    def __init__(self):
        self._idle_cache = []
        self._idle_using = []
        self._maxconnections = 10

class SimpleDBOConnection(DBO):

    type='simpledbo'

    def __init__(self, engine, *args, **kwargs):
        self._conn = None
        self._name = 'simple'
        self.pool = TestPool()
        self._args, self._kwargs = args, kwargs
        try:
            self._engine = engine.connect
        except Exception as e:
            raise Exception('数据库连接器不可用')
        self._conn = self._engine(*self._args, **self._kwargs)
        # 记录连接的数据库信息
        self._server_id = None
        self._conn_id = 0
        self.conn_info()
        self._transaction = 0

    def __enter__(self):
        """Enter the runtime context for the connection object."""
        return self

    def __exit__(self, *exc):
        """Exit the runtime context for the connection object.
        This does not close the connection, but it ends a transaction.
        """
        if exc[0] is None and exc[1] is None and exc[2] is None:
            self.commit()
        else:
            self.rollback()

    def conn_info(self):
        """获取数据库连接信息，便于问题追踪"""
        cur = self._conn.cursor()
        cur.execute("show variables like 'server_id'")
        row = cur.fetchone()
        self._server_id = int(row[1])
        cur.close()

        cur = self._conn.cursor()
        cur.execute("select connection_id()")
        row = cur.fetchone()
        self._conn_id = row[0]
        cur.close()


    def cursor(self, *args, **kwargs):
        return self._conn.cursor(*args, **kwargs)

    def close(self):
        self._conn.close()

    def begin(self, *args, **kwargs):
        begin = self._conn.begin
        begin(*args, **kwargs)

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def cancel(self):
        cancel = self._conn.cancel
        cancel()

    def ping(self, *args, **kwargs):
        return self._conn.ping(*args, **kwargs)
    
    def escape(self, s):
        return self._conn.escape_string(s)

    @contextmanager
    def connect_cur(self):
        cur = None
        try:
            cur = self.cursor()
            yield cur
            self.commit()
        except Exception as e:
            self.rollback()
            raise e
        finally:
            if cur is not None:
                cur.close()
