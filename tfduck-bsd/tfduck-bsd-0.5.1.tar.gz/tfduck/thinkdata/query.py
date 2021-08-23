"""
from tfduck.tinkdata.query import Query
tq = Query("token")
datas = tq.query(sql="select to_char("#event_time", 'yyyymmdd') as date, "#user_id","#event_name", "#app_id", "#country", "#country_code" from v_event_15 where "$part_event"='click_ad' and "$part_date">'2020-04-01' and "$part_date"<'2020-04-03' limit 100")
"""
import requests


class Query(object):
    def __init__(self, token):
        self.query_uri = "http://da.163py.com:8889/get_result"
        self.token = token

    def query(self, sql):
        """
        @des: query from thinkdata
        @param sql: select to_char("#event_time", 'yyyymmdd') as date, "#user_id","#event_name", "#app_id", "#country", "#country_code" from v_event_15 where "$part_event"='click_ad' and "$part_date">'2020-04-01' and "$part_date"<'2020-04-03' limit 100
        @return: {"header":[数据头], "datas":[数据列表]}
        """
        res = requests.post(self.query_uri, data={
                            "sql": sql, "token": self.token}, timeout=(60, 600))
        query_data = res.json()
        #
        datas = query_data['result']['datas']
        return datas
