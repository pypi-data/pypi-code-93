# -*- coding: utf-8 -*-
# @Time : 2021-04-21 09:22
# @Author : xzr
# @File : server_connect.py
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc :

from framework.connections import connections


class ServerConnect(object):
    """服务器连接"""

    ServerModel = None

    @classmethod
    def get_conn(cls, server_conn_id):
        server_conn_id = int(server_conn_id)
        if server_conn_id != 0:
            server_id = server_conn_id
            server_model = cls.ServerModel.objects.get(id=server_conn_id)
        else:
            conn = connections['read']
        return conn
