
# -*- coding: utf-8 -*-

# ===================================================================
# The contents of this file are dedicated to the public domain.  To
# the extent that dedication to the public domain is not available,
# everyone is granted a worldwide, perpetual, royalty-free,
# non-exclusive license to exercise all rights associated with the
# contents of this file for any purpose whatsoever.
# KaisaGlobal rights are reserved.
# ===================================================================

"""
This code provide basic market and trade function for KaisaGlobal-Open.
Pls. note that only HK market is supported now.

developed by KaisaGlobal quant team.
2020.12.11
"""


import os, sys, json

import requests
import threading

import websocket
from copy import deepcopy
from pub_cls_com import *

from os.path import dirname, abspath
import socket

project_path = dirname(dirname(abspath(__file__)))
projec_full_path = project_path + r'\common'
sys.path.append(projec_full_path)

from com import *
from KaisaCrypto import *
from utils import *
from KaisaProtoc import *

kcrypto = KaisaCrypto()
kprotoc = KaisaProtoc()

class KaisaGateway(object):

    req_id = 0
    # gateway - market, trade;
    gateway_auth_status = False
    # ws
    market_ws_alive = False
    trade_ws_alive = False
    # trade;
    trade_connect_status = False
    trade_auth_status = False
    # token
    gatewayToken = None
    tradeToken = None
    _market_ws = None
    _trade_ws = None

    _market_connect_status = False
    _ws_trade_connect_status = False
    _market_connect_msg = ""

    def __init__(self):
        pass

    def jq_user_config(self, user_id,
                       user_pwd,
                       account_code,
                       account_pwd,
                       openapi_token,
                       ip_address='',
                       callback=None):
        # 构造
        self.user_id = user_id
        self.user_pwd = user_pwd
        self.account_code = account_code
        self.account_pwd = account_pwd
        self.openapi_token = openapi_token
        self.root_url = KAISA_ROOT_URL   # KAISA_ROOT_URL_SIM if self.environment in ["simulate", "paper"] else
        self._update_urls()
        self.init_api_bool = False
        self.ip_address = ip_address
        # AF_INET:ipv4, SOCK_STREAM:tcp
        self._open_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.subscribe_code_list = []
        self.callback_cls = callback
        self.userid = ''
        self.gatewayToken = ''
        self.gateway_auth_status = False
        self.gateway_auth_msg = ''
        self.th = None
        self.trade_access_token = None
        self.file_name = project_path + '/logger/heatlog.txt'

    def init_open_md_api(self):
        # 初始化行情api--TCP>>Login

        if self.gateway_auth_status:
            return self.gateway_auth_status, self.gateway_auth_msg

        auth_data = self.gateway_auth()
        use_id = auth_data['userid']
        token = auth_data['token']
        ret_ok = auth_data['status']
        print(f'md_api-开始连接, 更新时间:{datetime.datetime.now()}')
        # 请求登录和初始化行情api
        self._open_sock.connect((OPENIP, OPENPORT))
        self.req_id += 1
        bs_param = KaisaProtoc.tcp_login(token,
                                         get_mac_addr(),
                                         self.ip_address,
                                         use_id,
                                         self.req_id)
        self._open_sock.sendall(bs_param)
        # 获取服务端返回的数据
        res_data = self.on_recv()
        print(f'md_api-连接状态:{res_data}')

        time.sleep(1)

    def _update_urls(self):

        update_url = lambda url: url.replace("__kaisarooturl__", self.root_url)

        self.CRYPTO_RSA_URL = update_url(CRYPTO_RSA_URL)
        self.AUTHENTICA_URL = update_url(AUTHENTICA_URL)
        self.QUOTE_URL = update_url(QUOTE_URL)

        self.REST_DATA_HOST = update_url(REST_DATA_HOST)
        #self.WEBSOCKET_DATA_HOST = update_url(WEBSOCKET_DATA_HOST)

        self.ClientByMobile_URL = update_url(ClientByMobile_URL)
        self.REST_HOST = update_url(REST_HOST)
        self.WEBSOCKET_TRADE_HOST = update_url(WEBSOCKET_TRADE_HOST)

        self.TRADE_CRYPTO_RSA_URL = update_url(TRADE_CRYPTO_RSA_URL)

    def write_error(self, data):
        print(f"error: {data}")

    def write_log(self, data):
        print(f"log: {data}")

    def _authentica(self, auth_username: str, auth_password: str) -> None:
        """
        ## sockt 登录
        获取网关登录令牌;
        :param auth_username:
        :param auth_password:
        :return:
        """

        if self.gateway_auth_status:
            return {'status': self.gateway_auth_status, 'msg': self.gateway_auth_msg, 'token': self.gatewayToken, 'userid': self.userid}
        gateway_auth_msg = ""

        try:
            # only for token of gateway.
            timestamp_ = generate_timestamp()
            sign_ = kcrypto.encrypt_md5("username{}Timestamp{}".format(auth_username, timestamp_))

            auth_username_encrypt = kcrypto.encrypt_rsa_username(auth_username, crypto_rsa_url=self.CRYPTO_RSA_URL)
            auth_password_encrypt = kcrypto.encrypt_aes_password(auth_password, "MAKRET")

            params = {
                "username": auth_username_encrypt,
                "password": auth_password_encrypt,
                "grant_type": "password",
                "scope": openapi_scope
            }

            ipAddress = self.ip_address
            if ipAddress:
                params["ipAddress"] = ipAddress

            headerParam = {"srvType": "open", "ipAddress": ipAddress, "phoneModel": "",
                           "deviceId": "", "deviceToken": "", "macAddress": get_mac_addr(),
                           "channelId": "", "country": "", "sysVersion": "",
                           "apiVersion": "", "platform": ""}
            header_userid_param = {"platform": "web"}
            headerParam = json.dumps(headerParam)
            header_userid_param = json.dumps(header_userid_param)
            authorization_str = "basic {}".format(self.openapi_token)
            headers = {
                "Authorization": authorization_str,
                "Content-Type": "application/x-www-form-urlencoded",
                "Sign": sign_,
                "Timestamp": timestamp_,
                "headerParam": headerParam
            }

            response = requests.post(url=self.AUTHENTICA_URL, params=params, headers=headers)

            data = response.json()
            if response.status_code // 100 == 2:
                # get_userid-url
                self.write_log("网关认证成功")
                if data['success']:
                    self.write_log("获取登录令牌成功")
                    trade_token_body = data["body"]["accessToken"]   #  data['boday']['accessToken']
                    self.trade_access_token = f"bearer {trade_token_body}"
                    __, ___ = self._get_accessToken(data)
                    __gatewayToken__ = __
                    gateway_auth_status = ___

                    __userid__ = self._get_user_info(__, header_userid_param)
                else:
                    self.token = None
                    self.write_log("获取登录令牌失败")
                    self.write_error(data)
                    gateway_auth_status = False
                    gateway_auth_msg = None
                    __userid__ = None
                    __gatewayToken__ = None
            else:
                self.write_log("网关认证失败")
                self.write_error(data)
                gateway_auth_status = False
                gateway_auth_msg = None
                __userid__ = None
                __gatewayToken__ = None
            # self.gatewayToken = f"bearer {token_body}"
            # self.token = self.gatewayToken
            self.gatewayToken = __gatewayToken__
            self.gateway_auth_msg = gateway_auth_msg
            self.gateway_auth_status = gateway_auth_status
            self.userid = __userid__
            self.token = f"bearer {__gatewayToken__}"
        except Exception as expp:
            self.write_log("网关认证失败, err:{}".format(expp))
            gateway_auth_status = self.gateway_auth_status
            gateway_auth_msg = self.gateway_auth_msg
            __userid__ = self.userid
            __gatewayToken__ = self.gatewayToken
            self.token = None

        return {'status': gateway_auth_status, 'msg': gateway_auth_msg, 'token': __gatewayToken__, 'userid': __userid__}

    def _get_user_info(self, token, header_userid_param):
        # 获取user-msg
        headers_userid = {
            "Authorization": 'bearer ' + token,
            "headerParam": header_userid_param
        }
        UA_URL = AU_USERID_URL.replace('__kaisarooturl__', self.root_url)
        response_userid = requests.post(url=UA_URL, headers=headers_userid)

        if response_userid.status_code // 100 == 2:
            userid_data = response_userid.json()
            user_id_num = userid_data['body']['userId']

        else:
            user_id_num = ''
        return user_id_num

    def _get_accessToken(self, data):
        # 获取登录令牌
        try:
            token_body = data["body"]["accessToken"]
            #gatewayToken = f"bearer {token_body}"
            gateway_auth_status = True
        except Exception as exp:
            print('获取登录令牌抛异常:{}'.format(exp))
            token_body = ''
            gateway_auth_status = False
        return token_body, gateway_auth_status

    def gateway_auth(self):
        return self._authentica(self.user_id, self.user_pwd)

    def init_md_api(self):
        '''
        初始化mdApi
        --login并验证行情账号
        --初始化行情Api
        '''
        try:
            data = self.gateway_auth()
            ret_msg = data['msg']
            ret_ok = data['status']
            if ret_ok:
                print('行情账号登录成功!')
                self.init_api_bool = ret_ok
            else:
                print('行情账号登录失败,error:{}!'.format(ret_msg))
        except Exception as exp:
            return 'market-ws disconnected!', exp

    def do_market_requests(self, url, reqdata):

        reqdata = self._market_req_decorate(reqdata)
        method = reqdata["method"] if ("method" in reqdata) else "POST"
        headers = reqdata["headers"] if ("headers" in reqdata) else None
        params = reqdata["params"] if ("params" in reqdata) else None
        data = reqdata["data"] if ("data" in reqdata) else None

        response = requests.request(
            method,
            url,
            headers=headers,
            params=params,
            data=json.dumps(data)
        )
        status_code = response.status_code
        resp_data = response.json()
        return status_code, resp_data

    def _market_req_decorate(self, reqdata):

        reqdata['headers'] = {
            "Authorization": self.gatewayToken,
            "Content-Type": "application/json"
        }
        return reqdata

    def query_all_symbollist(self):

        contractdata_all = []
        beginpos = 0
        count = 1000
        while True:
            symbols = self.query_symbollist(beginpos=beginpos, count=count)
            if symbols is None:
                break
            contractdata_all += symbols
            if len(symbols)<count:
                break
            beginpos += count
        if len(contractdata_all)>0:
            self.write_log("合约信息查询成功")
        else:
            self.write_log("合约信息查询失败")

        return contractdata_all

    def query_symbollist(self, beginpos=0, count=1000):

        self.req_id += 1
        data = {
            "reqtype": QUERY_CONTRACT,
            "reqid": self.req_id,
            "session": "",
            "data": {
                "marketid": HKSE_MARKET,
                "idtype": 1,
                "beginpos": beginpos,
                "count": count,
                "getquote": 1
            }
        }

        reqdata = {"data": data}
        status_code, resp_data = self.do_market_requests(url=self.QUOTE_URL, reqdata=reqdata)
        if status_code//100 == 2:
            symbols = resp_data['data']['symbol']
        else:
            symbols = None
        return symbols

    def get_market_connect_ws_status(self):

        return self._market_connect_status, self._market_connect_msg

    def on_recv(self):
        # recv
        res_data = self._open_sock.recv(1024)
        return res_data

    def on_message(self):
        # get-data
        while True:
            try:
                message = self.on_recv()
                # 把字符串转换为json数据类型
                data = kprotoc.rec_bstring_to_json(message)
                if data is None:
                    pass
                elif data['data'] is not None:
                    #  回调函数
                    self.callback_cls(data)
            except Exception as expp:
                continue

    def _on_sub(self, subscribe_code_list):
        # open-sub
        print("####### on_sub #######")
        def run(*args):

            self.req_id += 1
            sub_bstring = kprotoc.get_subscribe_bstring(subscribe_code_list, self.req_id)
            rd = self._open_sock.sendall(sub_bstring)
            time.sleep(1)
        try:
            run()
            self.subscribe_code_list = subscribe_code_list
            # 发心跳
            self.th = threading.Thread(target=self._market_ping, args=())
            self.th.start()

            # 获取数据
            th_msg = threading.Thread(target=self.on_message, args=())
            th_msg.start()

        except Exception as exp:
            print('on-open--error:{}'.format(exp))
            pass

    def on_market_packet(self, packet):
        self.on_market_data(packet)

    def on_market_data(self, data):
        # 行情数据到达>>data
        pass

    def subscribe_marketdata(self, code_list):
        """
        订阅quote和tick数据
        code_list: [{'code':'01638', 'market':2, 'sub_type':2}]
        """
        self.req_id += 1
        # 订阅
        self._on_sub(code_list)

    def unsubscribe_marketdata(self, code_list):
        """
        取消推送行情和分笔
        :param symbols:
        :return:
        """
        try:
            self.req_id += 1
            bstring = kprotoc.get_unsubscribe_bstring(code_list, self.req_id)
            self._open_sock.sendall(bstring)
        except Exception as exp:
            pass


    def _market_ping(self):
        """
        :param this_ws:
        :return:
        """
        while True:
            _now_ = datetime.datetime.now()
            try:
                with open(self.file_name, 'a') as fs:
                    mytxt = '发送心跳:{}'.format(_now_) + ', ' + '线程状态:{}'.format(self.th.is_alive()) + '.\n'
                    fs.write(mytxt)
                self.market_heartbeat()
                time.sleep(5)
            except Exception as exp:
                with open(self.file_name, 'a') as fs:
                    mytxt = '发送心跳:{}'.format(_now_) + ', 出现异常:'.format(exp) + ', ' + '线程状态:{}'.format(self.th.is_alive()) + '.\n'
                    fs.write(mytxt)
                # 断开
                self._open_sock.close()
                self.gateway_auth_status = False
                # api 重连
                self.init_open_md_api()
                # 重新订阅行情
                self.subscribe_marketdata(self.subscribe_code_list)
                time.sleep(5)

    def market_heartbeat(self):
        # 心跳
        self.req_id += 1
        ping_bstring = kprotoc.get_ping_bstring(self.req_id)
        self._open_sock.sendall(ping_bstring)

    def send_market_packet(self, packet):
        text = json.dumps(packet)
        #self._open_sock.send(text)

    def generate_req(self, reqtype: int, data: dict) -> dict:

        self.req_id += 1
        req = {
            "reqtype": reqtype,
            "reqid": self.req_id,
            "session": "",
            "data": data
        }
        return req

    def _trade_req_decorate(self, reqdata, reqtype="normal"):

        json_dumps = lambda item: json.dumps(item, separators=(',', ':'))
        method = reqdata['method'] if 'method' in reqdata else "POST"
        headers = reqdata['headers'] if 'headers' in reqdata else {}
        data = reqdata['data'] if 'data' in reqdata else {}
        params = reqdata['params'] if 'params' in reqdata else {}

        this_timestamp = generate_timestamp()

        if (reqtype == "connect") and (method == "POST") and ('q' in reqdata['data']):
            headers = {"Content-Type": "application/json",
                       "Authorization": self.token
                       }
            params = deepcopy(reqdata['data'])
            reqdata = {'method': method,
                       'headers': headers,
                       'data': json_dumps(reqdata['data']),
                       'params': params
                       }
            return reqdata

        if reqtype == "login":
            #app_token = "bearer eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyX25hbWUiOiI5NjAwNzAyMDExIiwic2NvcGUiOlsicmVhZCJdLCJhdXRoVG9rZW4iOiJ7XCJhY2Nlc3NUb2tlblZhbGlkaXR5XCI6MCxcImFwcExvZ2luVHlwZVwiOlwiY2xpZW50SWRcIixcImhlYWRlclBhcmFtVk9cIjp7XCJhcGlWZXJzaW9uXCI6XCIxLjcuMVwiLFwiY2hhbm5lbElkXCI6XCJcIixcImNvdW50cnlcIjpcIlwiLFwiZGV2aWNlSWRcIjpcIjUyRDBEM0ZCLURDNzktNDFFNS04NDQ2LThGRjAxRDc5RUY5MFwiLFwiZGV2aWNlTmFtZVwiOlwiJUU2JTlEJThFJUU2JTlGJUIxJUU2JTk2JUIwJUU3JTlBJTg0aVBob25lXCIsXCJkZXZpY2VUb2tlblwiOlwiYmE4NDk5OWU0MzRkMzBkYTZjYWQyNjg3MWE5M2NiYjY4ZDJkYzZmNDBjMzFhOWRiZmQwNmNkMzI2ZmQzOWMyZFwiLFwiaXBBZGRyZXNzXCI6XCIxMTcuMTM2LjQwLjE3OVwiLFwibGFuZ3VhZ2VcIjpcImdiXCIsXCJtYWNBZGRyZXNzXCI6XCIwMjowMDowMDowMDowMDowMFwiLFwicGhvbmVNb2RlbFwiOlwiaVBob25lIFhcIixcInBsYXRmb3JtXCI6XCJpT1NcIixcInN5c1ZlcnNpb25cIjpcIjEzLjZcIn0sXCJtb2JpbGVcIjpcIjEzNTYwNzk3MTYwXCIsXCJwaG9uZUFyZWFcIjpcIis4NlwiLFwicmVmcmVzaFRva2VuVmFsaWRpdHlcIjowLFwidGltZXN0YW1wXCI6MCxcInVzZXJJZFwiOlwiMTM2NjYzMTU0MTYwNjQwODE5NFwifSIsImV4cCI6MTYyNzE5MjIwNiwidXNlcklkIjoiTVRNMk5qWXpNVFUwTVRZd05qUXdPREU1TkE9PSIsImF1dGhvcml0aWVzIjpbIlJPTEVfQURNSU4iXSwianRpIjoiZWM1ZDQ4MzgtNWU5MC00YWMzLTk4NjAtNjQ0ODExMjBmNTYxIiwiZmlyc3QiOm51bGwsImNsaWVudF9pZCI6InRlc3RfY2xpZW50X2FwcCIsInRpbWVzdGFtcCI6MTYyNzEwNTgwNjUxN30.cJ4-pGzuosEiIv_ZqKnMPuZe8MBE4sqR9zQiwiqSruw"
            headers['Content-Type'] = "application/json"
            headers["Authorization"] = self.token
            if reqtype == "login":
                data['Authorization'] = self.token
            if self.tradeToken is not None:
                headers['X-Trade-Token'] = self.tradeToken
            if reqtype == "normal":
                if 'tradeToken' in data:
                    del data['tradeToken']
            if method == "POST":
                header_ = reqdata['data'].copy()
                if self.tradeToken is not None:
                    header_["tradeToken"] = self.tradeToken
                headers["Sign"] = self.__sign(header_=header_, timestamp_=this_timestamp, request_="POST")
                headers["Timestamp"] = this_timestamp

            reqdata = {"method": method,
                       "data": json_dumps(data),
                       "headers": headers,
                       "params": json_dumps(params)}
            return reqdata

        headers = {"Content-Type": "application/json",
                   "Authorization": self.token,  # self.gatewayToken,
                   "X-Trade-Token": self.tradeToken
                   }

        if method == "GET":
            if 'params' in reqdata:
                header_ = reqdata['params'].copy()
            else:
                header_ = {}
            header_["Authorization"] = self.token
            headers["Sign"] = self.__sign(header_=header_, timestamp_=this_timestamp, request_="GET")
            headers["Timestamp"] = this_timestamp

        if method == "POST":
            header_ = data.copy()
            if self.tradeToken is not None:
                header_["tradeToken"] = self.tradeToken
            headers["Sign"] = self.__sign(header_=header_, timestamp_=this_timestamp, request_="POST")
            headers["Timestamp"] = this_timestamp

        if (method == "POST") and ('q' not in data):
            q_string = json_dumps(data)
            q_string = kcrypto.encrypt_aes_password_forQ(q_string, "SECRET")
            data = {'q': q_string}

        reqdata = {"method": method,
                   "data": json_dumps(data),
                   "headers": headers,
                   "params": params}

        return reqdata

    def _sign(self, reqdata, reqtype="normal"):

        json_dumps = lambda item: json.dumps(item, separators=(',', ':'))
        method = reqdata['method']
        headers = reqdata['headers'] if 'headers' in reqdata else {}
        data = reqdata['data'] if 'data' in reqdata else {}
        params = reqdata['params'] if 'params' in reqdata else {}

        if (reqtype == "connect") and (method == "POST") and ('q' in reqdata['data']):
            headers = {"Content-Type": "application/json",
                       "Authorization": self.token}

            params = deepcopy(reqdata['data'])
            reqdata = {'method': method,
                       'headers': headers,
                       'data': json_dumps(reqdata['data']),
                       'params': params
                       }
            return reqdata

        if reqtype == "login":

            headers['Content-Type'] = "application/json"
            headers["Authorization"] = self.token
            if reqtype == "login":
                data['Authorization'] = self.token

            if self.tradeToken is not None:
                headers['X-Trade-Token'] = self.tradeToken

            if reqtype == "normal":
                if 'tradeToken' in data:
                    del data['tradeToken']

            if method == "POST":
                timestamp_ = generate_timestamp()
                header_ = reqdata['data'].copy()
                if self.tradeToken is not None:
                    header_["tradeToken"] = self.tradeToken
                headers["Sign"] = self.__sign(header_=header_, timestamp_=timestamp_, request_="POST")
                headers["Timestamp"] = timestamp_

            reqdata = {"method": method,
                       "data": json_dumps(data),
                       "headers": headers,
                       "params": json_dumps(params)}

            return reqdata

        headers = {"Content-Type": "application/json",
                   "Authorization": self.gatewayToken,
                   "X-Trade-Token": self.tradeToken
                   }

        if method == "GET":
            timestamp_ = generate_timestamp()
            header_ = reqdata['params'].copy()
            header_["Authorization"] = self.token
            headers["Sign"] = self.__sign(header_=header_, timestamp_=timestamp_, request_="GET")
            headers["Timestamp"] = timestamp_

        if method == "POST":
            timestamp_ = generate_timestamp()
            header_ = data.copy()
            if self.tradeToken is not None:
                header_["tradeToken"] = self.tradeToken
            headers["Sign"] = self.__sign(header_=header_, timestamp_=timestamp_, request_="POST")
            headers["Timestamp"] = timestamp_

        if (method == "POST") and ('q' not in data):
            q_string = json_dumps(data)
            q_string = kcrypto.encrypt_aes_password_forQ(q_string, "SECRET")
            data = {'q': q_string}

        reqdata = {"method": method,
                   "data": json_dumps(data),
                   "headers": headers,
                   "params": params}

        return reqdata

    def __sign(self, header_: dict = {}, request_=None, timestamp_=None):

        sign_ = None
        str_ = ""
        for key_ in sorted(header_):
            str_ += str(key_)+str(header_[key_])
        str_ += "Timestamp"+timestamp_
        sign_ = kcrypto.encrypt_md5(str_)
        return sign_

    def do_trade_requests(self, url, reqdata, reqtype="normal"):

        reqdata = self._trade_req_decorate(reqdata, reqtype)
        method = reqdata["method"] if ("method" in reqdata) else "POST"
        headers = reqdata["headers"] if ("headers" in reqdata) else None
        params = reqdata["params"] if ("params" in reqdata) else None
        data = reqdata["data"] if ("data" in reqdata) else None
        response = requests.request(
            method,
            url,
            headers=headers,
            params=params,
            data=data
        )
        status_code = response.status_code
        resp_data = response.json()
        return status_code, resp_data

    def trade_connect(self):
        """
        交易api连接
        :return: trade_connect_status
        """

        auth_data = self.gateway_auth()
        use_id = auth_data['userid']
        token = auth_data['token']
        ret_ok = auth_data['status']
        if ret_ok:
            en_password_trade = kcrypto.encrypt_aes_password(self.account_pwd, type="TRADE")
            self.en_password_trade = en_password_trade
            secret_q = kcrypto.encrypt_rsa_secretQ(crypto_rsa_url=self.TRADE_CRYPTO_RSA_URL)
            data = {
                "q": secret_q,
                "accountCode": self.account_code
            }
            url = self.REST_HOST + "/v1/account/shakeHand"
            reqdata = {"data": data}

            status_code, resp_data = self.do_trade_requests(url, reqdata, "connect")
            self.sessionId = resp_data['body']['sessionId']
            self.trade_connect_status = True

        self.trade_connect_msg = ''
        return self.trade_connect_status, self.trade_connect_msg

    def trade_auth(self):
        # 交易账户认证、登录

        headerParam = {"platform": "open", "deviceName": "",
                      "apiVersion": "1.7.1", "country": "", "channelId": "", "language": "gb",
                      "ipAddress": self.ip_address, "phoneModel": "", "sysVersion": "13.6",
                      "macAddress": get_mac_addr(), "deviceId": "",
                      "deviceToken": ""}
        data = {
            "channelType": "INTERNET",
            "accountCode": self.account_code,
            "password": self.en_password_trade,
            "secondAuthFromOther": "Y",
            "sessionId": self.sessionId
        }
        headers = {
            "headerParam": json.dumps(headerParam)
        }

        reqdata = {"data": data, "headers": headers}

        url = self.REST_HOST + "/v1/account/login"
        status_code, resp_data = self.do_trade_requests(url, reqdata, "login")
        if status_code//100 == 2:
            self.tradeToken = resp_data['body']['tradeToken']
            print('self.tradeToken:{}'.format(self.tradeToken))
            self.trade_auth_status = True
        else:
            self.tradeToken = None
            self.trade_auth_status = False
        self.trade_auth_msg = ''
        return self.trade_auth_status, self.trade_auth_msg

    def trade_connect_ws(self):
        threading.Thread(target=self._start_trade_ws, daemon=True).start()

    def get_trade_connect_ws_status(self):
        return self._ws_trade_connect_status, ""

    def _trade_ping(self, this_ws):
        """
        :param this_ws:
        :return:
        """
        pass

    def _start_trade_ws(self):

        if self._ws_trade_connect_status:
            return True

        #
        data = {
            "channelType": "INTERNET",
            "accountCode": self.account_code,
            "password": self.en_password_trade,
            "ipAddress": "",
            "secondAuthFromOther": "Y",
            "sessionId": self.sessionId,
        }

        host = self.WEBSOCKET_TRADE_HOST
        header = {"Authorization": self.token}
        # # create_connection--
        self._trade_ws = websocket.create_connection(host, header=header)

        req = self.generate_req(LOGIN, data)

        req = json.dumps(req)
        self._trade_ws.send(req)
        self._trade_ping_th = threading.Thread(target=self._trade_ping, args=(self._trade_ws,), daemon=True)
        self._trade_ping_th.start()
        self._ws_trade_connect_status = True

        while True:
            text = self._trade_ws.recv()
            self.on_trade_packet(text)

    def on_trade_packet(self, packet):

        if len(packet) == 0:
            return
        data = json.loads(packet)
        if data.get('reqtype', 0) == 2:
            req_data = {"ts": data['data']["ts"]}
            req_data = self.generate_req(PONG, req_data)
            self._trade_ws.send(json.dumps(req_data))
        else:
            data = json.loads(packet)
            self.on_trade_data(packet)

    def send_order(self, bsFlag='B', price=550, qty=600, code='00700'):

        return self.place_order(bsFlag=bsFlag, price=price, qty=qty, code=code)

    def place_order(self, bsFlag='B', price=550, qty=600, code='00700'):

        data = {'channelType': "I",
                'exchangeCode': 'HKEX',
                'accountCode': self.account_code,
                'productCode': code,
                'price': price, 'qty': qty,
                'bsFlag': bsFlag, 'orderType': 'L',
                'tradeToken': self.tradeToken}

        reqdata = {"data": data,
                   "params": {'accountCode': self.account_code}}

        url = self.REST_HOST+"/v1/order/orders/place"
        status_code, resp_data = self.do_trade_requests(url, reqdata)

        resp_status = resp_data['success']
        if resp_status:
            body_data = resp_data['body']
        else:
            body_data = {'retCode': resp_data['retCode'],
                         'retMsg': resp_data['retMsg']
                         }
        return resp_status, body_data

    def cancel_order(self, sys_orderid):

        data = {
            "channelType": "I",
            "accountCode": self.account_code,
            "orderID": sys_orderid,
            "tradeToken": self.tradeToken,
        }
        reqdata = {"data": data,
                   "params": {'accountCode': self.account_code}}

        url = self.REST_HOST+"/v1/order/orders/cancel"
        status_code, resp_data = self.do_trade_requests(url, reqdata)

        resp_status = resp_data['success']
        if resp_status:
            body_data = resp_data['body']
        else:
            body_data = {'retCode': resp_data['retCode'],
                         'retMsg': resp_data['retMsg']
                         }
        return resp_status, body_data

    def query_portfolio(self):

        reqdata = {"method":"GET",
                   "params": {'accountCode': self.account_code}}

        url = self.REST_HOST+"/v1/account/accounts/portfolio"
        status_code, resp_data = self.do_trade_requests(url, reqdata)

        resp_status = resp_data['success']
        if resp_status:
            body_data = resp_data['body']
        else:
            body_data = {'retCode': resp_data['retCode'],
                         'retMsg': resp_data['retMsg']
                         }
        return resp_status, body_data

    def query_balance(self):

        reqdata = {"method": "GET",
                   "params": {'accountCode': self.account_code}}
        url = self.REST_HOST + "/v1/account/accounts/balance"
        status_code, resp_data = self.do_trade_requests(url, reqdata)
        resp_data = resp_data.json()
        resp_status = resp_data['success']
        if resp_status:
            body_data = resp_data['body']
        else:
            body_data = {'retCode': resp_data['retCode'],
                         'retMsg': resp_data['retMsg']
                         }
        return resp_status, body_data

    def query_position(self):

        reqdata = {"method": "GET",
                   "params": {'accountCode': self.account_code}}
        url = self.REST_HOST + "/v1/account/accounts/position"
        status_code, resp_data = self.do_trade_requests(url, reqdata)

        resp_status = resp_data['success']
        if resp_status:
            body_data = resp_data['body']
        else:
            body_data = {'retCode': resp_data['retCode'],
                         'retMsg': resp_data['retMsg']
                         }
        return resp_status, body_data

    def query_order(self):

        reqdata = {"method": "GET",
                   "params": {'accountCode': self.account_code}}
        url = self.REST_HOST + "/v1/order/orders"
        status_code, resp_data = self.do_trade_requests(url, reqdata)

        resp_status = resp_data['success']
        if resp_status:
            body_data = resp_data['body']
        else:
            body_data = {'retCode': resp_data['retCode'],
                         'retMsg': resp_data['retMsg']
                         }
        return resp_status, body_data

if __name__=="__main__":

    print("Hello, Kaisa.")

