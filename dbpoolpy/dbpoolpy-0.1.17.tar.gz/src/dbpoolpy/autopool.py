# coding: utf-8
import traceback
from contextlib import contextmanager
from .utils import log
from .pooled_db import PooledDB
from .dbhelper import DBHelper

auto_pool = None

class PoolConnection(DBHelper):

    def __init__(self, **kwargs):
        self.pool = PooledDB(**kwargs)

    @contextmanager
    def connect_cur(self):
        cur = None
        try:
            conn, cur = self._conn_cur()
            yield cur
            conn.commit()
        except:
            conn.rollback()
            log.error("error=%s", traceback.format_exc())
        finally:
            if cur is not None:
                self.close_cur(cur, conn)

    def conn_cur(self):
        '''连接数据库，开启会话'''
        conn = self.pool.connection()
        cur = conn.cursor()
        return conn, cur

    def close_cur(self, cur, conn):
        '''关闭数据库，关闭会话'''
        cur.close()
        conn.close()

def init_auto_pool(db_conf):
    global auto_pool
    if auto_pool:
        return auto_pool
    auto_pool = {}
    for name, item in db_conf.items():
        auto_pool[name] = PoolConnection(**item)
    return auto_pool

def connect_auto_pool(name):
    global auto_pool
    pool = auto_pool[name]
    return pool
