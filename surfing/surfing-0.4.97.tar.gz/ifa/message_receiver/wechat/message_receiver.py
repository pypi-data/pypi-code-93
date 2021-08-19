from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, quote, unquote
from xml.etree import ElementTree
import random
import threading
# import ssl
from ...util.config import Configurator
from ...util.struct import WxMsgItem
from ...util import Singleton
from ...util.wx_crypto.WXBizMsgCrypt3 import WXBizMsgCrypt

class MessageCrypt(metaclass=Singleton):

    def __init__(self):
        token = Configurator().config['message_receiver']['wechat']['token']
        aes_key = Configurator().config['message_receiver']['wechat']['aes_key']
        receive_id = Configurator().config['message_receiver']['wechat']['app_id']
        self._msg_crypt = WXBizMsgCrypt(token, aes_key, receive_id)
    
    def get_msg_crypt(self):
        return self._msg_crypt

class WxHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        query = urlparse(self.path).query
        query_components = dict(qc.split("=") for qc in query.split("&"))
        if ("signature" not in query_components or "timestamp" not in query_components or 
            "nonce" not in query_components or "echostr" not in query_components):
            self.send_response(400)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()

        signature = unquote(query_components["signature"])
        timestamp = unquote(query_components["timestamp"])
        nonce = unquote(query_components["nonce"])
        echostr = unquote(query_components["echostr"])

        ret, rsp_echo = MessageCrypt().get_msg_crypt().WechatVerifyURL(signature, timestamp, nonce, echostr)
        print(f'{ret} {rsp_echo}')
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(rsp_echo)

    def do_POST(self):
        query = urlparse(self.path).query
        query_components = dict(qc.split("=") for qc in query.split("&"))
        if ("signature" not in query_components or "timestamp" not in query_components or 
            "nonce" not in query_components):
            self.send_response(400)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()

        signature = unquote(query_components["signature"])
        timestamp = unquote(query_components["timestamp"])
        nonce = unquote(query_components["nonce"])

        # Get the size of post data
        content_length = int(self.headers['Content-Length'])
        # Get the post data
        post_data = self.rfile.read(content_length)

        ret, xml_content = MessageCrypt().get_msg_crypt().WechatDecryptMsg(post_data, signature, timestamp, nonce)
        xml_root = ElementTree.fromstring(xml_content)
        from_user = xml_root.find('FromUserName').text
        to_user = xml_root.find('ToUserName').text
        msg_type = xml_root.find('MsgType').text
        print(xml_content)

        if msg_type == 'text':
            content = xml_root.find('Content').text
            msg_id = xml_root.find('MsgId').text
            data = {
                'msgid': msg_id,
                'tolist': [from_user],
                'msgtype': msg_type,
                'msgtime': int(timestamp) * 1000, # convert to ms
                'text': {'content': content}
            }
            msg = WxMsgItem(data)
            print(msg)

            with self.server.msg_mutex:
                self.server.msgs.append(msg)
        elif msg_type == 'event':
            # When a user scans QR on page of MyProfile/WeChat
            # https://developers.weixin.qq.com/doc/offiaccount/Message_Management/Receiving_event_pushes.html
            event = xml_root.find('Event').text.lower()
            if event == 'subscribe' and xml_root.find('EventKey') is not None and xml_root.find('EventKey').text:
                # When an new user scans QR and follows IFA
                event_key = xml_root.find('EventKey').text
                # "qrscene_" in front of scene_id
                scene_id = event_key[8:]
                print(scene_id)
            elif event == 'scan':
                # When an existing user scans QR
                scene_id = xml_root.find('EventKey').text
                print(scene_id)

        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()

class MyHTTPServer(HTTPServer):
    def __init__(self, server_address, RequestHandlerClass):
        super().__init__(server_address, RequestHandlerClass)
        self.msg_mutex = threading.Lock()
        self.msgs = []

    def get_msg(self, count):
        with self.msg_mutex:
            result = self.msgs[:count]
            self.msgs = self.msgs[count:]
        return result

class MessageReceiver(object):
    def __init__(self):
        # keyfile = Configurator().config['cert']['keyfile']
        # certfile = Configurator().config['cert']['certfile']

        self.server = MyHTTPServer(('0.0.0.0', 80), WxHTTPRequestHandler)
        # server.socket = ssl.wrap_socket(server.socket, 
        #     keyfile=keyfile, 
        #     certfile=certfile, server_side=True)

    def run(self):
        self.server.serve_forever()

    def stop(self):
        self.server.shutdown()

    def get_msg(self, count):
        return self.server.get_msg(count)

if __name__ == '__main__':
    mr = MessageReceiver()
    print('Starting server, use <Ctrl-C> to stop')
    mr.run()