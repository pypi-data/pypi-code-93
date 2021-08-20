import asyncio
import json
import gzip
import logging
import traceback
import uuid
from datetime import datetime
from typing import Optional
from functools import partial, wraps
from urllib.parse import urlparse

import aiohttp
from aiohttp.web_ws import WSMessage

from common.exceptions import HuoBiWebSocketError
from common.huobi import constants
from common.huobi.constants import WebSocketOP
from common.huobi.tools import generate_signature


def is_coin_margined_market(f):
    @wraps(f)
    async def wrapper(self, *args, **kwargs):
        assert self.ws.url_path == HuoBiWebSocketManager.COIN_MARGINED_MARKET
        return await f(self, *args, **kwargs)
    return wrapper


def is_coin_margined_order(f):
    @wraps(f)
    async def wrapper(self, *args, **kwargs):
        assert self.ws.url_path == HuoBiWebSocketManager.COIN_MARGINED_ORDER
        return await f(self, *args, **kwargs)
    return wrapper


def is_future_market(f):
    @wraps(f)
    async def wrapper(self, *args, **kwargs):
        assert self.ws.url_path == HuoBiWebSocketManager.FUTURE_MARKET
        return await f(self, *args, **kwargs)
    return wrapper


def is_future_order(f):
    @wraps(f)
    async def wrapper(self, *args, **kwargs):
        assert self.ws.url_path == HuoBiWebSocketManager.FUTURE_ORDER
        return await f(self, *args, **kwargs)
    return wrapper


def is_index(f):
    @wraps(f)
    async def wrapper(self, *args, **kwargs):
        assert self.ws.url_path == HuoBiWebSocketManager.INDEX_DATA
        return await f(self, *args, **kwargs)
    return wrapper


def is_system_status(f):
    @wraps(f)
    async def wrapper(self, *args, **kwargs):
        assert self.ws.url_path == HuoBiWebSocketManager.SYSTEM_STATUS
        return await f(self, *args, **kwargs)
    return wrapper


class ReconnectingWebSocket:
    TIMEOUT = 20

    def __init__(self, url: str, auto_ping=True, proxy=None,
                 api_key: Optional[str] = None, api_secret: Optional[str] = None):
        """
        @param url 建立websocket的地址
        """
        self._url = url
        self.url_path = urlparse(url).path[1:]
        self.ws: aiohttp.ClientWebSocketResponse = None
        self._session: aiohttp.ClientSession = None
        self._conn = None
        self._proxy = proxy
        self._auto_ping = auto_ping
        self._api_key = api_key
        self._api_secret = api_secret
        self._connected = False
        self._already_send_auth = False
        self._complete_auth = False
        self._sub_channels = []
        self.auth_complete_event = asyncio.Event()

    @property
    def api_key(self):
        return self._api_key

    @property
    def need_send_auth(self) -> bool:
        return self._api_secret and self._api_key and not self._already_send_auth

    @property
    def need_reconnected(self) -> bool:
        return self.ws is None or self.ws.closed or self._connected is False

    def _reset_flag(self):
        """
        连接断开后重置标志变量
        """
        # 断开后conn已经失效，必须重连
        self._conn = None
        self._connected = self._already_send_auth = self._complete_auth = False

    async def send_auth(self):
        if not self.ws:
            raise HuoBiWebSocketError("no binding web socket")
        if self.ws.closed:
            raise HuoBiWebSocketError("websocket has closed")

        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
        data = {
            "AccessKeyId": self._api_key,
            "SignatureMethod": "HmacSHA256",
            "SignatureVersion": "2",
            "Timestamp": timestamp
        }
        sign = generate_signature(self._api_secret, "GET", self._url, data)
        data['op'] = WebSocketOP.AUTH
        data['type'] = 'api'
        data['Signature'] = sign
        logging.debug(f"send auth msg: {data}")
        await self.ws.send_json(data)
        self._already_send_auth = True

    async def __aenter__(self):
        if self.need_reconnected:
            self._reset_flag()
            await self._reconnect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.ws:
            await self.ws.close()
        if self._conn:
            await self._conn.__aexit__(exc_type, exc_val, exc_tb)
        self.ws = None
        self._reset_flag()
        if self._session:
            await self._session.close()
            self._session = None

    async def _reconnect(self):
        logging.warning("reconnecting web socket right now!")
        await self._connect()
        await self._connected_callback()

    async def _connect(self):
        logging.info(f"ws connect {self._url}")
        if not self._session or self._session.closed:
            self._session = aiohttp.ClientSession(trust_env=True)
            self._conn = None
            self.ws = None
        if self._conn is None:
            self._conn = self._session.ws_connect(self._url, proxy=self._proxy)
            self.ws = None
        try:
            if self.ws is None:
                self.ws = await self._conn.__aenter__()
            self._connected = True
            logging.debug("connect successfully!")
        except aiohttp.client.ClientConnectorError:
            logging.error(f"connect to ws server error! url: {self._url}")

    async def _connected_callback(self):
        """
        After connect to WebSocket server successfully, send a auth message to server.
        """
        if self.need_send_auth:
            await self.send_auth()
            logging.debug("wait for auth response")
            while self._complete_auth is False:
                await self.recv()
            self.auth_complete_event.set()
            logging.debug("auth complete!")

    async def check_connection(self, *args, **kwargs):
        if not self.ws:
            logging.warning("web socket connection not connected yet!")
            return
        if self.ws.closed:
            self._reset_flag()
            await self._reconnect()

    async def recv(self):
        res = None
        if self.ws is None:
            raise HuoBiWebSocketError("web socket connection not connected yet")

        while not res:
            if self.ws.closed:
                self._reset_flag()
                await self._reconnect()
                continue
            try:
                res = await asyncio.wait_for(self.ws.receive(), timeout=self.TIMEOUT)
            except asyncio.TimeoutError:
                logging.debug(f"no message in {self.TIMEOUT} seconds")
            except asyncio.CancelledError as e:
                logging.debug(f"cancelled error {e}")
            except asyncio.IncompleteReadError as e:
                logging.debug(f"incomplete read error {e}")
            except Exception as e:
                logging.debug(f"exception {e}")
            else:
                res = self._handle_message(res)

            if isinstance(res, dict):
                if ("ping" in res or res.get("op") == WebSocketOP.PING) and self._auto_ping:
                    if self.url_path in (HuoBiWebSocketManager.FUTURE_ORDER, HuoBiWebSocketManager.COIN_MARGINED_ORDER,
                                         HuoBiWebSocketManager.USDT_MARGINED_ORDER):
                        pong_msg = {"op": WebSocketOP.PONG, "ts": res['ts']}
                    else:
                        pong_msg = {"pong": res['ping']}
                    await self.ws.send_json(pong_msg)
                    logging.debug(f"send {pong_msg}")
                    res = None
                elif res.get("op") == WebSocketOP.CLOSE:
                    self._reset_flag()
                    await self._reconnect()
                    res = None
                elif res.get("op") == WebSocketOP.AUTH and res.get('err-code') == 0:
                    self._complete_auth = True

                if res and res.get('err-code'):
                    logging.error(res)

        return res

    def _handle_message(self, msg: WSMessage):
        if msg.type == aiohttp.WSMsgType.TEXT:
            try:
                data = json.loads(msg.data)
            except:
                data = msg.data
        elif msg.type == aiohttp.WSMsgType.BINARY:
            uncompress_data = gzip.decompress(msg.data).decode()
            try:
                data = json.loads(uncompress_data)
            except:
                data = uncompress_data
        elif msg.type in (aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
            logging.error(f"receive unexpected msg: {msg}")
            return None
        else:
            raise HuoBiWebSocketError(f"invalid msg type: {msg.type}")

        logging.debug(f"receive msg: {data}")
        return data

    async def send_heartbeat_msg(self, msg, *args, **kwargs):
        """
        发送心跳给server
        """
        if not self.ws:
            logging.warning("web socket connection not connected yet!")
        try:
            if isinstance(msg, dict):
                await self.ws.send_json(msg)
            elif isinstance(msg, str):
                await self.ws.send_str(msg)
            else:
                logging.error(f"invalid heartbeat msg type: {msg}")
            logging.debug(f"send ping message: {msg}")
        except ConnectionResetError:
            traceback.print_exc()
            await asyncio.get_running_loop().create_task(self._reconnect())

    async def send_request(self, payload):
        if self._connected is False or self.ws is None or self.ws.closed:
            await self._connect()
            await self._connected_callback()
        # payload['id'] = str(uuid.uuid1())
        logging.debug(f"send msg: {payload}")
        await self.ws.send_json(payload)


class HuoBiWebSocketManager:
    BASE_URL = "wss://api.hbdm.com/"
    BASE_AWS_URL = "wss://api.hbdm.vn/"

    FUTURE_MARKET = "ws"
    FUTURE_ORDER = "notification"
    COIN_MARGINED_MARKET = "swap-ws"
    COIN_MARGINED_ORDER = "swap-notification"
    USDT_MARGINED_MARKET = "linear-swap-ws"
    USDT_MARGINED_ORDER = "linear-swap-notification"

    INDEX_DATA = "ws_index" # 指数/基差
    SYSTEM_STATUS = "center-notification"

    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None, proxy=None):
        self.proxy = proxy
        self.ws: ReconnectingWebSocket = None
        self._api_key = api_key
        self._api_secret = api_secret
        self._create_ws = partial(ReconnectingWebSocket, proxy=self.proxy, api_key=api_key, api_secret=api_secret)

    def set_coin_margined_market_socket(self) -> "HuoBiWebSocketManager":
        self.ws = self._create_ws(url=self.BASE_URL + self.COIN_MARGINED_MARKET)
        return self

    def set_coin_margined_order_socket(self) -> "HuoBiWebSocketManager":
        self.ws = self._create_ws(url=self.BASE_URL + self.COIN_MARGINED_ORDER)
        return self

    def set_future_market_socket(self) -> "HuoBiWebSocketManager":
        self.ws = self._create_ws(url=self.BASE_URL + self.FUTURE_MARKET)
        return self

    def set_future_order_socket(self) -> "HuoBiWebSocketManager":
        self.ws = self._create_ws(url=self.BASE_URL + self.FUTURE_ORDER)
        return self

    def set_index_socket(self) -> "HuoBiWebSocketManager":
        self.ws = self._create_ws(url=self.BASE_URL + self.INDEX_DATA)
        return self

    def set_system_status_socket(self) -> "HuoBiWebSocketManager":
        self.ws = self._create_ws(url=self.BASE_URL + self.SYSTEM_STATUS)
        return self

    ######################################################
    # 币本位永续合约接口                                    #
    ######################################################

    ##########
    # 行情
    ##########

    @is_coin_margined_market
    async def sub_coin_margined_kline(self, symbol: str, period=constants.KLINE_INTERVAL_1MINUTE):
        await self.ws.send_request({WebSocketOP.SUB: f"market.{symbol}.kline.{period}"})

    @is_coin_margined_market
    async def req_coin_margined_kline(self, symbol: str, start: int, end: int, period=constants.KLINE_INTERVAL_1MINUTE):
        """
        :param symbol:
        :param start:
        :param end: 开始时间/秒
        :param period: 结束时间/秒
        :return:
        """
        await self.ws.send_request({
            WebSocketOP.REQ: f"market.{symbol.upper()}.kline.{period}",
            "from": start,
            "to": end
        })

    @is_coin_margined_market
    async def sub_coin_margined_market_depth(self, symbol: str, depth_type=constants.WS_DEPTH_5):
        await self.ws.send_request({WebSocketOP.SUB: f"market.{symbol}.depth.{depth_type}"})

    @is_coin_margined_market
    async def sub_coin_margined_incremental_market_depth(self, symbol: str, size=20, data_type=constants.DataType.INCREMENTAL):
        await self.ws.send_request({
            WebSocketOP.SUB: f"market.{symbol}.depth.size_{size}.high_freq",
            "data_type": data_type
        })

    @is_coin_margined_market
    async def sub_coin_margined_market_detail(self, symbol: str):
        await self.ws.send_request({
            WebSocketOP.SUB: f"market.{symbol}.detail"
        })

    @is_coin_margined_market
    async def sub_coin_margined_bbo(self, symbol: str):
        await self.ws.send_request({
            WebSocketOP.SUB: f"market.{symbol}.bbo"
        })

    @is_coin_margined_market
    async def sub_coin_margined_trade_detail(self, symbol: str):
        await self.ws.send_request({WebSocketOP.SUB: f"market.{symbol}.trade.detail"})

    @is_coin_margined_market
    async def req_coin_margined_trade_detail(self, symbol: str):
        await self.ws.send_request({WebSocketOP.REQ: f"market.{symbol}.trade.detail"})

    #############
    # 订单/用户数据
    #############

    @is_coin_margined_order
    async def sub_coin_margined_order(self, symbol):
        await self.ws.send_request({
            "op": WebSocketOP.SUB,
            "topic": f"orders.{symbol}"
        })

    @is_coin_margined_order
    async def unsub_coin_margined_order(self, symbol):
        await self.ws.send_request({
            "op": WebSocketOP.UNSUB,
            "topic": f"orders.{symbol}"
        })

    @is_coin_margined_order
    async def sub_coin_margined_account(self, symbol):
        await self.ws.send_request({
            "op": WebSocketOP.SUB,
            "topic": f"accounts.{symbol}"
        })

    @is_coin_margined_order
    async def unsub_coin_margined_account(self, symbol):
        await self.ws.send_request({
            "op": WebSocketOP.UNSUB,
            "topic": f"accounts.{symbol}"
        })

    @is_coin_margined_order
    async def sub_coin_margined_position(self, symbol):
        await self.ws.send_request({
            "op": WebSocketOP.SUB,
            "topic": f"positions.{symbol}"
        })

    @is_coin_margined_order
    async def unsub_coin_margined_position(self, symbol):
        await self.ws.send_request({
            "op": WebSocketOP.UNSUB,
            "topic": f"positions.{symbol}"
        })

    @is_coin_margined_order
    async def sub_coin_margined_match_orders(self, symbol):
        """订单撮合数据"""
        await self.ws.send_request({
            "op": WebSocketOP.SUB,
            "topic": f"matchOrders.{symbol}"
        })

    @is_coin_margined_order
    async def unsub_coin_margined_match_orders(self, symbol):
        await self.ws.send_request({
            "op": WebSocketOP.UNSUB,
            "topic": f"matchOrders.{symbol}"
        })

    @is_coin_margined_order
    async def sub_coin_margined_liquidation_orders(self, symbol):
        """强平订单数据"""
        await self.ws.send_request({
            "op": WebSocketOP.SUB,
            "topic": f"public.{symbol}.liquidation_orders"
        })

    @is_coin_margined_order
    async def unsub_coin_margined_liquidation_orders(self, symbol):
        await self.ws.send_request({
            "op": WebSocketOP.UNSUB,
            "topic": f"public.{symbol}.liquidation_orders"
        })

    @is_coin_margined_order
    async def sub_coin_margined_funding_rate(self, symbol):
        """资金费率推送"""
        await self.ws.send_request({
            "op": WebSocketOP.SUB,
            "topic": f"public.{symbol}.funding_rate"
        })

    @is_coin_margined_order
    async def unsub_coin_margined_funding_rate(self, symbol):
        await self.ws.send_request({
            "op": WebSocketOP.UNSUB,
            "topic": f"public.{symbol}.funding_rate"
        })

    @is_coin_margined_order
    async def sub_coin_margined_contract_info(self, symbol):
        """合约信息变动"""
        await self.ws.send_request({
            "op": WebSocketOP.SUB,
            "topic": f"public.{symbol}.contract_info"
        })

    @is_coin_margined_order
    async def unsub_coin_margined_contract_info(self, symbol):
        await self.ws.send_request({
            "op": WebSocketOP.UNSUB,
            "topic": f"public.{symbol}.contract_info"
        })

    @is_coin_margined_order
    async def sub_coin_margined_trigger_order(self, symbol):
        """计划委托订单更新"""
        await self.ws.send_request({
            "op": WebSocketOP.SUB,
            "topic": f"trigger_order.{symbol}"
        })

    @is_coin_margined_order
    async def unsub_coin_margined_trigger_order(self, symbol):
        await self.ws.send_request({
            "op": WebSocketOP.UNSUB,
            "topic": f"trigger_order.{symbol}"
        })

    ########################
    ### 交割合约接口
    ########################

    #### 行情 #####
    @is_future_market
    async def sub_future_kline(self, symbol: str, period=constants.KLINE_INTERVAL_1MINUTE):
        """
        KLine数据
        symbol	true	string	交易对		支持大小写，如"BTC_CW"表示BTC当周合约，"BTC_NW"表示BTC次周合约，"BTC_CQ"表示BTC当季合约 , "BTC_NQ"表示次季度合约 。支持使用合约code来订阅 例如："BTC200918"(当周)，"BTC200925"(次周)，"BTC201225"(季度)，"BTC210326"(次季度)。
        period	true	string	K线周期    仅支持小写，1min, 5min, 15min, 30min, 60min,4hour,1day,1week, 1mon
        """
        await self.ws.send_request({WebSocketOP.SUB: f"market.{symbol}.kline.{period}"})

    @is_future_market
    async def req_future_kline(self, symbol: str, start: int, end: int, period=constants.KLINE_INTERVAL_1MINUTE):
        await self.ws.send_request({
            WebSocketOP.REQ: f"market.{symbol.upper()}.kline.{period}",
            "from": start,
            "to": end
        })

    @is_future_market
    async def sub_future_market_depth(self, symbol: str, depth_type=constants.WS_DEPTH_5):
        """
        深度
        symbol	true	string	交易对		支持大小写，如"BTC_CW"表示BTC当周合约，"BTC_NW"表示BTC次周合约，"BTC_CQ"表示BTC当季合约, "BTC_NQ"表示次季度合约". 支持使用合约code来订阅 例如："BTC200918"(当周)，"BTC200925"(次周)，"BTC201225"(季度)，"BTC210326"(次季度)。
        type	true	string	Depth 类型		获得150档深度数据，使用step0, step1, step2, step3, step4, step5, step14, step15 （step1至step15是进行了深度合并后的深度），使用step0时，不合并深度获取150档数据;获得20档深度数据，使用 step6, step7, step8, step9, step10, step11, step12, step13（step7至step13是进行了深度合并后的深度），使用step6时，不合并深度获取20档数据
        """
        await self.ws.send_request({WebSocketOP.SUB: f"market.{symbol}.depth.{depth_type}"})

    @is_future_market
    async def sub_future_incremental_market_depth(self, symbol: str, size=20, data_type=constants.DataType.INCREMENTAL):
        """
        深度增量数据
        :param symbol:
        :param size:
        :param data_type:
        :return:
        """
        await self.ws.send_request({
            WebSocketOP.SUB: f"market.{symbol}.depth.size_{size}.high_freq",
            "data_type": data_type
        })

    @is_future_market
    async def sub_future_market_detail(self, symbol: str):
        await self.ws.send_request({
            WebSocketOP.SUB: f"market.{symbol}.detail"
        })

    @is_future_market
    async def sub_future_bbo(self, symbol: str):
        """
        买一卖一逐笔行情数据
        :param symbol:
        :return:
        """
        await self.ws.send_request({
            WebSocketOP.SUB: f"market.{symbol}.bbo"
        })

    @is_future_market
    async def sub_future_trade_detail(self, symbol: str):
        await self.ws.send_request({WebSocketOP.SUB: f"market.{symbol}.trade.detail"})

    @is_future_market
    async def req_future_trade_detail(self, symbol: str, size=50):
        await self.ws.send_request({
            WebSocketOP.REQ: f"market.{symbol}.trade.detail",
            "size": size
        })

    # 订单/资产变动
    @is_future_order
    async def sub_future_order(self, symbol):
        """
        订单成交数据
        :param symbol:
        :return:
        """
        await self.ws.send_request({
            "op": WebSocketOP.SUB,
            "topic": f"orders.{symbol}"
        })

    @is_future_order
    async def unsub_future_order(self, symbol):
        await self.ws.send_request({
            "op": WebSocketOP.UNSUB,
            "topic": f"orders.{symbol}"
        })

    @is_future_order
    async def sub_future_match_orders(self, symbol):
        """订单撮合数据"""
        await self.ws.send_request({
            "op": WebSocketOP.SUB,
            "topic": f"matchOrders.{symbol}"
        })

    @is_future_order
    async def unsub_future_match_orders(self, symbol):
        await self.ws.send_request({
            "op": WebSocketOP.UNSUB,
            "topic": f"matchOrders.{symbol}"
        })

    @is_future_order
    async def sub_future_account(self, symbol):
        """
        资产变动
        :param symbol:
        :return:
        """
        await self.ws.send_request({
            "op": WebSocketOP.SUB,
            "topic": f"accounts.{symbol}"
        })

    @is_future_order
    async def unsub_future_account(self, symbol):
        await self.ws.send_request({
            "op": WebSocketOP.UNSUB,
            "topic": f"accounts.{symbol}"
        })

    @is_future_order
    async def sub_future_position(self, symbol):
        """
        持仓变动
        :param symbol:
        :return:
        """
        await self.ws.send_request({
            "op": WebSocketOP.SUB,
            "topic": f"positions.{symbol}"
        })

    @is_future_order
    async def unsub_future_position(self, symbol):
        await self.ws.send_request({
            "op": WebSocketOP.UNSUB,
            "topic": f"positions.{symbol}"
        })

    @is_future_order
    async def sub_future_liquidation_orders(self, symbol):
        """强平订单数据"""
        await self.ws.send_request({
            "op": WebSocketOP.SUB,
            "topic": f"public.{symbol}.liquidation_orders"
        })

    @is_future_order
    async def unsub_future_liquidation_orders(self, symbol):
        await self.ws.send_request({
            "op": WebSocketOP.UNSUB,
            "topic": f"public.{symbol}.liquidation_orders"
        })

    @is_future_order
    async def sub_future_contract_info(self, symbol):
        """合约信息变动"""
        await self.ws.send_request({
            "op": WebSocketOP.SUB,
            "topic": f"public.{symbol}.contract_info"
        })

    @is_future_order
    async def unsub_future_contract_info(self, symbol):
        await self.ws.send_request({
            "op": WebSocketOP.UNSUB,
            "topic": f"public.{symbol}.contract_info"
        })

    @is_future_order
    async def sub_future_trigger_order(self, symbol):
        """计划委托订单更新"""
        await self.ws.send_request({
            "op": WebSocketOP.SUB,
            "topic": f"trigger_order.{symbol}"
        })

    @is_future_order
    async def unsub_future_trigger_order(self, symbol):
        await self.ws.send_request({
            "op": WebSocketOP.UNSUB,
            "topic": f"trigger_order.{symbol}"
        })


    ########################
    ### 指数/基差数据
    ########################
    @is_index
    async def sub_index(self, symbol, period=constants.KLINE_INTERVAL_1HOUR):
        """
        K线数据
        :param symbol:  支持大小写，"BTC-USD","ETH-USD"...
        :param period: 仅支持小写,1min, 5min, 15min, 30min, 60min,4hour,1day, 1mon
        :return:
        """
        await self.ws.send_request({
            WebSocketOP.SUB: f"market.{symbol}.index.{period}"
        })

    @is_index
    async def req_index(self, symbol, start: int, end: int, period=constants.KLINE_INTERVAL_1HOUR):
        """
        请求K线数据
        :param symbol:
        :param start:
        :param end:
        :param period:
        :return:
        """
        await self.ws.send_request({
            WebSocketOP.REQ: f"market.{symbol}.index.{period}",
            "from": start,
            "to": end
        })

    @is_index
    async def sub_premium_index(self, symbol, period=constants.KLINE_INTERVAL_1DAY):
        """
        溢价K线数据
        :param symbol:
        :param period:
        :return:
        """
        await self.ws.send_request({
            WebSocketOP.SUB: f"market.{symbol}.premium_index.{period}"
        })

    @is_index
    async def req_premium_index(self, symbol, start: int, end: int, period=constants.KLINE_INTERVAL_1DAY):
        """
        请求溢价K线数据
        :param symbol:
        :param start:
        :param end:
        :param period:
        :return:
        """
        await self.ws.send_request({
            WebSocketOP.REQ: f"market.{symbol}.premium_index.{period}",
            "from": start,
            "to": end
        })

    @is_index
    async def sub_estimated_funding_rate(self, symbol, period=constants.KLINE_INTERVAL_60MINUTE):
        """
        预测基金费率K线
        """
        await self.ws.send_request({
            WebSocketOP.SUB: f"market.{symbol}.estimated_rate.{period}"
        })

    @is_index
    async def req_estimated_funding_rate(self, symbol, start: int, end: int, period=constants.KLINE_INTERVAL_60MINUTE):
        await self.ws.send_request({
            WebSocketOP.REQ: f"market.{symbol}.estimated_rate.{period}",
            "from": start,
            "to": end
        })

    @is_index
    async def sub_basis_data(self, symbol, period=constants.KLINE_INTERVAL_1DAY,
                                         price_type=constants.BasisPriceType.OPEN):
        """
        基差数据
        """
        await self.ws.send_request({
            WebSocketOP.SUB: f"market.{symbol}.basis.{period}.{price_type}"
        })

    @is_index
    async def req_basis_data(self, symbol, start: int, end: int, period=constants.KLINE_INTERVAL_1DAY,
                                         price_type=constants.BasisPriceType.OPEN):
        await self.ws.send_request({
            WebSocketOP.REQ: f"market.{symbol}.basis.{period}.{price_type}",
            "from": start,
            "to": end
        })

    @is_index
    async def sub_mark_price(self, symbol, period=constants.KLINE_INTERVAL_1DAY):
        """
        标记价格K线
        """
        await self.ws.send_request({
            WebSocketOP.SUB: f"market.{symbol}.mark_price.{period}"
        })

    @is_index
    async def req_mark_price(self, symbol, start: int, end: int, period=constants.KLINE_INTERVAL_1DAY):
        await self.ws.send_request({
            WebSocketOP.REQ: f"market.{symbol}.mark_price.{period}",
            "from": start,
            "to": end
        })

    ########################
    ### 系统状态
    ########################
    @is_system_status
    async def sub_system_status(self, service: str = "swap"):
        """
        :param service:
        swap - 币本位永续
        linear-swap - U本位永续
        futures - 交割
        :return:
        """
        await self.ws.send_request({
            "op": WebSocketOP.SUB,
            "topic": f"public.{service}.heartbeat"
        })














