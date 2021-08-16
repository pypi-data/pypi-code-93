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
        token = Configurator().config['message_receiver']['wxwork']['token']
        aes_key = Configurator().config['message_receiver']['wxwork']['aes_key']
        receive_id = Configurator().config['message_receiver']['wxwork']['corp_id']
        self._msg_crypt = WXBizMsgCrypt(token, aes_key, receive_id)
    
    def get_msg_crypt(self):
        return self._msg_crypt

class WxHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        query = urlparse(self.path).query
        query_components = dict(qc.split("=") for qc in query.split("&"))
        msg_signature = unquote(query_components["msg_signature"])
        timestamp = unquote(query_components["timestamp"])
        nonce = unquote(query_components["nonce"])
        echostr = unquote(query_components["echostr"])

        ret, rsp_echo = MessageCrypt().get_msg_crypt().VerifyURL(msg_signature, timestamp, nonce, echostr)
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        # self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(rsp_echo)

    def do_POST(self):
        query = urlparse(self.path).query
        query_components = dict(qc.split("=") for qc in query.split("&"))
        msg_signature = unquote(query_components["msg_signature"])
        timestamp = unquote(query_components["timestamp"])
        nonce = unquote(query_components["nonce"])

        # Get the size of post data
        content_length = int(self.headers['Content-Length'])
        # Get the post data
        post_data = self.rfile.read(content_length)

        ret, xml_content = MessageCrypt().get_msg_crypt().DecryptMsg(post_data, msg_signature, timestamp, nonce)
        xml_root = ElementTree.fromstring(xml_content)
        from_user = xml_root.find('FromUserName').text
        msg_type = xml_root.find('MsgType').text
        content = xml_root.find('Content').text
        msg_id = xml_root.find('MsgId').text
        agent_id = xml_root.find('AgentID').text

        if msg_type == 'text':
            data = {
                'msgid': msg_id,
                'from': f'wo{agent_id}',
                'tolist': [from_user],
                'msgtype': msg_type,
                'msgtime': int(timestamp) * 1000, # convert to ms
                'text': {'content': content}
            }
            msg = WxMsgItem(data)
            print(msg)

            with self.server.msg_mutex:
                self.server.msgs.append(msg)

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
        port = Configurator().config['message_receiver']['wxwork']['port']

        self.server = MyHTTPServer(('0.0.0.0', port), WxHTTPRequestHandler)
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