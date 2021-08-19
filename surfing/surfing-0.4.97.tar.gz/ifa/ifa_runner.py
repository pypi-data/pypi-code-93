
from .util.config import Configurator
from .util.struct import WxRawData, WxSeqItem, WxMsgItem
from .message_processor import IfaProcessor
from .message_receiver.wechat.message_receiver import MessageReceiver
import signal
import time, json
import threading
import sys
import libwxwork

class IfaRunner(object):

    def __init__(self, seq=None):
        self.seq = seq or 0
        
        self.processors = []

        self.received_signal = None
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)

    def register(self, processor: IfaProcessor):
        self.processors.append(processor)

    def process_monitor(self):
        corp_id = Configurator().config['wxwork']['corp_id']
        secret_key = Configurator().config['wxwork']['secret_key']
        private_key = Configurator().config['wxwork']['private_key']
        with open(private_key, 'r') as fin:
            private_key_content = fin.read()
        monitor = libwxwork.WxworkWrapper(corp_id, secret_key, private_key_content, -1)
        monitor.init()

        while not self.is_stopped():
            time.sleep(1)
            try:
                res = monitor.get(self.seq, 500)
                data = WxRawData(**json.loads(res))
                for item in data.chatdata:
                    decrypted = None
                    try:
                        decrypted_str = monitor.decode(item.encrypt_random_key, item.encrypt_chat_msg)
                        decrypted = json.loads(decrypted_str)
                    except:
                        print('!' * 10)
                        print(f'error: {decrypted_str}')
                        print('!' * 10)
                    if decrypted:
                        msg = WxMsgItem(decrypted)
                    self.process(msg)
            except Exception as e:
                print(e)
            self.seq = data.max_seq or self.seq

    def process_received(self):
        mr = MessageReceiver()
        t = threading.Thread(target=mr.run)
        t.setDaemon(True)
        t.start()

        while not self.is_stopped():
            time.sleep(1)
            try:
                data = mr.get_msg(500)
                for item in data:
                    self.process(item)
            except Exception as e:
                print(e)

        mr.stop()

    def process(self, msg: WxMsgItem):
        for pr in self.processors:
            pr.process(msg)

    def run(self):
        from .message_processor.wechat.message_processor import WechatMessageProcessor
        self.register(WechatMessageProcessor())

        ts = [
            # threading.Thread(target=self.process_monitor),
            threading.Thread(target=self.process_received)
        ]
        for t in ts:
            t.setDaemon(True)
            t.start()

        print('IFA service started.')

        while True:
            time.sleep(0.01)
            if self.is_stopped():
                print('Wxwork service exited. (sig){}'.format(self.received_signal))
                break

    def signal_handler(self, signum=None, frame=None):
        if self.received_signal is None:
            self.stop(signum=signum)

    def stop(self, signum=signal.SIGTERM):
        self.received_signal = signum

    def is_stopped(self):
        return self.received_signal is not None
