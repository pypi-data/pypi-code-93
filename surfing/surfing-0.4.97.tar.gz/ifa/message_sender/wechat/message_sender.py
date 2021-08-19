from ...util.config import Configurator
import datetime
import requests
import json
import time

class MessageSender(object):

    def __init__(self):
        app_secret = Configurator().config['message_sender']['wechat']['app_secret']
        self.app_id = Configurator().config['message_sender']['wechat']['app_id']
        self.access_token_snapshot = None
        self.access_token_expire_timestamp = None

        self.access_token_url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.app_id}&secret={app_secret}'
        
    def get_access_token(self):
        now = datetime.datetime.now()
        if self.access_token_snapshot is None or now > self.access_token_expire_timestamp:
            res = requests.get(self.access_token_url, timeout=5)
            data = json.loads(res.text)
            if 'errcode' in data:
                print(f'Failed to get access token, errmsg: {data["errmsg"]}')
                self.access_token_snapshot = None
                return None
            self.access_token_snapshot = data['access_token']
            self.access_token_expire_timestamp = now + datetime.timedelta(seconds=data['expires_in']-30)
        return self.access_token_snapshot

    def send(self, msg_to, msg_content):
        pass
