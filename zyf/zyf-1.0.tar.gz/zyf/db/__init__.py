# -*- coding: utf-8 -*-
"""
Author     : ZhangYafei
Description:
"""
import json

import pandas as pd
from dbutils.pooled_db import PooledDB


class DBPoolHelper(object):
    def __init__(self, dbname, user=None, password=None, db_type='postgressql', host='localhost', port=5432):
        """
        # sqlite3
        # 连接数据库文件名，sqlite不支持加密，不使用用户名和密码
        import sqlite3
        config = {"datanase": "path/to/your/dbname.db"}
        pool = PooledDB(sqlite3, maxcached=50, maxconnections=1000, maxusage=1000, **config)
        # mysql
        import pymysql
        pool = PooledDB(pymysql,5,host='localhost', user='root',passwd='pwd',db='myDB',port=3306) #5为连接池里的最少连接数
        # postgressql
        import psycopg2
        POOL = PooledDB(creator=psycopg2, host="127.0.0.1", port="5342", user, password, database)
        # sqlserver
        import pymssql
        pool = PooledDB(creator=pymssql, host=host, port=port, user=user, password=password, database=database, charset="utf8")
        :param type:
        """
        if db_type == 'postgressql':
            import psycopg2
            pool = PooledDB(creator=psycopg2, host=host, port=port, user=user, password=password, database=dbname)
        elif db_type == 'mysql':
            import pymysql
            pool = PooledDB(pymysql, 5, host='localhost', user='root', passwd='pwd', db='myDB',
                            port=3306)  # 5为连接池里的最少连接数
        elif db_type == 'sqlite':
            import sqlite3
            config = {"database": dbname}
            pool = PooledDB(sqlite3, maxcached=50, maxconnections=1000, maxusage=1000, **config)
        else:
            raise Exception('请输入正确的数据库类型, db_type="postgresql" or db_type="mysql" or db_type="sqlite"')
        self.__conn = pool.connection()
        self.__cursor = self.__conn.cursor()

    def __connect_close(self):
        """关闭连接"""
        self.__cursor.close()
        self.__conn.close()

    def commit(self):
        self.__conn.commit()

    def execute_without_commit(self, sql, params=tuple()):
        self.__cursor.execute(sql, params)

    def execute(self, sql, params=tuple()):
        self.__cursor.execute(sql, params)
        self.__conn.commit()

    def execute_many(self, sql, params=tuple()):
        self.__cursor.executemany(sql, params)
        self.__conn.commit()

    def fetchone(self, sql, params=tuple()):
        self.__cursor.execute(sql, params)
        data = self.__cursor.fetchone()
        return data

    def fetchall(self, sql, params=tuple()):
        self.__cursor.execute(sql, params)
        data = self.__cursor.fetchall()
        return data

    def __del__(self):
        self.__connect_close()


class MongoHelper(object):
    """
    mongodb:
        save(self, data, collection):                    将数据保存到数据库
        read(self, data):                                读取数据库中指定表格
        insert(self, table, dict_data)：                 插入数据
        delete(self, table, condition)：                 删除指定数据
        update(self, table, condition, new_dict_data)：  更新指定数据
        dbFind(self, table, condition=None):             按条件查找
        findAll(self, table)：                           查找全部
        close(self)：                                    关闭连接
    """

    def __init__(self, mongo_db, mongo_uri='localhost'):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        import pymongo
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close(self):
        """
        关闭连接
        :return:
        """
        self.client.close()

    def save(self, data, collection):
        """
        将数据保存到数据库表
        :param data:
        :param collection:
        :return: None
        """
        self.collection = self.db[collection]
        try:
            if self.collection.insert(json.loads(data.T.to_json()).values()):
                print('mongodb insert {} sucess.'.format(collection))
                return
        except Exception as e:
            print('insert error:', e)
            import traceback
            traceback.print_exc(e)

    def read(self, table):
        """
        读取数据库中的数据
        :param table:
        :return: dataframe
        """
        try:
            # 连接数据库
            table = self.db[table]
            # 读取数据
            data = pd.DataFrame(list(table.find()))
            return data
        except Exception as e:
            import traceback
            traceback.print_exc(e)

    def insert(self, table, dict_data):
        """
        插入
        :param table:
        :param dict_data:
        :return: None
        """
        try:
            self.db[table].insert(dict_data)
            print("插入成功")
        except Exception as e:
            print(e)

    def update(self,table, condition, new_dict_data):
        """
        更新
        :param table:
        :param dict_data:
        :param new_dict_data:
        :return: None
        """
        try:
            self.db[table].update(condition, new_dict_data)
            print("更新成功")
        except Exception as e:
            print(e)

    def delete(self,table, condition):
        """
        删除
        :param table:
        :param dict_data:
        :return: None
        """
        try:
            self.db[table].remove(condition)
            print("删除成功")
        except Exception as e:
            print(e)

    def dbFind(self, table, condition=None):
        """
        按条件查找
        :param table:
        :param dict_data:
        :return: generator dict
        """
        data = self.db[table].find(condition)
        for item in data:
            yield item

    def findAll(self, table):
        """
        查找全部
        :param table:
        :return: generator dict
        """
        for item in self.db[table].find():
            yield item