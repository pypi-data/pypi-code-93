# -*- encoding:utf-8 -*-
import pandas as pd
import json
import redis
import datetime
from dateutil import tz

UTC = tz.gettz('UTC')
BJ = tz.gettz('Asia/Shanghai')
ET = tz.gettz('America/New_York')


class RedisObject(object):
    def __init__(self, host, port):
        pool = redis.ConnectionPool(host=host, port=port)
        self.rds = redis.Redis(connection_pool=pool)

    def hash_to_dataframe_new(self, key, redis_timestamp_tz=None, local_tz=None,
                              columns=None, start_time=None, end_time=None, is_trans_time=True):

        if not columns:
            columns = ['tradeTime', 'open', 'close', 'high', 'low', 'volume']

        res_dict = self.rds.hgetall(key)
        # columns.remove('tradeTime')
        if 'tradeTime' in columns:
            datetime_list = json.loads(res_dict[b'tradeTime'])
            if is_trans_time:
                if not redis_timestamp_tz:
                    datetime_list = list(
                        map(lambda x: datetime.datetime.utcfromtimestamp(x),
                            datetime_list))
                else:
                    datetime_list = list(
                        map(lambda x: datetime.datetime.fromtimestamp(x, tz=redis_timestamp_tz).astimezone(local_tz),
                            datetime_list))
        else:
            raise Exception('`tradeTime` not in columns')

        pd_dict = dict()
        for column in columns:
            if column == 'tradeTime':
                pd_dict.update({column: datetime_list})
            else:
                pd_dict.update({column: json.loads(res_dict[bytes(column, encoding='utf-8')])})
        if 'tradeTime' in columns:
            df = pd.DataFrame(pd_dict, index=datetime_list)
        else:
            df = pd.DataFrame(pd_dict)

        if not redis_timestamp_tz:
            if start_time:
                start_time = start_time.replace(tzinfo=None)
            if end_time:
                end_time = end_time.replace(tzinfo=None)
        else:
            if start_time:
                start_time = start_time.replace(tzinfo=local_tz)
            if end_time:
                end_time = end_time.replace(tzinfo=local_tz)
        if not start_time and not end_time:
            pass
        elif start_time and end_time:
            df = df.loc[(df.index >= start_time) & (df.index <= end_time)]
        elif start_time and not end_time:
            df = df.loc[df.index >= start_time]
        else:
            df = df.loc[df.index <= end_time]
        return df

    def get_dataframe_from_redis(self, key, fromdate=datetime.datetime(1970, 2, 1, tzinfo=ET),
                                 todate=datetime.datetime.now().astimezone(tz=ET), ktype='d1', columns=None,
                                 redis_timestamp_tz=None,
                                 local_tz=ET
                                 ):
        """
        根据tickerId获取指定时间段内、指定列的df
        :param key: str
        :param fromdate: datetime
        :param todate: datetime
        :param ktype: str
        :param columns: list, list of str
        :param redis_timestamp_tz: dateutil.tz
        :param local_tz: dateutil.tz
        :return: df
        """
        f_stamp = fromdate.timestamp()
        t_stamp = todate.timestamp()
        pattern = f'*{ktype}*'

        if ':' not in key:
            match_list = self.rds.keys(pattern=pattern + f'{key}*')
            match_list = list(map(lambda i: str(i, encoding="utf-8"), match_list))
            filter_list = []
            for m in match_list:
                ml = m.split(':')
                stime, etime = int(float(ml[-3])), int(float(ml[-2]))
                if stime <= t_stamp and f_stamp <= etime:
                    filter_list.append(m)
            dataframe = []
            for key in filter_list:
                dataframe.append(self.hash_to_dataframe_new(key,
                                                            redis_timestamp_tz=redis_timestamp_tz,
                                                            local_tz=local_tz,
                                                            start_time=fromdate,
                                                            end_time=todate, columns=columns))
            if dataframe:
                copy_dataframe = dataframe.copy()
                for d, i in zip(copy_dataframe, range(len(copy_dataframe))):
                    if d.empty:
                        del dataframe[i]
            if dataframe:
                dataname = pd.concat(dataframe)
                dataname = dataname.sort_values(by="tradeTime", ascending=True)
            else:
                dataname = pd.DataFrame()

        else:
            dataname = self.hash_to_dataframe_new(key,
                                                  redis_timestamp_tz=redis_timestamp_tz,
                                                  local_tz=local_tz,
                                                  )
        return dataname
