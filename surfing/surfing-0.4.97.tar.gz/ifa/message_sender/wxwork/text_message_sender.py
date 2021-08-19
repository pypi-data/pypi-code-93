from .message_sender import MessageSender
import datetime
import requests
import json
import time

class TextMessageSender(MessageSender):

    def __init__(self):
        super(TextMessageSender, self).__init__()

    def send(self, msg_to, msg_content):
        # Send snapshot of webpage and url
        # doc: https://open.work.weixin.qq.com/api/doc/90000/90135/90236
        access_token = self.get_access_token()
        target_url = f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}'

        # Send url
        message = {
            'touser': '|'.join(msg_to) if type(msg_to) is list else msg_to,
            'msgtype': 'text',
            'agentid': self.app_id,
            'text': {'content': msg_content}
        }
        res = requests.post(url=target_url, data=json.dumps(message), timeout=20)
