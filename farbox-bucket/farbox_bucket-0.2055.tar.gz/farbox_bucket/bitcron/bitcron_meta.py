# coding: utf8
import datetime
import requests
from requests.exceptions import ConnectionError

def get_bitcron_metas(token, prefix='', cursor=None, got=None, sync_list_url=None):
    """
    :param token: bitcron token
    :param prefix: 具体某个路径下，不用特殊指定
    :param cursor: cursor
    :param got: 存储数据的
    :param sync_list_url: list 的 api url
    :return:
    """
    # 做成一个递归的
    if cursor=='init': # 初始化
        cursor = None
    got = got or []
    if token:
        data = dict(token=token, prefix=prefix)
        if cursor:
            if isinstance(cursor, datetime.datetime):
                cursor = cursor.strftime('%s')
            cursor = str(cursor)
            data['cursor'] = cursor
        try:
            response = requests.post(sync_list_url, data=data)
        except ConnectionError: # 连接错误
            return None, []
        if response.status_code >= 400:
            return None, []
        try:
            cursor_got = response.json()['cursor']
            if isinstance(cursor_got, float):
                new_cursor = '%f' % cursor_got
            else:
                new_cursor = str(cursor_got)
        except:
            return None, []
        new_files = response.json()['files']
        got += new_files
        if new_cursor == cursor or not new_files: # break this function
            return new_cursor, got
        else:
            return get_bitcron_metas(token, prefix, new_cursor, got, sync_list_url)
    else: # 没有token，不处理
        return None, []

