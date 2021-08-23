# coding: utf-8
import pymysql
from dbutils.pooled_db import PooledDB, SharedDBConnection

import logging

logger = logging.getLogger(__name__)


class Mysql(object):
    """
    注意：insert，update，delete操作时需要commit
    """

    def __init__(self, db, host, port, user, pwd):
        self.db = pymysql.connect(host=host, port=port, user=str(user), password=str(pwd))
        self.cursor = self.db.cursor()
        self.current_db = db

    def __del__(self):
        self.cursor.close()
        self.db.close()

    def execute_sql(self, sql):
        try:
            self.db.ping(reconnect=True)
            self.db.select_db(self.current_db)
            sql = sql.lower()
            self.cursor.execute(sql)

            if sql.startswith(('insert', 'update', 'delete')):
                self.db.commit()
                return True
            elif sql.startswith('select'):
                return list(self.cursor.fetchall())
            else:
                self.db.commit()
                logger.error('未知sql类型'.format(sql))
                return False
        except Exception as e:
            logger.error('sql执行出错\nSQL: {} ,错误原因 {}'.format(sql, e), exc_info=True)
            return False

    def insert(self, tb, dt):
        """
        :param tb: 目标插入表
        :param dt: 字典型
        :return:
        """
        ls = [(k, dt[k]) for k in dt if dt[k] is not None]
        sql = 'insert %s (' % tb + ','.join(i[0] for i in ls) + \
              ') values (' + ','.join('%r' % i[1] for i in ls) + ');'
        self.execute_sql(sql)

    def select(self, tb, *columns, **factor):
        """
        :param tb: 目标插入表
        :param columns:select内容，空为全部
        :param factor: where内容

        example: self.select('arm_entry_services', asset_ip='192.168.90.26')
        """
        where = ''
        columns = '*' if columns == () or '' else ','.join(columns)

        if len(factor) > 0:
            where = 'where 1=1 '
            for column in factor:
                if factor[column] == '':
                    continue
                elif factor[column].startswith('like'):
                    conditional = 'and {} {}'.format(column, factor[column])
                else:
                    conditional = 'and {}={}'.format(column, "%r" % factor[column])
                if column == 'limit':
                    where += f'{column} {factor[column]}'
                else:
                    where += conditional + ' '

        sql = f'select {columns} from {tb} {where}'
        return self.execute_sql(sql)

    def update(self, tb, target_dic, set_dic):
        ts = [(k, target_dic[k]) for k in target_dic if target_dic[k] is not None]
        ss = [(k, set_dic[k]) for k in set_dic if set_dic[k] is not None]
        sql = 'UPDATE {} SET {} WHERE {}'.format(tb, ','.join([i[0] + '=' + '%r' % i[1] for i in ss]),
                                                 ' AND '.join([i[0] + '=' + '%r' % i[1] for i in ts]))
        self.execute_sql(sql)


class MysqlPool(object):
    """
    mysql连接池，用于处理多线程
    """

    def __init__(self, db, host, port, user, pwd, **kwargs):

        pool_config = {
            'creator': pymysql,  # 使用链接数据库的模块
            'maxconnections': 6,  # 连接池允许的最大连接数，0和None表示不限制连接数
            'mincached': 2,  # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
            'maxcached': 5,  # 链接池中最多闲置的链接，0和None不限制
            'maxshared': 3,
            # 链接池中最多共享的链接数量，0和None表示全部共享。PS: 无用，因为pymysql和MySQLdb等模块的 threadsafety都为1，所有值无论设置为多少，_maxcached永远为0，所以永远是所有链接都共享。
            'blocking': True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
            'maxusage': None,  # 一个链接最多被重复使用的次数，None表示无限制
            'setsession': [],  # 开始会话前执行的命令列表。如：["set datestyle to ...", "set time zone ..."]
            'ping': 1,
            # ping MySQL服务端，检查是否服务可用。# 如：0 = None = never, 1 = default = whenever it is requested, 2 = when a cursor is created, 4 = when a query is executed, 7 = always
            'host': host,
            'port': port,
            'user': user,
            'password': pwd,
            'database': db,
            'charset': 'utf8'
        }
        pool_config.update(**kwargs)

        self.pool = PooledDB(**pool_config)

    def __new__(cls, *args, **kw):
        '''
        启用单例模式
        :param args:
        :param kw:
        :return:
        '''
        if not hasattr(cls, '_instance'):
            cls._instance = object.__new__(cls)
        return cls._instance

    def __del__(self):
        try:
            self.pool.close()
        except Exception:
            pass

    def execute_sql(self, sql, **args):
        try:
            sql = sql.lower()
            conn, cursor = self.connect()
            cursor.execute(sql, args)

            if sql.startswith(('insert', 'update', 'delete')):
                conn.commit()
                self.connect_close(conn, cursor)
                return True
            elif sql.startswith('select'):
                record_list = cursor.fetchall()
                self.connect_close(conn, cursor)
                return record_list
            else:
                conn.commit()
                logger.error('未知sql类型'.format(sql))
                return False
        except Exception as e:
            logger.error('sql执行出错\nSQL: {} ,错误原因 {}'.format(sql, e), exc_info=True)
            return False

    def connect(self):
        '''
        启动连接
        :return:
        '''
        conn = self.pool.connection()
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        return conn, cursor

    def connect_close(self, conn, cursor):
        '''
        关闭连接
        :param conn:
        :param cursor:
        :return:
        '''
        cursor.close()
        conn.close()

    def select_all(self, sql, args):
        '''
        批量查询
        :param sql:
        :param args:
        :return:
        '''
        conn, cursor = self.connect()

        cursor.execute(sql, args)
        record_list = cursor.fetchall()
        self.connect_close(conn, cursor)

        return record_list

    def select_one(self, sql, args):
        '''
        查询单条数据
        :param sql:
        :param args:
        :return:
        '''
        conn, cursor = self.connect()
        cursor.execute(sql, args)
        result = cursor.fetchone()
        self.connect_close(conn, cursor)

        return result

    def execute(self, sql, args):
        """
        执行insert/delete/update操作
        :param sql:
        :param args:
        :return:
        """
        conn, cursor = self.connect()
        row = cursor.execute(sql, args)
        conn.commit()
        self.connect_close(conn, cursor)
        return row


class TaskMysql(MysqlPool, Mysql):
    def __init__(self, db, host, port, user, pwd, **kwargs):
        super().__init__(db=str(db), host=host, port=port,
                         user=str(user), pwd=str(pwd), **kwargs)
