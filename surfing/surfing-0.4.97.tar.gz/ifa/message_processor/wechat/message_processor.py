from .. import IfaProcessor
from ..message_parser import WechatMessageParser
from ...message_sender.wechat.image_message_sender import ImageMessageSender
from ...message_sender.wechat.text_message_sender import TextMessageSender
import time
import json
import urllib.parse
import sys
import datetime
from ...util.config import Configurator
from ...util.struct import WxMsgItem

class WechatMessageProcessor(IfaProcessor):

    def __init__(self):
        self.message_parser = WechatMessageParser()
        self.image_message_sender = ImageMessageSender()
        self.text_message_sender = TextMessageSender()

        self.start_ts = int(datetime.datetime.now().timestamp() * 1000)

    def process(self, msg: WxMsgItem):
        if msg.msgtime < self.start_ts:
            return

        if len(msg.to_ids) != 1:
            return

        result = self.message_parser.parse(msg.from_id, msg.to_ids, msg.text_content)
        print(result)
        # we can handle scenario 1 only
        if result['type'] == 'hqzx' and 'target' in result['data'] and result['data']['target'] == 'fund':
            target_url = 'http://52.82.113.3:12300/FundInfo?id='
            content = target_url + urllib.parse.quote_plus(result['data']['fund'])
            self.text_message_sender.send(msg.to_ids, content)
            self.image_message_sender.send(msg.to_ids, content)
        elif result['type'] == 'hx':
            self.text_message_sender.send(msg.to_ids, self.process_hx_message(result['data']['message']))
        else:
            content = json.dumps(result, indent=4, ensure_ascii=False)
            self.text_message_sender.send(msg.to_ids, content)

    def process_hx_message(self, message):
        interrogatives = ['吗', '嘛', '么']
        for interrogative in interrogatives:
            if interrogative in message:
                pos = message.rfind(interrogative)
                result = message[0: pos]
                return result
        return message
