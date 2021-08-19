# -*- coding: utf-8 -*-
import sys
import time, struct
from os.path import dirname, abspath
import requests, datetime
import pandas as pd
import numpy as np
import json, uuid, socket
from ctypes import *
from com import *
'''Date: 2021.03.15'''

from py_protoc import msg_comm_request_pb2 as msg_stock_common
from py_protoc import msg_comm_cust_pb2 as cust_pb
from py_protoc import msg_comm_response_pb2 as reponse_pb
from py_protoc import stock_comm_pb2 as comm_pb
from py_protoc import stock_real_pb2 as msg_stock    # real_pb
from py_protoc import stock_his_pb2 as msg_his_stock
def get_mac_addr():
    # 获取Mac地址
    macaddr = uuid.UUID(int=uuid.getnode()).hex[-12:]
    return ":".join([macaddr[e:e+2] for e in range(0, 11, 2)])

def get_ip_addr():
    # 获取本机ip
    # 获取电脑名称
    this_name = socket.getfqdn(socket.gethostname())
    # 获取IP
    ip = socket.gethostbyname(this_name)
    return ip



def total_handle_req(body, URL):
    response = requests.request(
        method='POST',
        url=URL,
        headers={'Content-Type': 'application/json'},
        params=None,
        data=json.dumps(body),
    )
    resp_data = response.json()
    resp_status = resp_data['success']

    if resp_status is False:
        return pd.DataFrame()
    try:
        _df_ = pd.DataFrame(resp_data['body']['data'])
    except:
        _df_ = (resp_data['body'])

    return _df_

def handle_hist_data_req_pages(body, URL):
    # 历史行情数据
    response = requests.request(
        method='POST',
        url=URL,
        headers={'Content-Type': 'application/json'},
        params=None,
        data=json.dumps(body),
    )
    try:
        resp_data = response.json()
        resp_status = resp_data['success']

        if resp_status is False:
            return pd.DataFrame()
        try:
            pages = resp_data['body']['pages']
            return pages
        except:
            ret = resp_data['body']
            return ret
    except Exception as exp:
        return '您好, 您填入的参数有误(response.status:{}), 请检查后重新请求!'.format(response.status_code)

def total_handle_hist_data_req(body, URL):
    response = requests.request(
        method='POST',
        url=URL,
        headers={'Content-Type': 'application/json'},
        params=None,
        data=json.dumps(body),
    )
    resp_data = response.json()
    resp_status = resp_data['success']

    if resp_status is False:
        return pd.DataFrame()
    try:
        __ = resp_data['body']['records']
        return __
    except:
        ret = resp_data['body']
        return ret

def change_timestamp(ts):
    # change ts
    ts = int(str(ts)[:10])
    timeArray = time.localtime(int(ts))
    _date_ = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return _date_

def t_typeof(variate):
    '''
    返回变量的类型
    '''

    type = None
    if isinstance(variate, int):
        type = "int"
    elif isinstance(variate, str):
        type = "str"
    elif isinstance(variate, float):
        type = "float"
    elif isinstance(variate, list):
        type = "list"
    elif isinstance(variate, tuple):
        type = "tuple"
    elif isinstance(variate, dict):
        type = "dict"
    elif isinstance(variate, set):
        type = "set"
    return type


# ResHead头定义
class IPResHead(Structure):
    _fields_ = [
        ("ihl", c_ubyte, 4),
        ("version", c_ubyte, 4),
        ("tos", c_ubyte),
        ("len", c_ushort),
        ("id", c_ushort),
        ("offset", c_ushort),
        ("ttl", c_ubyte),
        ("protocol_num", c_ubyte),
        ("sum", c_ushort),
        ("src", c_uint),
        ("dst", c_uint),
    ]

    def __new__(self, socket_buffer=None):
        return self.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer=None):
        self.protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}
        # readable ip address
        self.src_address = socket.inet_ntoa(struct.pack("<I", self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("<I", self.dst))
        # type of protocol
        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except:
            self.protocol = str(self.protocol_num)


def get_respdata(data=None):
    head = data[0:28]
    respheat = struct.unpack('>hhhihihhii', head)
    mod = respheat[6]
    cmd = respheat[7]

    datalen = respheat[9]
    rspdata = ''
    if mod == 20 and cmd == 0:
        rspdata=''

    elif mod == 4 and cmd ==21:
        rspdata = rsp_HandicapQuotaResp(data[28:])
        #mssg = eum.cmd_mod(mod, cmd, rspdata)

    elif mod == 7 and cmd == 300:
        rspdata = rsp_TransactionStatResp(data[28:])
        #eum.cmd_mod(mod, cmd, rspdata)

    elif mod == 4 and cmd == 22:
        rspdata = rsp_KlineQuoteResp(data[28:])
        #eum.cmd_mod(mod, cmd, rspdata)

    elif mod == 4 and cmd == 23:
        rspdata = rsp_TickResp(data[28:])
        #eum.cmd_mod(mod, cmd, rspdata)

    elif mod == 4 and cmd == 24:
        rspdata = rsp_MinuteQuoteResp(data[28:])
        #eum.cmd_mod(mod, cmd, rspdata)

    elif mod ==5 and cmd in [100,101,102,105,106,107]:
        rspdata = rsp_SubMarketPlateReq(data[28:])
        #eum.cmd_mod(mod, cmd, rspdata)

# -----------------  订阅  ---------------------------------------

    elif mod == 1 and cmd == 1:
        # 分比数据
        # rspdata = rsp_Quote(data[28:])
        # eum.cmd_mod(mod, cmd, rspdata)
        rspdata = rsp_Quote(data[28:datalen + 28])
        #message = eum.cmd_mod(mod, cmd, rspdata)
        # print(message)
        surplus_data = data[datalen + 28:]
        if len(surplus_data) >= 28:
            get_respdata(data=surplus_data)

    # 订阅tick
    elif mod == 1 and cmd == 2:
        # 基础行情数据（返回）
        rspdata = rsp_TickList(data[28:datalen+28])

        now = rspdata.tick[0].now
        cur_volume = rspdata.tick[0].cur_volume
        tick_flag = rspdata.tick[0].tick_flag
        if rspdata.tick[0].tick_time.seconds:
            timeArray = time.localtime(rspdata.tick[0].tick_time.seconds)
            ns = int(rspdata.tick[0].tick_time.nanos / 10000) % 1000
        else:
            timeArray = time.localtime(rspdata.tick[0].recv_time.seconds)
            ns = int(rspdata.tick[0].recv_time.nanos / 10000) % 1000
        tick_time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        quote_time = str(tick_time)+'.'+str(ns)
        time_now = time.time()
        if rspdata.tick[0].tick_time.seconds:
            tick_time = rspdata.tick[0].tick_time.seconds + rspdata.tick[0].tick_time.nanos / 1000000000
        else:
            tick_time = rspdata.tick[0].recv_time.seconds + rspdata.tick[0].recv_time.nanos / 1000000000

        # if rspdata.market in (1, 2, 10, 11):
        #     alltime = cf.time_difference(time_now, tick_time)
        # else:
        #     alltime = cf.time_difference(time_now,tick_time) - 12*3600*1000
        # loginfo = rspdata.code + ':'+quote_time.ljust(26)+str(now).ljust(10)+ str(cur_volume).ljust(5) + str(tick_flag)+ '    延迟时间：'+str(int(alltime))+'ms'
        #log.info(loginfo)
        #eum.cmd_mod(mod, cmd, rspdata)
        surplus_data = data[datalen+28:]
        if len(surplus_data) >= 28:
            get_respdata(data=surplus_data)

    elif mod == 1 and cmd == 3:
        # 经纪人队列数据
        # rspdata = rsp_BrokerList(data[28:])
        # eum.cmd_mod(mod, cmd, rspdata)
        rspdata = rsp_BrokerList(data[28:datalen + 28])
        # message = eum.cmd_mod(mod, cmd, rspdata)
        surplus_data = data[datalen + 28:]
        if len(surplus_data) >= 28:
            get_respdata(data=surplus_data)

    elif mod == 1 and cmd == 4:
        # 买卖档数据
        rspdata = rsp_OrderStallsList(data[28:datalen + 28])
        # message = eum.cmd_mod(mod, cmd, rspdata)
        surplus_data = data[datalen + 28:]
        if len(surplus_data) >= 28:
            get_respdata(data=surplus_data)

    return cmd, rspdata

# --------------   拉取数据返回   ---------------------------------------

# 盘口响应解析
def rsp_HandicapQuotaResp(data):
    user_out = msg_his_stock.HandicapQuotaResp()
    user_out.ParseFromString(data)
    return user_out

# 成交统计数据（返回）
def rsp_TransactionStatResp(data):
    user_out = msg_his_stock.TransactionStatResp()
    user_out.ParseFromString(data)
    return user_out

# K线数据（返回）
def rsp_KlineQuoteResp(data):
    user_out = msg_his_stock.KlineQuoteResp()
    user_out.ParseFromString(data)
    return user_out

# tick数据（返回）
def rsp_TickResp(data):
    user_out = msg_his_stock.TickResp()
    user_out.ParseFromString(data)
    return user_out

def rsp_MinuteQuoteResp(data):
    user_out = msg_his_stock.MinuteQuoteResp()
    user_out.ParseFromString(data)
    return user_out

# --------------   订阅数据返回   ---------------------------------------
# 基础行情数据（返回）
def rsp_Quote(data):
    user_out = msg_stock.Quote()
    user_out.ParseFromString(data)
    return user_out

# 分比数据（返回）
def rsp_TickList(data):
    # print(' 分比数据（返回）:',data)
    user_out = msg_stock.TickList()
    user_out.ParseFromString(data)
    return user_out

# 经纪人队列数据（返回）
def rsp_BrokerList(data):
    user_out = msg_stock.BrokerList()
    user_out.ParseFromString(data)
    return user_out

# 买卖盘数据（返回）
def rsp_OrderStallsList(data):
    user_out = msg_stock.OrderStallsList()
    user_out.ParseFromString(data)
    return user_out

def rsp_SubMarketPlateReq(data):
    user_out = msg_his_stock.SubMarketAssetInfoResp()
    user_out.ParseFromString(data)
    return user_out


if __name__ == '__main__':
    pass
    # get_TransactionStatReq()
    # code_list=[{'code':'00700'},{'code':'01638'}]
    # HandicapQuotaReq(mod = 4, cmd = 21,symbollist = code_list)