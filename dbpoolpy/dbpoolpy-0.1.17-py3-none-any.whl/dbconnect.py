#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
import traceback
from .utils import timeit
from .utils import log
from .conf import MYSQL_SSLKEY_PATH
from .dbhelper import DBHelper
from contextlib import contextmanager


def with_mysql_reconnect(func):
    def close_mysql_conn(self):
        try:
            self._conn.close()
        except:
            log.warning(traceback.format_exc())
            self._conn = None

    def _(self, *args, **argitems):
        trycount = 3
        while True:
            try:
                x = func(self, *args, **argitems)
            except self._engine.OperationalError as e:
                if e[0] >= 2000 and not self._transaction:  # 客户端错误
                    log.info(traceback.format_exc())
                    close_mysql_conn(self)
                    self._connect()
                    trycount -= 1
                    if trycount > 0:
                        continue
                log.warning(traceback.format_exc())
                raise
            except (self._engine.InterfaceError, self._engine.InternalError):
                log.warning(traceback.format_exc())
                if not self._transaction:
                    close_mysql_conn(self)
                    self._connect()
                    trycount -= 1
                    if trycount > 0:
                        continue
                raise
            else:
                return x
    return _


class DBConnection(object):
    pass

class MySQLConnection(DBHelper):
    type = "mysql"

    def __init__(self, name, engine, lasttime, status, role='master', *args, **kwargs):
        self._name = name                       # 连接池名称
        self._engine = engine                   # 数据库连接引擎，满足DB API 2.0规范
        self._args, self._kwargs = args, kwargs # 数据库连接所传参数
        self._conn = None                       # 连接存储位置
        self._status = status                   # 连接状态
        self._lasttime = lasttime               # 连接创建时间
        self._server_id = None                  # MySQL服务唯一id
        self._conn_id = 0                       # MySQL连接唯一id
        self._transaction = False               # 是否正在执行事务
        self._role = role                       # MySQL服务器在MySQL集群中的角色
        self.connect()

    def __str__(self):
        return '<%s %s:%d %s@%s>' % (
            self.type,
            self._kwargs.get('host', ''), 
            self._kwargs.get('port', 0),
            self._kwargs.get('user', ''), 
            self._kwargs.get('database', 0)
        )

    def connect(self):
        #  ssl = None
        #  key_path = os.path.join(MYSQL_SSLKEY_PATH, '{host}_{port}'.format(**{
        #      'host': self._param['host'], 'port': self._param['port']}))
        #  if os.path.exists(key_path):
        #      log.debug('IP:%s|PORT:%s|SSL=True|ssl_path:%s',
        #                  self._param['host'], self._param['port'], key_path)
        #      ssl = {
        #          'ssl': {
        #              'ca': os.path.join(key_path, 'ssl-ca'),
        #              'key': os.path.join(key_path, 'ssl-key'),
        #              'cert': os.path.join(key_path, 'ssl-cert'),
        #          }
        #      }
        self._conn = self._engine.connect(*self._args, **self._kwargs)
        self._conn.autocommit(1)
        self._transaction = False

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

        log.info('server=%s|func=connect|id=%d|name=%s|user=%s|role=%s|addr=%s:%d|db=%s',
                 self.type, self._conn_id % 10000,
                 self._name, self._kwargs.get('user', ''), self._role,
                 self._kwargs.get('host', ''), self._kwargs.get('port', 0),
                 self._kwargs.get('database', ''))

    def cursor(self, *args, **kwargs):
        return self._conn.cursor(*args, **kwargs)

    def close(self):
        log.info('server=%s|func=close|id=%d', self.type, self._conn_id % 10000)
        self._conn.close()
        self._conn = None
    
    def reconnect(self):
        '''重新连接'''
        try:
            self.close()
        except:
            pass
        self.connect()

    def begin(self, *args, **kwargs):
        self._transaction = True
        begin = self._conn.begin
        begin(*args, **kwargs)

    def commit(self):
        self._transaction = False
        self._conn.commit()

    def rollback(self):
        self._transaction = False
        self._conn.rollback()

    def cancel(self):
        cancel = self._conn.cancel
        cancel()

    def ping(self, *args, **kwargs):
        return self._conn.ping(*args, **kwargs)

    def escape(self, s):
        return self._conn.escape_string(s)

    def is_available(self):
        return self._status == 0

    def useit(self):
        self._status = 1
        self._lasttime = time.time()

    def releaseit(self):
        self._status = 0

    def alive(self):
        pass

    def last_insert_id(self):
        pass

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


    # @with_mysql_reconnect
    # def alive(self):
    #     if self.is_available():
    #         cur = self._conn.cursor()
    #         cur.execute("show tables;")
    #         cur.close()
    #         self._conn.ping()

    # def last_insert_id(self):
    #     ret = self.query('select last_insert_id()', isdict=False)
    #     return ret[0][0]

    # def start(self):
    #     self._transaction = True
    #     sql = "start transaction"
    #     return self.execute(sql)

    # def commit(self):
    #     self._transaction = False
    #     sql = 'commit'
    #     return self.execute(sql)

    # def rollback(self):
    #     self._transaction = False
    #     sql = 'rollback'
    #     return self.execute(sql)

#  class SQLiteConnection(DBConnection):
#      type = "sqlite"
#
#      def __init__(self, lasttime, status, *args, **kwargs):
#          DBConnection.__init__(self, lasttime, status, *args, **kwargs)
#
#      def connect(self):
#          self._transaction = False
#          self._conn = self._engine.connect(*args, **kwargs)
#
#      def useit(self):
#          DBConnection.useit(self)
#          if not self._conn:
#              self._connect()
#
#      def releaseit(self):
#          DBConnection.releaseit(self)
#          self._conn.close()
#          self._conn = None
#
#      def last_insert_id(self):
#          ret = self.query('select last_insert_rowid()', isdict=False)
#          return ret[0][0]
#
#      def start(self):
#          self._transaction = True
#          sql = "BEGIN"
#          return self._conn.execute(sql)
