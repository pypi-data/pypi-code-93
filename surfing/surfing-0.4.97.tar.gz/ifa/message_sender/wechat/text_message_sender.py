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
        target_url = f'https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={access_token}'

        # Send url
        message = {
            'touser': '|'.join(msg_to) if type(msg_to) is list else msg_to,
            'msgtype': 'text',
            'text': {'content': msg_content}
        }
        print(message)
        res = requests.post(url=target_url, data=json.dumps(message, ensure_ascii=False).encode(), timeout=20)

        # # For QR test
        # qr_url = f'https://api.weixin.qq.com/cgi-bin/qrcode/create?access_token={access_token}'
        # qr_message = {
        #     'expire_seconds': 1800, # QR is valid for 30 minutes
        #     'action_name': 'QR_SCENE',
        #     'action_info': {
        #         'scene': {
        #             'scene_id': 1122
        #         }
        #     }
        # }
        # print(qr_message)
        # res = requests.post(url=qr_url, data=json.dumps(qr_message, ensure_ascii=False).encode(), timeout=20)
        # print(res.text)
