from ...util.config import Configurator
import datetime
import requests
import json
import time

class MessageSender(object):

    def __init__(self):
        corp_id = Configurator().config['message_sender']['wechat']['corp_id']
        app_secret = Configurator().config['message_sender']['wechat']['app_secret']
        self.app_id = Configurator().config['message_sender']['wechat']['app_id']
        self.access_token_snapshot = None
        self.access_token_expire_timestamp = None

        self.access_token_url = f'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corp_id}&corpsecret={app_secret}'
        
    def get_access_token(self):
        now = datetime.datetime.now()
        if self.access_token_snapshot is None or now > self.access_token_expire_timestamp:
            res = requests.get(self.access_token_url, timeout=5)
            data = json.loads(res.text)
            if data['errcode'] != 0:
                print(f'Failed to get access token, errmsg: {data["errmsg"]}')
                self.access_token_snapshot = None
                return None
            self.access_token_snapshot = data['access_token']
            self.access_token_expire_timestamp = now + datetime.timedelta(seconds=data['expires_in']-30)
        return self.access_token_snapshot

    def send(self, msg_to, msg_content):
        pass
