import requests
import time
from collections import OrderedDict
import os


class DingDingHelper:
    def __init__(self, **kwargs):
        self.url = None

    def _send(self, data):
        result = requests.post(self.url, json=data)
        if result.json().get('errcode') != '0':
            raise ValueError('error in sending {} {}'.format(str(data), self.url))
        return result


class DingDingTaskHelper(DingDingHelper):
    def __init__(self, **kwargs):
        super(DingDingTaskHelper, self).__init__(**kwargs)
        self.url = 'https://oapi.dingtalk.com/topapi/workrecord/add?access_token={}'.format(self.get_access_token(**kwargs))

    def get_access_token(self, **kwargs):
        appkey = kwargs.get('appkey', os.getenv('appkey'))
        appsecret = kwargs.get('appsecret', os.getenv('appsecret'))
        url = 'https://oapi.dingtalk.com/gettoken?appkey={appkey}&appsecret={appsecret}'.format(appkey=appkey, appsecret=appsecret)

        return requests.get(url).json().get('access_token')

    def add_task(self, **kwargs):
        data = dict((k, v) for k, v in kwargs.items())
        data.pop('subject')
        data.pop('detail')

        data['create_time'] = int(time.time() * 1000)
        data['formItemList'] = OrderedDict(
                {'title': kwargs.get('subject', ''),
                 'content': kwargs.get('detail', '')
                 }
            )

        result = self._send(data)

    def get_task(self, **kwargs):
        data = dict((k,v) for k, v in kwargs.items())

        result = self._send(data)
        pass


class DingDingWebHookHelper(DingDingHelper):
    def __init__(self, **kwargs):
        super(DingDingWebHookHelper, self).__init__(**kwargs)
        self.url = 'https://oapi.dingtalk.com/robot/send?access_token={webhook_access_token}'.format(**kwargs)



        # 发送文本内容

    def send_text(self, content, *at_mobiles):
        at = {
            # "isAtAll": True
        }
        if at_mobiles:
            at = {
                "isAtAll": False,
                "atMobiles": [i for i in at_mobiles]
            }

        data = {
            "msgtype": "text",
            "text": {
                "content": content
            },
            "at": at
        }
        self._send(data)




if __name__ == '__main__':
    # import pandas as pd
    # from tabulate import tabulate
    # df = pd.read_csv(r"C:\Users\Administrator\Downloads\tech_company_job_2020-03-24.csv")
    # result = df.groupby(['RunDate', 'company']).size().unstack()
    # result_str = tabulate(result, showindex=True, headers='keys', tablefmt='psql')
    # t = DingDingWebHookHelper(webhook_access_token='f74b9260b08a8d6583af9ba6fa4303f16b00f9172385903ff5c166d0d047a31e')
    # t.send_text(content=result_str)
    t = DingDingTaskHelper()
    task = {
        'userid': '656656234939084964',
        'title': 'Youtube',
        'url': 'https://www.baidu.com',
        'subject': 'this is a test message',
        'detail': 'testing '
    }
    t.add_task(**task)


