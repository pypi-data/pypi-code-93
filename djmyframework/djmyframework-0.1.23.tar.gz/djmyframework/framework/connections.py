# -*- coding: utf-8 -*-
# @Time    : 2020-06-15 15:50
# @Author  : xzr
# @File    : connections
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc    : 

from django.utils.translation import gettext_lazy as _
from django.db import connection, connections
import settings
import MySQLdb
from .utils import trace_msg

CENTER_CONN = None


def get_center_conn(alias='default'):
    '''获取中央服的mysql连接
    '''
    global CENTER_CONN
    try:
        CENTER_CONN.ping()
    except:
        db_cfg = settings.DATABASES.get(alias, {})
        if db_cfg:
            conf_cfg = {"host": db_cfg.get('HOST'),
                        "user": db_cfg.get('USER'),
                        "passwd": db_cfg.get('PASSWORD'),
                        "port": int(db_cfg.get('PORT', 3306)),
                        "db": db_cfg.get('NAME'),
                        "charset": 'utf8'
                        }
            CENTER_CONN = MySQLdb.connect(**conf_cfg)
    return CENTER_CONN


def get_conn(databases='default', connect_timeout=10):
    the_conn = None
    try:
        the_conn_str = settings.DATABASES.get(databases, {})
        the_conn = MySQLdb.connect(host=the_conn_str['HOST'], user=the_conn_str['USER'],
                                   passwd=the_conn_str['PASSWORD'], port=int(the_conn_str.get('PORT', 3306)),
                                   db=the_conn_str['NAME'], charset='utf8', connect_timeout=connect_timeout)
        the_conn.autocommit(1)
    except Exception as e:
        print(trace_msg())
        raise e
    return the_conn