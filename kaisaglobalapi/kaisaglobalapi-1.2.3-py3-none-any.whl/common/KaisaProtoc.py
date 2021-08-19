# -*- coding: utf-8 -*-

import sys, json, time, struct, datetime
from os.path import dirname, abspath
from google.protobuf import json_format
project_path = dirname(dirname(abspath(__file__)))
projec_full_path = project_path + r'\py_protoc'
sys.path.append(projec_full_path)
from pub_cls_com import *
from com import *
############################旧版################################
# from py_protoc import msg_stock_pb2 as msg_stock
# from py_protoc import msg_stock_pb2 as msg_stock
# from py_protoc import msg_stock_common_pb2 as msg_stock_common
############################旧版################################

from py_protoc import msg_comm_request_pb2 as msg_stock_common
from py_protoc import msg_comm_cust_pb2 as cust_pb
from py_protoc import msg_comm_response_pb2 as reponse_pb
from py_protoc import stock_comm_pb2 as comm_pb
from py_protoc import stock_real_pb2 as msg_stock    # real_pb

class KaisaProtoc(object):

    def __init__(self):
        pass

    @staticmethod
    def tcp_login(token, macip, ip, userid, reqid):
        # tcp 登录、初始化行情api
        pb_login = comm_pb.Login()
        pb_login.token = token
        pb_login.deviceId = macip
        pb_login.macAddress = macip
        pb_login.ipAddress = ip
        pb_login.sysVersion = SYSVERSION
        pb_login.platform = PLATFORM
        pb_login.phoneModel = PHONEMODEL
        pb_login.srvType = SRVTYPE
        pb_login.username = EP
        pb_login.password = EP
        pb_login.userId = userid
        pb_string = pb_login.SerializeToString()
        return KaisaProtoc.get_reqhead(20, 0, pb_string, reqid)

    @staticmethod
    def get_head_bstring():
        #  通讯头
        packFlag = struct.pack('>h', 2021)
        iCompress = struct.pack('>h', 0)
        iVersion = struct.pack('>h', 0)
        iReserve = struct.pack('>i', 0)
        iCheckId = struct.pack('>h', 1990)
        head_bstrin = packFlag + iCompress + iVersion + iReserve + iCheckId
        return head_bstrin

    @staticmethod
    def get_cust_head_bstring():
        #cust_head
        cust_c = cust_pb.CustHead()
        cust_c.packFlag = 2021
        cust_c.iCompress = 0
        cust_c.iVersion = 0
        cust_c.iReserve = 0
        cust_c.iCheckId = 1990
        return cust_c

    @staticmethod
    def get_reqhead(mod, cmd, data, reqid=None):
        # 请求头
        #len_data = len(data)
        if reqid is not None:
            reqId = struct.pack('>i', reqid)
        else:
            reqId = 0
        # 心跳
        if mod == 3:
            data = b'0'
        mod = struct.pack('>h', mod)
        cmd = struct.pack('>h', cmd)
        datalen = struct.pack('>i', len(data))
        #len_custhead = len(KaisaProtoc.get_head_bstring())
        reqhead = KaisaProtoc.get_head_bstring() + reqId + mod + cmd + datalen
        #len_reqhead = len(reqhead)
        result = reqhead + data
        #len_rresult = len(result)
        return result
    @staticmethod
    def get_reshead(data):
        #
        res = KaisaProtoc.get_head_bstring() + data
        return res

    @staticmethod
    def get_ping_bstring(reqId=1):
        # 心跳
        pb_string = KaisaProtoc.get_reqhead(3, 0, b'0', reqId)
        return pb_string

    @staticmethod
    def get_subscribe_bstring(symbollist, reqId=1):
        '''
        订阅行情
        SUB_TYPE_NONE = 0;
        QUOTE = 1;
        TICK = 2;
        BROKER = 3;
        ORDER = 4;
        '''
        pb_rule = msg_stock.Rule()
        #pb_stockcode = msg_stock.StockCode()
        for secucode_dict in symbollist:
            pb_stockcode_one = pb_rule.stockCodes.add()
            pb_stockcode_one.code = secucode_dict['code']
            market = secucode_dict['market']
            pb_stockcode_one.market = market
            pb_stockcode_one.language = 0
            pb_stockcode_one.types.append(secucode_dict['sub_type'])

        ps = pb_rule.SerializeToString()
        mod = 1
        cmd = 10
        pb_string = KaisaProtoc.get_reqhead(mod, cmd, ps, reqId)
        return pb_string

    @staticmethod
    def get_unsubscribe_bstring(symbollist, reqId=1):
        '''
        退订行情
        SUB_TYPE_NONE = 0;
        QUOTE = 1;
        TICK = 2;
        BROKER = 3;
        ORDER = 4;
        '''
        mod = 1
        cmd = 11
        pb_rule = msg_stock.Rule()
        pb_stockcode = msg_stock.StockCode()
        for secucode_dict in symbollist:
            pb_stockcode_one = pb_rule.stockCodes.add()
            pb_stockcode_one.code = secucode_dict['code']
            market = secucode_dict['market']
            pb_stockcode_one.market = market
            pb_stockcode_one.language = 0
            pb_stockcode_one.types.append(secucode_dict['sub_type'])
        ps = pb_rule.SerializeToString()

        pb_string = KaisaProtoc.get_reqhead(mod, cmd, ps, reqId)
        return pb_string

    @staticmethod
    def rec_bstring_to_json(bstring):
        '''
        uint32 cmd = 4; //对应模块编号下的指令 2位
        {QUOTE = 1;
        TICK = 2;
        }
        bytes data = 7; //二进制数据 4位

        # '!'表示我们用网络字节序解析,因为我们是从网络上接收到这个buf的。
        # 'H'表示unsigned short的id；
        # '4s'表示四个字节长的字符串； char[4]
        # '2I'表示有两个unsigned int类型的数据；
        '''

        data_type = 0
        try:
            if len(bstring) >= 28:
                cmd, __ = get_respdata(bstring)
                if __ == '' or cmd not in ALLDATAIDLIST:
                    return {'type': 0, 'data': None}
                else:
                    data_type, res_data = KaisaProtoc.handle_any_data_cls(cmd, __)
                    return {'type': data_type, 'data': res_data}
            else:
                return {'type': 0, 'data': None}
        except BaseException as exp:
            print('获取行情抛异常:{}'.format(exp))
            return {'type': data_type, 'data': None}


    @staticmethod
    def quote_bstring_to_json(quote):
        ## 解析quote-data
        sec = quote.quote_time.seconds
        nano = quote.quote_time.nanos
        # up_t = datetime.datetime.fromtimestamp((sec + nano / 1000000000.0))
        update_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(sec + nano / 1000000000.0))
        return {'market': quote.market,
                'code': quote.code,
                'now': quote.now,
                'high': quote.high,
                'low': quote.low,
                'volume': quote.volume,
                'amount': quote.amount,
                'quote_time': update_time,
                }

    @staticmethod
    def broker_list_bstring_to_json(broker_list):
        # broker-list data to json

        return {'market': broker_list.market,
                'code': broker_list.code,
                'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(
                    broker_list.time.seconds+broker_list.time.nanos/1000000000.0)),
                'brokerSell': [KaisaProtoc.broker_bstring_to_json(bs) for bs in broker_list.brokerSell],
                'brokerBuy': [KaisaProtoc.broker_bstring_to_json(bb) for bb in broker_list.brokerBuy]
                }

    @staticmethod
    def broker_bstring_to_json(broker):
        ## broker data to json
        return {'broker_level': broker.broker_level,
                'broker_id': [KaisaProtoc.broker_id_bstring_to_json(_id_) for _id_ in broker.broker_id]
                }

    @staticmethod
    def broker_id_bstring_to_json(broker):
        # broker-is data to json
        return {'broker_id': broker}

    @staticmethod
    def ticklist_bstring_to_json(ticklist):

        return {'market': ticklist.market,
                'code': ticklist.code,
                'tick': [KaisaProtoc.tick_bstring_to_json(item) for item in ticklist.tick]
                }

    @staticmethod
    def tick_bstring_to_json(tick):

        return {'now': tick.now,
                'cur_volume': tick.cur_volume,
                'tick_flag': tick.tick_flag,
                'tick_vi': tick.tick_vi,
                'tick_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(
                    tick.tick_time.seconds+tick.tick_time.nanos/1000000000.0))
                }

    @staticmethod
    def level_order_list_string_to_json(order_list):
        # level_order list data

        return {'market': order_list.market,
                'code': order_list.code,
                'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(
                    order_list.time.seconds+order_list.time.nanos/1000000000.0)),
                'orderSell': [KaisaProtoc.level_order_bsstring_to_json(bs) for bs in order_list.orderSell],
                'orderBuy': [KaisaProtoc.level_order_bsstring_to_json(bb) for bb in order_list.orderBuy]
                }
    @staticmethod
    def level_order_bsstring_to_json(order_bs):
        # 转换order中的bs数据
        return {'level': order_bs.level,
                'price': order_bs.price,
                'volume': order_bs.volume,
                'broker_count': order_bs.broker_count
                }

    @staticmethod
    def handle_any_data_cls(DATATYPE, data):
        # total-handle-data
        try:
            THISDATATYPE = PROTODATADIC[DATATYPE]
            if THISDATATYPE == 'QUOTE':
                return KaisaProtoc._get_quote_data(data)
            elif THISDATATYPE == 'TICK':
                return KaisaProtoc._get_tick_data(data)
            elif THISDATATYPE == 'BROKER':
                return KaisaProtoc._get_broker_data(data)
            elif THISDATATYPE == 'ORDER':
                return KaisaProtoc._get_level_order_data(data)
            else:
                pass
        except Exception as exp:
            print('get-quote-data-_dic_ error:{}'.format(exp))
            return None

    @staticmethod
    def _get_tick_data(data):
        #### cmd=2
        #### 逐笔数据 tick

        body_json = KaisaProtoc.ticklist_bstring_to_json(data)
        return PROTODATADIC[TICK], body_json

    @staticmethod
    def _get_quote_data(data):
        #### cmd=1
        #### 盘口数据 quote

        try:
            ## 判断该条行情是否有效
            if data.update_flag != [1, 4, 8, 16, 32, 2048, 32768]:
                return QUOTE, None
            else:
                body_json = KaisaProtoc.quote_bstring_to_json(data)
                return PROTODATADIC[QUOTE], body_json
        except Exception as exp:
            print('get-quote-data-error:{}'.format(exp))

    @staticmethod
    def _get_broker_data(data):
        #### cmd=3
        #### 经纪商数据 broker-list
        body_json = KaisaProtoc.broker_list_bstring_to_json(data)
        return PROTODATADIC[BROKERS], body_json

    @staticmethod
    def _get_level_order_data(data):
        ### cmd=4
        ### level-10 order data
        body_json = KaisaProtoc.level_order_list_string_to_json(data)
        return PROTODATADIC[LEVEL_ORDER], body_json

if __name__=='__main__':
    print('start.')

