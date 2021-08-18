# coding=utf-8
from sqlalchemy import Column, String, create_engine
from sqlalchemy.dialects.postgresql import DATE
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
# from importlib import reload
from datetime import *
# import sys
# reload(sys)
# sys.setdefaultencoding("utf-8")

# 创建对象的基类:
Base = declarative_base()

engine_template = '{dialect}+{driver}://{user}:{pwd}@{host}:{port}/{db}'


class SQLAlchemyHelper(object):

    @staticmethod
    def create_pg_engine(driver='psycopg2', user='', pwd='', host='localhost', port='5432', db=''):
        engine_str = engine_template % ('postgresql', driver, user, pwd, host, port, db)
        return create_engine(
            engine_str,
            client_encoding='utf8',
            echo=True  # 是不是要把所执行的SQL打印出来，一般用于调试
            # pool_size=int(config.SQLALCHEMY_POOL_SIZE),  # 连接池大小
            # max_overflow=int(config.SQLALCHEMY_POOL_MAX_SIZE),  # 连接池最大的大小
            # pool_recycle=int(config.SQLALCHEMY_POOL_RECYCLE),  # 多久时间主动回收连接，见下注释
        )

    @staticmethod
    def create_pg_psycopg2_engine(user='', pwd='', host='localhost', port='5432', db=''):
        return SQLAlchemyHelper.create_pg_engine(user=user, pwd=pwd, host=host, port=port, db=db)


class SQLAlchemyBaseDAL(object):

    engine = None

    def __init__(self, **kwargs):

        user = kwargs.get('user')
        pwd = kwargs.get('pwd')
        host = kwargs.get('host')
        port = kwargs.get('port')
        db = kwargs.get('db')

        # self.engine = SQLAlchemyHelper.create_pg_psycopg2_engine(user, pwd, host, port, db)
