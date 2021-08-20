from typing import Optional, Dict
from abc import ABC, abstractmethod
from datetime import datetime
from urllib.parse import urlparse

import aiohttp

from common.okex.tools import generate_signature
from common.okex.exceptions import OkexAPIException
from common.dict_util import package_data, remove_key
from common.okex.constants import *
from common.models import Result
from common.okex.error_code import ERROR_CODE


class BaseClient(ABC):
    API_URL = "https://www.okex.com"
    # 模拟盘
    SIMULATED_API_URL = "https://www.okex.com"

    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None,
                 passphrase: Optional[str] = None, simulated=False):
        self._API_KEY = api_key
        self._API_SECRET = api_secret
        self._passphrase = passphrase
        self.session = self._init_session()
        self._simulated = simulated

        if simulated:
            self._api_url = self.SIMULATED_API_URL
        else:
            self._api_url = self.API_URL

    def _get_headers(self) -> Dict:
        headers = {
            "OK-ACCESS-KEY": self._API_KEY,
            "OK-ACCESS-TIMESTAMP": datetime.utcnow().isoformat("T", "milliseconds") + 'Z',
            "OK-ACCESS-PASSPHRASE": self._passphrase,
            'Content-Type': 'application/json'
        }
        if self._simulated:
            headers['x-simulated-trading'] = "1"
        return headers

    @abstractmethod
    def _init_session(self):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def create(cls, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        raise NotImplementedError

    def _create_account_api_uri(self, path: str) -> str:
        return f"{self._api_url}/api/v5/account/{path}"

    def _create_asset_api_uri(self, path: str) -> str:
        return f"{self._api_url}/api/v5/asset/{path}"

    def _create_market_api_uri(self, path: str) -> str:
        return f"{self._api_url}/api/v5/market/{path}"

    def _create_public_api_uri(self, path: str) -> str:
        return f"{self._api_url}/api/v5/public/{path}"

    def _create_trade_api_uri(self, path: str) -> str:
        return f"{self._api_url}/api/v5/trade/{path}"

    def _create_sub_account_api_uri(self, path: str) -> str:
        return f"{self._api_url}/api/v5/users/subaccount/{path}"

    def _create_system_api_uri(self, path: str) -> str:
        return f"{self._api_url}/api/v5/system/{path}"


class AsyncClient(BaseClient):
    def _init_session(self):
        return aiohttp.ClientSession(trust_env=True)

    @classmethod
    def create(cls, api_key: Optional[str] = None, api_secret: Optional[str] = None, passphrase: Optional[str] = None,
               simulated=False):
        return cls(api_key, api_secret, passphrase, simulated)

    async def close_connection(self):
        if self.session:
            await self.session.close()
            self.session = None

    async def _request(self, method: str, uri: str, params=None, data=None, signed=False) -> Result:
        kwargs = {
            "json": data,
            "params": params
        }

        headers = self._get_headers()
        if signed:
            headers['OK-ACCESS-SIGN'] = generate_signature(
                method, urlparse(uri).path, headers['OK-ACCESS-TIMESTAMP'], params, data, self._API_SECRET
            )
        kwargs['headers'] = headers
        async with getattr(self.session, method)(uri, **kwargs) as response:
            return await self._handler_response(response)

    @staticmethod
    async def _handler_response(response: aiohttp.ClientResponse) -> Result:
        if not str(response.status).startswith('2'):
            raise OkexAPIException(response, await response.text())
        try:
            result = await response.json()
            if result['code'] != "0":
                error_msg = result['msg'] if result['msg'] else ERROR_CODE[int(result['code'])]
                raise OkexAPIException(response, error_msg, result['code'], result['data'])
            return Result(result['code'], None, result['msg'], result['data'])
        except ValueError:
            raise OkexAPIException(response, f'Invalid Response: {await response.text()}')

    async def _request_asset_api(self, method="get", path=None, params=None, data=None):
        uri = self._create_asset_api_uri(path)
        return await self._request(method, uri, params=params, data=data, signed=True)

    async def _request_account_api(self, method="get", path=None, params=None, data=None) -> Result:
        uri = self._create_account_api_uri(path)
        return await self._request(method, uri, params=params, data=data, signed=True)

    async def _request_market_api(self, method="get", path=None, params=None, data=None):
        uri = self._create_market_api_uri(path)
        return await self._request(method, uri, params=params, data=data)

    async def _request_public_api(self, method="get", path=None, params=None):
        uri = self._create_public_api_uri(path)
        return await self._request(method, uri, params=params)

    async def _request_system_api(self, method="get", path=None, params=None):
        uri = self._create_system_api_uri(path)
        return await self._request(method, uri, params=params)

    async def _request_trade_api(self, method="get", path=None, params=None, data=None):
        uri = self._create_trade_api_uri(path)
        return await self._request(method, uri, params=params, data=data, signed=True)

    ##########################
    # 资金
    ##########################
    async def currencies(self):
        # 获取平台所有币种列表。并非所有币种都可被用于交易。
        return await self._request_asset_api(path="currencies")

    async def asset_balances(self, ccy: str = None):
        # 获取资金账户所有资产列表，查询各币种的余额、冻结和可用等信息(只返回余额大于0的币资产信息)
        params = package_data(remove_key(locals()))
        return await self._request_asset_api(path="balances", params=params)

    async def transfer(self, ccy, amt, _from, to, _type=0, subAcct=None, instId=None, toInstId=None):
        # 资金划转
        # 支持母账户的资金账户划转到交易账户，母账户到子账户的资金账户和交易账户划转。不支持子账户和子账户之间直接划转
        """
        ccy	String	是	币种，如 USDT
        amt	String	是	划转数量
        type	String	否
        0：账户内划转
        1：母账户转子账户
        2：子账户转母账户
        默认为0。
        from	String	是	转出账户
        1：币币账户 3：交割合约 5：币币杠杆账户 6：资金账户 9：永续合约账户 12：期权合约 18：统一账户
        to	String	是	转入账户
        1：币币账户 3：交割合约 5：币币杠杆账户 6：资金账户 9：永续合约账户 12：期权合约 18：统一账户
        subAcct	String	可选	子账户名称，type 为1或2：subAcct 为必填项
        instId	String	可选	币币杠杆转出币对（如 BTC-USDT）或者转出合约的 underlying（如 BTC-USD）
        toInstId	String	可选	币币杠杆转入币对（如 BTC-USDT）或者转入合约的 underlying（如 BTC-USD）
        """
        if _type in (1, 2):
            assert subAcct != None
        params = package_data(
            remove_key(locals()),
            {
                "_from": "from",
                "_type": "type"
            }
        )
        return await self._request_asset_api(method="post", path="transfer", data=params)

    ##########################
    # 账户
    ##########################
    async def account_balance(self, ccy=None):
        # 获取账户中资金余额信息
        params = package_data(remove_key(locals()))
        return await self._request_account_api(path="balance", params=params)

    async def positions(self, instType: InstType = None, instId=None, posId=None):
        """
        查看持仓信息
        获取该账户下拥有实际持仓的信息。账户为单向持仓模式会显示净持仓（net），账户为双向持仓模式下会分别返回多头（long）或空头（short）的仓位。
        instType	String	否	产品类型
                        MARGIN：币币杠杆
                        SWAP：永续合约
                        FUTURES：交割合约
                        OPTION：期权
                        instType和instId同时传入的时候会校验instId与instType是否一致，结果返回instId的持仓信息
        instId	String	否	交易产品ID，如：BTC-USD-190927-5000-C
                            支持多个instId查询，半角逗号分隔。instId个数不超过10个
        posId	String	否	持仓ID
                            支持多个posId查询（不超过20个），逗号分割
        """
        params = package_data(remove_key(locals()))
        return await self._request_account_api(path="positions", params=params)

    async def account_position_risk(self, instType: InstType = None):
        """
        查看账户整体风险。
        instType	String	否	产品类型
                        MARGIN：币币杠杆
                        SWAP：永续合约
                        FUTURES：交割合约
                        OPTION：期权
        """
        params = package_data(remove_key(locals()))
        return await self._request_account_api(path="account-position-risk", params=params)

    async def account_config(self) -> Result:
        """
        查看当前账户的配置信息
        """
        return await self._request_account_api(path="config")

    async def set_position_mode(self, posMode: PosMode):
        """
        设置持仓模式
        交割和永续合约支持双向持仓模式和单向持仓模式。单向持仓只会有一个方向的仓位；双向持仓可以分别持有多、空2个方向的仓位。

        posMode	String	是	持仓方式
                            long_short_mode：双向持仓 net_mode：单向持仓
                            仅适用交割/永续
        """
        data = package_data(remove_key(locals()))
        return await self._request_account_api("post", "set-position-mode", data=data)

    async def max_withdrawal(self, ccy):
        """
        查看账户最大可转余额
        当指定币种时会返回该币种的最大可划转数量，不指定币种会返回所有拥有的币种资产可划转数量
        """
        params = package_data(remove_key(locals()))
        return await self._request_account_api(path="max-withdrawal", params=params)

    ##########################
    # 行情
    ##########################
    async def tickers(self, instType: InstType, uly=None):
        """
        获取所有产品行情信息
        instType	String	是	产品类型
                                SPOT：币币
                                SWAP：永续合约
                                FUTURES：交割合约
                                OPTION：期权
        uly	String	否	合约标的指数，仅适用于交割/永续/期权 ，如 BTC-USD
        """
        params = package_data(remove_key(locals()))
        return await self._request_market_api(path="tickers", params=params)

    async def ticker(self, instId):
        """
        获取单个产品行情信息
        instId	String	是	产品ID，如 BTC-USD-SWAP
        """
        params = package_data(remove_key(locals()))
        return await self._request_market_api(path="ticker", params=params)

    async def index_ticker(self, quoteCcy=None, instId=None):
        """
        获取指数行情数据

        quoteCcy	String	可选	指数计价单位， 目前只有 USD/USDT/BTC为计价单位的指数，quoteCcy和instId必须填写一个
        instId	String	可选	指数，如 BTC-USD
        """
        params = package_data(remove_key(locals()))
        return await self._request_market_api(path="index-tickers", params=params)

    async def books(self, instId, sz=None):
        """
        获取产品深度列表
        instId	String	是	产品ID，如 BTC-USD-190927-5000-C
        sz	String	否	深度档位数量，最大值可传400，即买卖深度共800条，不填写此参数，默认返回1档深度数据
        """
        params = package_data(remove_key(locals()))
        return await self._request_market_api(path="books", params=params)

    async def trades(self, instId, limit=100):
        """
        查询市场上的成交信息数据
        instId	String	是	产品ID，如 BTC-USD
        limit	String	否	分页返回的结果集数量，最大为500，不填默认返回100条
        """
        params = package_data(remove_key(locals()))
        return await self._request_market_api(path="trades", params=params)

    ##########################
    # 公共数据
    ##########################
    async def instruments(self, instType: InstType, uly=None, instId=None):
        """
        获取所有可交易产品的信息列表
        instType	String	是	产品类型
                                SPOT：币币
                                MARGIN：币币杠杆
                                SWAP：永续合约
                                FUTURES：交割合约
                                OPTION：期权
        uly	String	可选	合约标的指数，仅适用于交割/永续/期权，期权必填
        instId	String	否	产品ID
        """
        params = package_data(remove_key(locals()))
        return await self._request_public_api(path="instruments", params=params)

    async def open_interest(self, instType: InstType, uly=None, instId=None):
        """
        查询单个交易产品的市场的持仓总量
        instType	String	是	产品类型
                                SWAP：永续合约
                                FUTURES：交割合约
                                OPTION：期权
        uly	String	否	合约标的指数，仅适用于交割/永续/期权，期权必填
        instId	String	否	产品ID，如 BTC-USD-180216，仅适用于交割/永续/期权
        """
        params = package_data(remove_key(locals()))
        return await self._request_public_api(path="open-interest", params=params)

    async def funding_rate(self, instId):
        """
        获取永续合约当前资金费率
        instId	String	是	产品ID ，如 BTC-USD-SWAP，仅适用于永续
        """
        params = package_data(remove_key(locals()))
        return await self._request_public_api(path="funding-rate", params=params)

    async def time(self):
        return await self._request_public_api(path="time")

    async def underlying(self, instType: InstType):
        """
        获取合约衍生品标的指数

        instType	String	是	产品类型
                                SWAP：永续合约
                                FUTURES：交割合约
                                OPTION：期权
        """
        assert instType in (InstType.SWAP, InstType.FUTURES, InstType.OPTION)
        params = package_data(remove_key(locals()))
        return await self._request_public_api(path="underlying", params=params)

    ##########################
    # 系统
    ##########################
    async def status(self, state: SystemState = None):
        """
        获取系统升级事件的状态
        state	String	No	系统的状态，scheduled:等待中 ; ongoing:进行中 ; completed:已完成 canceled: 已取消
                                        不填写此参数，默认返回 等待中和进行中 的数据
        """
        params = package_data(remove_key(locals()))
        return await self._request_system_api(path="status", params=params)

    ##########################
    # 交易
    ##########################
    async def create_order(self, instId, tdMode: TradeMode, side: Side, ordType: OrderType, sz, ccy=None, clOrdId=None,
                           tag=None, posSide: PosSide = None, px=None, reduceOnly: bool = None):
        """
        下单
        instId	String	是	产品ID，如 BTC-USD-190927-5000-C
        tdMode	String	是	交易模式
                            保证金模式：isolated：逐仓 ；cross：全仓
                            非保证金模式：cash：非保证金
        ccy	String	否	保证金币种，仅适用于单币种保证金模式下的全仓杠杆订单
        clOrdId	String	否	客户自定义订单ID
                            字母（区分大小写）与数字的组合，可以是纯字母、纯数字且长度要在1-32位之间。
        tag	String	否	订单标签
                        字母（区分大小写）与数字的组合，可以是纯字母、纯数字，且长度在1-8位之间。
        side	String	是	订单方向 buy：买 sell：卖
        posSide	String	可选	持仓方向 在双向持仓模式下必填，且仅可选择 long 或 short
        ordType	String	是	订单类型
                            market：市价单
                            limit：限价单
                            post_only：只做maker单
                            fok：全部成交或立即取消
                            ioc：立即成交并取消剩余
                            optimal_limit_ioc：市价委托立即成交并取消剩余（仅适用交割、永续）
        sz	String	是	委托数量
        px	String	可选	委托价格，仅适用于限价单
        reduceOnly	Boolean	否	是否只减仓，true 或 false，默认false
                                仅适用于币币杠杆订单
        """
        data = package_data(remove_key(locals()))
        return await self._request_trade_api("post", "order", data=data)

    async def batch_create_order(self, orders_data: list):
        return await self._request_trade_api("post", "batch-orders", data=orders_data)

    async def cancel_order(self, instId, ordId=None, clOrdId=None):
        """
        撤销订单
        instId	String	是	产品ID，如 BTC-USD-190927
        ordId	String	可选	订单ID， ordId和clOrdId必须传一个，若传两个，以ordId为主
        clOrdId	String	可选	用户自定义ID
        """
        assert not (ordId is None and clOrdId is None)
        data = package_data(remove_key(locals()))
        return await self._request_trade_api("post", "cancel-order", data=data)

    async def batch_cancel_orders(self, orders_data: list):
        """
        批量撤销订单
        """
        return await self._request_trade_api("post", "cancel-batch-orders", data=orders_data)

    async def amend_order(self, instId, cxlOnFail=False, ordId=None, clOrdId=None, reqId=None, newSz=None, newPx=None):
        """
        修改当前未成交的挂单
        instId	String	是	产品ID
        cxlOnFail	Boolean	否	false：不自动撤单 true：自动撤单 当订单修改失败时，该订单是否需要自动撤销。默认为false
        ordId	String	可选	订单ID， ordId和clOrdId必须传一个，若传两个，以ordId为主
        clOrdId	String	可选	用户自定义order ID
        reqId	String	否	用户自定义修改事件ID
                            字母（区分大小写）与数字的组合，可以是纯字母、纯数字且长度要在1-32位之间。
        newSz	String	可选	修改的新数量，newSz和newPx不可同时为空。对于部分成交订单，该数量应包含已成交数量。
                            当修改的数量<=该笔订单已成交数量时，该订单的状态会修改为完全成交状态。
        newPx	String	可选	修改的新价格
        """
        assert not (ordId is None and clOrdId is None)
        assert not (newSz is None and newPx is None)
        data = package_data(remove_key(locals()))
        return await self._request_trade_api("post", "amend-order", data=data)

    async def batch_amend_orders(self, orders_data: list):
        """
        批量修改订单
        """
        return await self._request_trade_api("post", "amend-batch-orders", data=orders_data)

    async def close_position(self, instId, mgnMode: MgnMode, posSide: PosSide = None, ccy=None):
        """
        市价平掉某个合约下的全部持仓
        instId	String	是	产品ID
        posSide	String	可选	持仓方向
                            单向持仓模式下：可不填写此参数，默认值net，如果填写，仅可以填写net
                            双向持仓模式下： 必须填写此参数，且仅可以填写 long：平多 ，short：平空
        mgnMode	String	是	保证金模式
                            全仓：cross ； 逐仓： isolated
        ccy	String	可选	保证金币种，单币种保证金模式的全仓币币杠杆平仓必填
        """
        data = package_data(remove_key(locals()))
        return await self._request_trade_api("post", "close-position", data=data)

    async def order_info(self, instId, ordId=None, clOrdId=None):
        """
        获取订单信息
        """
        assert not (ordId is None and clOrdId is None)
        params = package_data(remove_key(locals()))
        return await self._request_trade_api(path="order", params=params)

    async def pending_orders(self, instType: InstType = None, uly=None, instId=None, ordType: OrderType = None,
                             state: OrderState = None, after=None, before=None, limit=100):
        """
        获取当前账户下所有未成交订单信息
        instType	String	否	产品类型
                                SPOT：币币
                                MARGIN：币币杠杆
                                SWAP：永续合约
                                FUTURES：交割合约
                                OPTION：期权
        uly	String	否	合约标的指数
        instId	String	否	产品ID，如BTC-USD-200927
        ordType	String	否	订单类型
                            market：市价单
                            limit：限价单
                            post_only：只做maker单
                            fok：全部成交或立即取消
                            ioc：立即成交并取消剩余
        optimal_limit_ioc：市价委托立即成交并取消剩余（仅适用交割、永续）
        state	String	否	订单状态
                            live：等待成交
                            partially_filled：部分成交
        after	String	否	请求此ID之前（更旧的数据）的分页内容，传的值为对应接口的ordId
        before	String	否	请求此ID之后（更新的数据）的分页内容，传的值为对应接口的ordId
        limit	String	否	返回结果的数量，默认100条
        """
        params = package_data(remove_key(locals()))
        return await self._request_trade_api(path="orders-pending", params=params)

    async def orders_history(self, instType: InstType, uly: str = None, instId=None, ordType: OrderType = None,
                             state: OrderState = None, category: OrderCategory = None, after=None, before=None,
                             limit=100):
        """
        获取最近7天的已经完结状态的订单数据，已经撤销的未成交单 只保留2小时
        uly	String	否	合约标的指数
        instId	String	否	产品ID，如BTC-USD-190927
        after	String	否	请求此ID之前（更旧的数据）的分页内容，传的值为对应接口的ordId
        before	String	否	请求此ID之后（更新的数据）的分页内容，传的值为对应接口的ordId
        """
        params = package_data(remove_key(locals()))
        return await self._request_trade_api(path="orders-history", params=params)

    async def fills(self, instType: InstType = None, uly=None, instId=None, ordId=None, after=None, before=None, limit=100):
        """
        获取近3个月订单成交明细信息
        """
        params = package_data(remove_key(locals()))
        return await self._request_trade_api(path="fills", params=params)








