import gzip
import json
import logging
import asyncio
from functools import partial
from typing import Optional
import aiohttp
import time
from aiohttp.web_ws import WSMessage

from common.exceptions import OkexWebSocketError
from common.okex.tools import generate_signature
from common.okex.constants import *
from common.dict_util import remove_key


class ReconnectingWebSocket:
    # 如果连接成功后30s未订阅或订阅后30s内服务器未向用户推送数据，系统会自动断开连接
    TIMEOUT = 20

    # 实盘
    WS_PUBLIC_URL = "wss://ws.okex.com:8443/ws/v5/public"
    WS_PRIVATE_URL = "wss://ws.okex.com:8443/ws/v5/private"
    # 模拟盘
    SIMULATED_WS_PUBLIC_URL = "wss://ws.okex.com:8443/ws/v5/public?brokerId=9999"
    SIMULATED_WS_PRIVATE_URL = "wss://wspap.okex.com:8443/ws/v5/private?brokerId=9999"

    def __init__(self, public=True, proxy=None, api_key: Optional[str] = None, api_secret: Optional[str] = None,
                 api_passphrase: Optional[str] = None, simulated=False):
        self._public = public
        self.ws: aiohttp.ClientWebSocketResponse = None
        self._session: aiohttp.ClientSession = None
        self._conn = None
        self._proxy = proxy
        self._api_key = api_key
        self._api_secret = api_secret
        self._api_passphrase = api_passphrase
        self._connected = False

        # 用于断开重连时再次订阅
        self._sub_channel_msg = []

        # 以下认证相关变量
        self._already_send_auth = False
        # 确保login消息处理完毕
        self._complete_auth = False
        # 通知事件等待者已完成认证
        self.auth_complete_event = asyncio.Event()

        self._simulated = simulated

    @property
    def url(self) -> str:
        if self._simulated:
            return self.SIMULATED_WS_PUBLIC_URL if self._public else self.SIMULATED_WS_PRIVATE_URL
        else:
            return self.WS_PUBLIC_URL if self._public else self.WS_PRIVATE_URL

    @property
    def need_send_auth(self) -> bool:
        return not self._public and not self._already_send_auth

    @property
    def need_reconnected(self) -> bool:
        return self.ws is None or self.ws.closed or not self._connected

    @property
    def api_key(self):
        return self._api_key

    async def __aenter__(self):
        if self.need_reconnected:
            self._reset_flag()
            await self._reconnect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.ws:
            await self.ws.close()
            self.ws = None
        if self._conn:
            await self._conn.__aexit(exc_type, exc_val, exc_tb)
        self._reset_flag()
        if self._session:
            await self._session.close()
            self._session = None

    def _package_msg(self, op: WebSocketOp, payload):
        msg = {"op": op.value}
        if isinstance(payload, dict):
            msg['args'] = [payload]
        else:
            msg['args'] = payload
        for item in msg['args']:
            for k, v in item.items():
                if isinstance(v, Enum):
                    item[k] = v.value
        return msg

    def _reset_flag(self):
        """
        连接断开后重置标志变量
        """
        # 断开后conn已经失效，必须重连
        self._conn = None
        self._connected = self._already_send_auth = self._complete_auth = False

    async def send_auth(self):
        if not self.ws:
            raise OkexWebSocketError("no binding web socket")
        if self.ws.closed:
            raise OkexWebSocketError("websocket has closed")

        timestamp = str(int(time.time()))
        payload = {
            "apiKey": self._api_key,
            "passphrase": self._api_passphrase,
            "timestamp": timestamp,
            "sign": generate_signature("GET", "/users/self/verify", timestamp, None, None, self._api_secret)
        }
        logging.debug(f"send auth msg: {payload}")
        await self.ws.send_json(self._package_msg(WebSocketOp.LOGIN, payload))
        self._already_send_auth = True

    async def _connect(self):
        logging.info(f"ws connect {self.url}")
        if not self._session or self._session.closed:
            self._session = aiohttp.ClientSession(trust_env=True)
            self._conn = None
            self.ws = None
        if not self._conn:
            self._conn = self._session.ws_connect(self.url, proxy=self._proxy)
            self.ws = None
        try:
            if not self.ws:
                self.ws = await self._conn.__aenter__()
            self._connected = True
            logging.debug(f"connect {self.url} successfully!")
        except aiohttp.client.ClientConnectorError:
            logging.error(f"connect to ws server error! url: {self.url}")

    async def _connected_callback(self):
        if self.need_send_auth:
            await self.send_auth()
            logging.debug("wait for auth response")
            while self._complete_auth is False:
                await self.recv()
            self.auth_complete_event.set()
            logging.debug("auth complete!")
        if self._sub_channel_msg:
            msg = self._package_msg(WebSocketOp.SUB, self._sub_channel_msg)
            await self.ws.send_json(msg)

    async def _reconnect(self):
        logging.warning("reconnecting web socket right now!")
        await self._connect()
        await self._connected_callback()

    async def recv(self):
        res = None
        if self.ws is None:
            raise OkexWebSocketError("web socket connection not connected yet")
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
                if res.get("event") == WebSocketEvent.LOGIN and res.get("code") == '0':
                    self._complete_auth = True
            elif res == "pong":
                res = None

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
        elif msg.type == aiohttp.WSMsgType.CLOSE:
            data = None
        else:
            raise OkexWebSocketError(f"invalid msg type: {msg.type}")

        logging.debug(f"receive msg: {data}")
        return data

    async def send_request(self, payload):
        if self._connected is False or self.ws is None or self.ws.closed:
            await self._connect()
            await self._connected_callback()
        logging.debug(f"send msg: {payload}")
        await self.ws.send_json(payload)

    async def sub(self, payload):
        msg = self._package_msg(WebSocketOp.SUB, payload)
        if msg not in self._sub_channel_msg:
            self._sub_channel_msg.append(msg)
        await self.send_request(msg)

    async def unsub(self, payload):
        msg = self._package_msg(WebSocketOp.UNSUB, payload)
        if msg in self._sub_channel_msg:
            self._sub_channel_msg.remove(msg)
        await self.send_request(msg)

    async def sub_or_unsub(self, payload, op: WebSocketOp):
        if op == WebSocketOp.SUB:
            await self.sub(payload)
        elif op == WebSocketOp.UNSUB:
            await self.unsub(payload)
        else:
            raise Exception(f"unsupported op: {op.value}")


class OkexSocketManager:
    def __init__(self, proxy=None, api_key: Optional[str] = None, api_secret: Optional[str] = None,
                 api_passphrase: Optional[str] = None):
        self.ws: ReconnectingWebSocket = None
        self._create_ws = partial(
            ReconnectingWebSocket, proxy=proxy, api_key=api_key, api_secret=api_secret, api_passphrase=api_passphrase)

    def set_public_simulated_socket(self) -> "OkexSocketManager":
        self.ws = self._create_ws(public=True, simulated=True)
        return self

    def set_private_simulated_socket(self) -> "OkexSocketManager":
        self.ws = self._create_ws(public=False, simulated=True)
        return self

    def set_public_socket(self) -> "OkexSocketManager":
        self.ws = self._create_ws(public=True, simulated=False)
        return self

    def set_private_socket(self) -> "OkexSocketManager":
        self.ws = self._create_ws(public=False, simulated=False)
        return self

    ######################################################
    # 公共频道                                             #
    ######################################################
    async def sub_instruments(self, instType: InstType, op=WebSocketOp.SUB):
        # 产品频道
        # 首次订阅推送产品的全量数据；后续当有产品状态变化时（如期货交割、期权行权、新合约/币对上线、人工暂停/恢复交易等），推送产品的增量数据。
        await self.ws.sub_or_unsub({
            "channel": "instruments",
            "instType": instType
        }, op)

    async def sub_tickers(self, instId: str, op=WebSocketOp.SUB):
        # 行情频道
        # 获取产品的最新成交价、买一价、卖一价和24小时交易量等信息，每100ms有数据更新推送一次数据
        await self.ws.sub_or_unsub({
            "channel": "tickers",
            "instId": instId
        }, op)

    async def sub_open_interest(self, instId: str, op=WebSocketOp.SUB):
        """
        持仓总量频道
        获取持仓总量，每3s有数据更新推送一次数据
        """
        await self.ws.sub_or_unsub({
            "channel": "open-interest",
            "instId": instId
        }, op)

    async def sub_kline(self, kline_type: KlineType, instId: str, op=WebSocketOp.SUB):
        """
        K线频道
        获取产品的K线数据，每500ms推送一次数据。
        """
        await self.ws.sub_or_unsub({
            "channel": kline_type.value,
            "instId": instId
        }, op)

    async def sub_trades(self, instId: str, op=WebSocketOp.SUB):
        """
        交易频道
        获取最近的成交数据，有成交数据就推送
        """
        await self.ws.sub_or_unsub({
            "channel": "trades",
            "instId": instId
        }, op)

    async def sub_estimated_price(self, instType: InstType, uly=None, instId=None, op=WebSocketOp.SUB):
        """
        预估交割/行权价格频道
        获取交割合约和期权预估交割/行权价。交割/行权预估价只有交割/行权前一小时开始推送预估交割/行权价，有价格变化就推送
        uly和instId必须指定一个
        """
        assert instType in (InstType.FUTURES, InstType.OPTION)
        assert not (uly is None and instId is None)
        payload = remove_key(locals(), "self,op")
        payload['channel'] = "estimated-price"
        await self.ws.sub_or_unsub(payload, op)

    async def sub_mark_price(self, instId: str, op=WebSocketOp.SUB):
        """
        标记价格频道
        获取标记价格，标记价格有变化时，每200ms推送一次数据，标记价格没变化时，每10s推送一次数据
        """
        await self.ws.sub_or_unsub({
            "channel": "mark-price",
            "instId": instId
        }, op)

    async def sub_mark_price_kline(self, kline_type: KlineType, instId: str, op=WebSocketOp.SUB):
        """
        标记价格K线频道
        获取标记价格的K线数据，每500ms推送一次数据
        """
        await self.ws.sub_or_unsub({
            "channel": f"mark-price-{kline_type.value}",
            "instId": instId
        }, op)

    async def sub_price_limit(self, instId: str, op=WebSocketOp.SUB):
        """
        限价频道
        获取交易的最高买价和最低卖价。限价有变化时，每5秒推送一次数据，限价没变化时，不推送数据
        """
        await self.ws.sub_or_unsub({
            "channel": "price-limit",
            "instId": instId
        }, op)

    async def sub_books(self, books_type: BooksType, instId: str, op=WebSocketOp.SUB):
        """
        深度频道
        获取深度数据，books是400档频道，books5是5档频道，books-l2-tbt是先400档后实时推送的频道，books50-l2-tbt是先50档后实时推的频道；
        books 首次推400档快照数据，以后增量推送，即每100毫秒有深度变化推送一次变化的数据
        books5首次推5档快照数据，以后定量推送，每100毫秒有深度变化推送一次5档数据，即每次都推送5档数据
        books-l2-tbt 首次推400档快照数据，以后增量推送，即有深度有变化推送一次变化的数据
        books50-l2-tbt 首次推50档快照数据，以后增量推送，即有深度有变化推送一次变化的数据
        """
        await self.ws.sub_or_unsub({
            "channel": books_type.value,
            "instId": instId
        }, op)

    async def sub_opt_summary(self, uly: str, op=WebSocketOp.SUB):
        """
        期权定价频道
        获取所有期权合约详细定价信息，一次性推送所有
        """
        await self.ws.sub_or_unsub({
            "channel": "opt-summary",
            "uly": uly
        }, op)

    async def sub_funding_rate(self, instId: str, op=WebSocketOp.SUB):
        """
        资金费率频道
        获取合约资金费率，一分钟推送一次数据
        """
        await self.ws.sub_or_unsub({
            "channel": "funding-rate",
            "instId": instId
        }, op)

    async def sub_index_kline(self, kline_type: KlineType, instId: str, op=WebSocketOp.SUB):
        """
        指数K线频道
        获取指数的K线数据，每500ms推送一次数据。
        """
        await self.ws.sub_or_unsub({
            "channel": f"index-{kline_type.value}",
            "instId": instId
        }, op)

    async def sub_index_tickers(self, instId: str, op=WebSocketOp.SUB):
        """
        指数行情频道
        获取指数的行情数据
        """
        await self.ws.sub_or_unsub({
            "channel": "index-tickers",
            "instId": instId
        }, op)

    async def sub_status(self, op=WebSocketOp.SUB):
        """
        Status 频道
        获取系统维护的状态，当系统维护状态改变时推送。首次订阅：”推送最新一条的变化数据“；后续每次有状态变化，推送变化的内容
        """
        await self.ws.sub_or_unsub({
            "channel": "status"
        }, op)

    ######################################################
    # 私有频道                                             #
    ######################################################
    async def sub_account(self, ccy: str, op=WebSocketOp.SUB):
        """
        账户频道
        获取账户信息，首次订阅按照订阅维度推送数据，此外，当下单、撤单等事件触发时，推送数据以及按照订阅维度定时推送数据
        """
        await self.ws.sub_or_unsub({
            "channel": "account",
            "ccy": ccy
        }, op)

    async def sub_positions(self, instType: InstType, uly: str = None, instId: str = None, op=WebSocketOp.SUB):
        """
        持仓频道
        获取持仓信息，首次订阅按照订阅维度推送数据，此外，当下单、撤单等事件触发时，推送数据以及按照订阅维度定时推送数据
        """
        assert not (uly is None and instId is None)
        payload = remove_key(locals(), "self,op")
        payload['channel'] = "positions"
        await self.ws.sub_or_unsub(payload, op)

    async def sub_balance_and_position(self, op=WebSocketOp.SUB):
        """
        账户余额和持仓频道
        获取账户余额和持仓信息，首次订阅按照订阅维度推送数据，此外，当成交、资金划转等事件触发时，推送数据。
        该频道适用于尽快获取账户现金余额和仓位资产变化的信息。
        """
        await self.ws.sub_or_unsub({
            "channel": "balance_and_position",
        }, op)

    async def sub_orders(self, instType: InstType, uly=None, instId=None, op=WebSocketOp.SUB):
        """
        订单频道
        获取订单信息，首次订阅不推送，只有当下单、撤单等事件触发时，推送数据
        """
        payload = remove_key(locals(), "self,op")
        payload['channel'] = "orders"
        await self.ws.sub_or_unsub(payload, op)

    async def sub_orders_algo(self, instType: InstType, uly=None, instId=None, op=WebSocketOp.SUB):
        """
        策略委托订单频道
        获取策略委托订单，首次订阅不推送，只有当下单、撤单等事件触发时，推送数据
        """
        assert instType != instType.OPTION
        payload = remove_key(locals(), "self,op")
        payload['channel'] = "orders-algo"
        await self.ws.sub_or_unsub(payload, op)






