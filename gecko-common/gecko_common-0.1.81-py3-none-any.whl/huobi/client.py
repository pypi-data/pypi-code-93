import logging
from typing import Optional, Dict
from abc import ABC, abstractmethod
from datetime import datetime

import aiohttp

from common.huobi import constants
from .exceptions import HuobiAPIException
from common.models import Result
from .tools import generate_signature
from common.dict_util import package_data, remove_key


class BaseClient(ABC):
    # API URL
    API_URL = "https://api.huobi.pro"
    API_AWS_URL = "https://api-aws.huobi.pro"

    # 合约
    API_FUTURE_URL= "https://api.hbdm.com"

    # version
    SPOT_API_VERSION = 'v1'
    SPOT_API_VERSION2 = 'v2'

    FUTURE_API_VERSION = "v1"

    COIN_MARGINED_API_VERSION = "v1"

    USD_MARGINED_API_VERSION = "v1"

    # ACCOUNT_TYPE
    SPOT = "spot"   # 现货
    OTC = "otc"
    MARGIN = "margin"   # 逐仓杠杆账户，该账户类型以subType区分具体币种对账户
    SUPER_MARGIN = "super-margin"   # 全仓杠杆账户
    POINT = "point"     # 点卡
    MINEPOOL = "minepool"   # 矿池账户
    ETF = "etf"     # ETF账户

    KLINE_INTERVAL_1MINUTE = '1min'
    KLINE_INTERVAL_5MINUTE = '5min'
    KLINE_INTERVAL_15MINUTE = '15min'
    KLINE_INTERVAL_30MINUTE = '30min'
    KLINE_INTERVAL_60MINUTE = '60min'
    KLINE_INTERVAL_4HOUR = '4hour'
    KLINE_INTERVAL_1DAY = '1day'
    KLINE_INTERVAL_1WEEK = '1week'
    KLINE_INTERVAL_1MONTH = '1mon'
    KLINE_INTERVAL_1YEAR = '1year'

    DEPTH_TYPE_0 = "step0"
    DEPTH_TYPE_1 = "step1"
    DEPTH_TYPE_2 = "step2"
    DEPTH_TYPE_3 = "step3"
    DEPTH_TYPE_4 = "step4"
    DEPTH_TYPE_5 = "step5"

    TRANSFER_FUTURES_TO_PRO = "futures-to-pro"
    TRANSFER_PRO_TO_FUTURES = "pro-to-futures"

    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        self.API_KEY = api_key
        self.API_SECRET = api_secret
        self.session = self._init_session()

    @abstractmethod
    def _init_session(self):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def create(cls, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        raise NotImplementedError

    def _create_spot_api_uri(self, path: str, version: str = SPOT_API_VERSION) -> str:
        return f"{self.API_URL}/{version}/{path}"

    def _create_spot_basic_api_uri(self, path: str, version: str = SPOT_API_VERSION) -> str:
        return f"{self.API_URL}/{version}/common/{path}"

    def _create_spot_market_api_uri(self, path: str) -> str:
        return f"{self.API_URL}/market/{path}"

    def _create_spot_account_api_uri(self, path: str, version: str = SPOT_API_VERSION) -> str:
        return f"{self.API_URL}/{version}/account/{path}"

    def _create_spot_sub_account_api_uri(self, path: str, version: str = SPOT_API_VERSION) -> str:
        return f"{self.API_URL}/{version}/subuser/{path}"

    def _create_spot_order_api_uri(self, path: str, version: str = SPOT_API_VERSION) -> str:
        return f"{self.API_URL}/{version}/order/{path}"

    def _create_spot_margin_api_uri(self, path: str, version: str = SPOT_API_VERSION) -> str:
        return f"{self.API_URL}/{version}/margin/{path}"

    def _create_spot_cross_margin_api_uri(self, path: str, version: str = SPOT_API_VERSION) -> str:
        return f"{self.API_URL}/{version}/cross-margin/{path}"

    # 交割合约
    def _create_future_api_uri(self, path: str, version: str = FUTURE_API_VERSION) -> str:
        return f"{self.API_FUTURE_URL}/api/{version}/{path}"

    # 币本位合约
    def _create_coin_margined_api_uri(self, path: str, version: str = COIN_MARGINED_API_VERSION) -> str:
        return f"{self.API_FUTURE_URL}/swap-api/{version}/{path}"

    # U本位合约
    def _create_usd_margined_api_uri(self, path: str, version: str = USD_MARGINED_API_VERSION) -> str:
        return f"{self.API_FUTURE_URL}/linear-swap-api/{version}/{path}"

    @staticmethod
    def _get_headers() -> Dict:
        return {'Content-type': 'application/x-www-form-urlencoded', 'Accept': 'application/json'}

    @staticmethod
    def _post_headers() -> Dict:
        return {'Accept': 'application/json', 'Content-type': 'application/json'}


class AsyncClient(BaseClient):
    def _init_session(self):
        return aiohttp.ClientSession(trust_env=True)

    async def close_connection(self):
        if self.session:
            await self.session.close()

    @classmethod
    def create(cls, api_key: Optional[str] = None, api_secret: Optional[str] = None) -> "AsyncClient":
        client = cls(api_key, api_secret)
        return client

    async def _request(self, method: str, uri: str, params=None, data=None, signed=False) -> Result:
        kwargs = dict()
        kwargs['timeout'] = 10
        kwargs['json'] = data

        if signed:
            timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
            params = params if params else {}
            params.update({
                "AccessKeyId": self.API_KEY,
                "SignatureMethod": "HmacSHA256",
                "SignatureVersion": "2",
                "Timestamp": timestamp
            })
            params["Signature"] = generate_signature(self.API_SECRET, method, uri, params)

        if params:
            kwargs['params'] = params

        if method == "get":
            headers = self._get_headers()
        else:
            headers = self._post_headers()
        kwargs['headers'] = headers
        logging.debug(f"uri: {uri}, kwargs: {kwargs}")
        async with getattr(self.session, method)(uri, **kwargs) as response:
            return await self._handle_response(response)

    @staticmethod
    async def _handle_response(response: aiohttp.ClientResponse) -> Result:
        """Internal helper for handling API responses from the Binance server.
        Raises the appropriate exceptions when necessary; otherwise, returns the
        response.
        """
        if not str(response.status).startswith('2'):
            raise HuobiAPIException(response, await response.text())
        try:
            result = await response.json()
            logging.debug(f"handler response: {result}")
            # 统一v1/v2返回值格式
            if "code" in result:
                if result['code'] != 200:
                    raise HuobiAPIException(response, result['message'])
                else:
                    return Result(
                        result['code'], 'ok',
                        result.get('message'), result.get("data", result.get("tick"))
                    )
            else:
                if result['status'] != 'ok':
                    error_code = result.get('err-code', result.get('err_code'))
                    raise HuobiAPIException(
                        response,
                        f"error code: {error_code}, "
                        f"error msg: {result.get('err-msg', result.get('err_msg'))}",
                        error_code
                    )
                else:
                    return Result(200, result['status'], "", result.get("data", result.get("tick")))
        except ValueError:
            raise HuobiAPIException(response, f'Invalid Response: {await response.text()}')

    async def _get(self, path, params=None, signed=False):
        return await self._request('get', path, params, signed=signed)

    async def _post(self, path, data=None, signed=True):
        return await self._request('post', path, data=data, signed=signed)

    async def _request_spot_basic_api(self, method="get", path=None, version=BaseClient.SPOT_API_VERSION, params=None):
        uri = self._create_spot_basic_api_uri(path, version)
        return await self._request(method, uri, params)

    async def _request_spot_market_api(self, method="get", path=None, params=None):
        uri = self._create_spot_market_api_uri(path)
        return await self._request(method, uri, params)

    async def _request_spot_account_api(self, method="get", path=None, version=BaseClient.SPOT_API_VERSION,
                                        params=None, data=None):
        uri = self._create_spot_account_api_uri(path, version)
        return await self._request(method, uri, params, data, True)

    async def _request_spot_order_api(self, method="get", path=None, version=BaseClient.SPOT_API_VERSION,
                                      params=None, data=None):
        uri = self._create_spot_order_api_uri(path, version)
        return await self._request(method, uri, params, data, True)

    async def _request_future_private_api(self, method="get", path=None, version=BaseClient.SPOT_API_VERSION,
                                        params=None, data=None):
        uri = self._create_future_api_uri(path, version)
        return await self._request(method, uri, params, data, True)

    async def _request_coin_margined_private_api(self, method="get", path=None,
                                                 version=BaseClient.COIN_MARGINED_API_VERSION, params=None, data=None):
        uri = self._create_coin_margined_api_uri(path, version)
        return await self._request(method, uri, params, data, True)

    async def _request_usd_margined_private_api(
            self, method="get", path=None, version=BaseClient.USD_MARGINED_API_VERSION, params=None, data=None
    ):
        uri = self._create_usd_margined_api_uri(path, version)
        return await self._request(method, uri, params, data, True)

    async def spot_system_status(self):
        """
        获取当前系统状态
        https://huobiapi.github.io/docs/spot/v1/cn/#cd63bde415
        """
        return await self._request("get", "https://status.huobigroup.com/api/v2/summary.json")

    async def spot_market_status(self):
        """
        获取当前市场状态
        https://huobiapi.github.io/docs/spot/v1/cn/#f80d403388
        """
        uri = self._create_spot_api_uri("market-status", version=self.SPOT_API_VERSION2)
        return await self._request("get", uri)

    async def spot_symbols(self):
        """
        获取所有交易对
        https://huobiapi.github.io/docs/spot/v1/cn/#0e505d18dc
        """
        return await self._request_spot_basic_api(path="symbols")

    async def spot_currencys(self):
        """
        获取所有币种
        https://huobiapi.github.io/docs/spot/v1/cn/#7393cc8596
        """
        return await self._request_spot_basic_api(path="currencys")

    async def spot_timestamp(self):
        return await self._request_spot_basic_api(path="timestamp")

    async def spot_kline(self, symbol: str, period, **params):
        params['symbol'] = symbol
        params['period'] = period
        return await self._request_spot_market_api(path="history/kline", params=params)

    async def spot_merged_ticker(self, symbol: str):
        """
        聚合行情（Ticker）
        此接口获取ticker信息同时提供最近24小时的交易聚合信息。
        """
        return await self._request_spot_market_api(path="detail/merged", params={"symbol": symbol})

    async def spot_tickers(self):
        """
        所有交易对的最新 Tickers
        获得所有交易对的 tickers。 shell curl "https://api.huobi.pro/market/tickers"
        此接口返回所有交易对的 ticker，因此数据量较大。
        """
        return await self._request_spot_market_api(path="tickers")

    async def spot_depth(self, symbol: str, depth_type: Optional[str] = BaseClient.DEPTH_TYPE_0, depth: Optional[int] = 20):
        """
        市场深度数据
        depth 范围 5，10，20
        当type值为‘step0’时，‘depth’的默认值为150而非20
        参数type的各值说明

        取值	说明
        step0	无聚合
        step1	聚合度为报价精度*10
        step2	聚合度为报价精度*100
        step3	聚合度为报价精度*1000
        step4	聚合度为报价精度*10000
        step5	聚合度为报价精度*100000
        """
        params = {"symbol": symbol, "depth": depth, "type": depth_type}
        return await self._request_spot_market_api(path="depth", params=params)

    async def spot_trade(self, symbol: str):
        """
        返回指定交易对最新的一个交易记录
        """
        return await self._request_spot_market_api(path="trade", params={'symbol': symbol})

    async def spot_trade_history(self, symbol: str, size: Optional[int] = 1):
        """
        返回指定交易对近期的所有交易记录
        size 最大值 2000
        """
        assert size <= 2000
        return await self._request_spot_market_api(path="history/trade", params={"symbol": symbol, "size": size})

    async def spot_market_detail(self, symbol: str):
        """
        最近24小时的行情数据汇总
        此接口返回的成交量、成交金额为24小时滚动数据（平移窗口大小24小时），有可能会出现后一个窗口内的累计成交量、累计成交额小于前一窗口的情况。
        """
        return await self._request_spot_market_api(path="detail", params={"symbol": symbol})

    async def spot_etf(self, symbol: str):
        """
        杠杆ETP的最新净值
        """
        return await self._request_spot_market_api(path="etf", params={'symbol': symbol})

    async def spot_account_info(self):
        """
        查询当前用户的所有账户 ID account-id 及其相关信息
        """
        return await self._request_spot_account_api(path="accounts")

    async def spot_account_balance(self, account_id: str):
        """
        查询指定账户的余额，支持以下账户：

        spot：现货账户， margin：逐仓杠杆账户，otc：OTC 账户，point：点卡账户，super-margin：全仓杠杆账户,
        investment: C2C杠杆借出账户, borrow: C2C杠杆借入账户
        """
        return await self._request_spot_account_api(path=f"accounts/{account_id}/balance")

    async def spot_asset_valuation(self, account_type: str, currency: Optional[str] = "BTC"):
        """
        按照BTC或法币计价单位，获取指定账户的总资产估值
        """
        return await self._request_spot_account_api(
            path="asset-valuation", version=BaseClient.SPOT_API_VERSION2,
            params={'accountType': account_type, "valuationCurrency": currency}
        )

    async def spot_cancel_order(self, order_id):
        uri = self._create_spot_order_api_uri(f"orders/{order_id}/submitcancel")
        return await self._request_spot_order_api("post", uri)

    async def future_transfer(self, currency: str, amount, transfer_type: str):
        """
        币币现货账户与交割合约账户划转
        从现货现货账户转至交割合约账户，类型为pro-to-futures
        从交割合约账户转至现货账户，类型为futures-to-pro
        """
        uri = self._create_spot_api_uri("futures/transfer")
        data = {
            "currency": currency,
            "amount": amount,
            "type": transfer_type
        }
        return await self._request("post", uri, data=data, signed=True)

    async def coin_margined_transfer(self, _from, _to, currency, amount):
        """
        现货-币本位永续合约账户之间进行资金的划转

        此接口用户币币现货账户与币本位永续合约账户之间的资金划转。
        该接口的访问频次的限制为1秒/1次。
        现货与币本位永续合约划转接口，所有划转的币的精度是8位小数

        from	true	string	来源业务线账户，取值：spot(币币)、swap(币本位永续)	e.g. spot
        to	true	string	目标业务线账户，取值：spot(币币)、swap(币本位永续)	e.g. swap
        currency	true	string	币种,支持大小写	e.g. btc
        amount	true	Decimal	划转金额
        """
        uri = self._create_spot_api_uri("account/transfer", version=BaseClient.SPOT_API_VERSION2)
        data = {
            "from": _from,
            "to": _to,
            "currency": currency,
            "amount": amount
        }
        return await self._request("post", uri, data=data, signed=True)


    ##############################
    # 交割合约
    ##############################

    #### 市场行情 ####

    async def future_contract_info(self, symbol=None, contract_type=None, contract_code=None):
        """
        symbol	string	false	支持大小写，"BTC","ETH"...
        contract_type	string	false	合约类型: （this_week:当周 next_week:下周 quarter:当季 next_quarter:次季）
        contract_code	string	false	BTC180914
        """
        uri = self._create_future_api_uri("contract_contract_info")
        params = {}
        if symbol:
            params['symbol'] = symbol
        if contract_type:
            params['contract_type'] = contract_type
        if contract_code:
            params['contract_code'] = contract_code
        return await self._request("get", uri, params=params)

    async def future_contract_index(self, symbol=None):
        """
        合约指数
        :param symbol:
        :return:
        """
        uri = self._create_future_api_uri("contract_index")
        params = {}
        if symbol:
            params['symbol'] = symbol
        return await self._request("get", uri, params=params)

    async def future_contract_price_limit(self, symbol=None, contract_type=None, contract_code=None):
        """
        获取合约最高/低限价
        symbol	string	false	支持大小写，"BTC","ETH"...
        contract_type	string	false	合约类型: （this_week:当周 next_week:下周 quarter:当季 next_quarter:次季）
        contract_code	string	false	BTC180914
        """
        uri = self._create_future_api_uri("contract_price_limit")
        params = {}
        if symbol:
            params['symbol'] = symbol
        if contract_type:
            params['contract_type'] = contract_type
        if contract_code:
            params['contract_code'] = contract_code
        return await self._request("get", uri, params=params)

    async def future_contract_open_interest(self, symbol=None, contract_type=None, contract_code=None):
        """
        当前合约的总持仓量
        symbol	string	false	支持大小写，"BTC","ETH"...
        contract_type	string	false	合约类型: （this_week:当周 next_week:下周 quarter:当季 next_quarter:次季）
        contract_code	string	false	BTC180914
        """
        uri = self._create_future_api_uri("contract_open_interest")
        params = {}
        if symbol:
            params['symbol'] = symbol
        if contract_type:
            params['contract_type'] = contract_type
        if contract_code:
            params['contract_code'] = contract_code
        return await self._request("get", uri, params=params)

    async def future_contract_delivery_price(self, symbol=None):
        """
        预估交割价
        :param symbol:
        :return:
        """
        uri = self._create_future_api_uri("contract_delivery_price")
        params = {}
        if symbol:
            params['symbol'] = symbol
        return await self._request("get", uri, params=params)

    async def future_contract_estimated_settlement_price(self, symbol=None):
        """
        预估结算价
        :param symbol:
        :return:
        """
        params = package_data(remove_key(locals()))
        uri = self._create_future_api_uri("contract_estimated_settlement_price")
        return await self._request("get", uri, params=params)

    async def future_api_state(self, symbol=None):
        """
        查询系统状态
        :param symbol:
        :return:
        """
        params = package_data(remove_key(locals()))
        uri = self._create_future_api_uri("contract_api_state")
        return await self._request("get", uri, params=params)

    async def future_market_depth(self, symbol, depth_type = constants.WS_DEPTH_5):
        """
        获取行情深度
        :param symbol:
        :param depth_type:
        :return:
        """
        params = package_data(remove_key(locals()), replace_keys={"depth_type": "type"})
        uri = f"{self.API_FUTURE_URL}/market/depth"
        return await self._request("get", uri, params=params)

    async def future_market_bbo(self, symbol=None):
        """
        获取最优挂单
        symbol	false	string	合约标识，不填返回全部合约的最优挂单信息
        如"BTC_CW"表示BTC当周合约，"BTC_NW"表示BTC次周合约，"BTC_CQ"表示BTC当季合约 ，"BTC_NQ"表示BTC次季度合约。
        支持使用合约code来查询数据， 例如："BTC200918"(当周)，"BTC200925"(次周)，"BTC201225"(季度)，"BTC210326"(次季度)。
        """
        params = package_data(remove_key(locals()))
        uri = f"{self.API_FUTURE_URL}/market/bbo"
        return await self._request("get", uri, params=params)

    async def future_kline(self, symbol, period, size=None, start=None, end=None):
        """
        获取K线数据
        symbol	false	string	合约标识，不填返回全部合约的最优挂单信息
        如"BTC_CW"表示BTC当周合约，"BTC_NW"表示BTC次周合约，"BTC_CQ"表示BTC当季合约 ，"BTC_NQ"表示BTC次季度合约。
        支持使用合约code来查询数据， 例如："BTC200918"(当周)，"BTC200925"(次周)，"BTC201225"(季度)，"BTC210326"(次季度)。
        period	true	string	K线类型		1min, 5min, 15min, 30min, 60min,4hour,1day, 1mon
        size	false	int	获取数量	150	[1,2000]
        from	false	long	开始时间戳 10位 单位S
        to	false	long	结束时间戳 10位 单位S

        Note
        1、size字段或者from、to字段至少要填写一个。
        2、如果size、from、to 均不填写，则返回错误。
        3、如果填写from，也要填写to。最多可获取连续两年的数据。
        4、如果size、from、to 均填写，会忽略from、to参数。
        支持查询已下市四周内的合约的K线数据（即到期日在过去最近四周的合约），可输入已下市四周内的合约的合约代码进行查询K线数据。
        """
        params = package_data(remove_key(locals()), {"start": "from", "end": "to"})
        uri = f"{self.API_FUTURE_URL}/market/history/kline"
        return await self._request("get", uri, params=params)

    async def future_mark_price_kline(self, symbol, period, size):
        """
        获取标记价格的K线数据
        symbol	false	string	合约标识，不填返回全部合约的最优挂单信息
        如"BTC_CW"表示BTC当周合约，"BTC_NW"表示BTC次周合约，"BTC_CQ"表示BTC当季合约 ，"BTC_NQ"表示BTC次季度合约。
        支持使用合约code来查询数据， 例如："BTC200918"(当周)，"BTC200925"(次周)，"BTC201225"(季度)，"BTC210326"(次季度)。
        period	true	string	K线类型		1min, 5min, 15min, 30min, 60min,4hour,1day, 1mon
        size	false	int	获取数量	150	[1,2000]

        Note
        1、最多一次2000条数据
        """
        params = package_data(remove_key(locals()))
        uri = f"{self.API_FUTURE_URL}/index/market/history/mark_price_kline"
        return await self._request("get", uri, params=params)

    async def future_merged(self, symbol):
        """
        获取聚合行情
        symbol	false	string	合约标识，不填返回全部合约的最优挂单信息
        如"BTC_CW"表示BTC当周合约，"BTC_NW"表示BTC次周合约，"BTC_CQ"表示BTC当季合约 ，"BTC_NQ"表示BTC次季度合约。
        支持使用合约code来查询数据， 例如："BTC200918"(当周)，"BTC200925"(次周)，"BTC201225"(季度)，"BTC210326"(次季度)。
        """
        params = package_data(remove_key(locals()))
        uri = f"{self.API_FUTURE_URL}/market/detail/merged"
        return await self._request("get", uri, params=params)

    async def future_batch_merged(self, symbol=None):
        """
        批量获取聚合行情
        symbol	false	string	合约标识，不填返回全部合约的最优挂单信息
        如"BTC_CW"表示BTC当周合约，"BTC_NW"表示BTC次周合约，"BTC_CQ"表示BTC当季合约 ，"BTC_NQ"表示BTC次季度合约。
        支持使用合约code来查询数据， 例如："BTC200918"(当周)，"BTC200925"(次周)，"BTC201225"(季度)，"BTC210326"(次季度)。

        该接口更新频率为50ms
        """
        params = package_data(remove_key(locals()))
        uri = f"{self.API_FUTURE_URL}/market/detail/batch_merged"
        return await self._request("get", uri, params=params)

    async def future_trade_history(self, symbol=None):
        """
        获取市场最近成交记录
        symbol	false	string	合约标识，不填返回全部合约的最优挂单信息
        如"BTC_CW"表示BTC当周合约，"BTC_NW"表示BTC次周合约，"BTC_CQ"表示BTC当季合约 ，"BTC_NQ"表示BTC次季度合约。
        支持使用合约code来查询数据， 例如："BTC200918"(当周)，"BTC200925"(次周)，"BTC201225"(季度)，"BTC210326"(次季度)。
        """
        params = package_data(remove_key(locals()))
        uri = f"{self.API_FUTURE_URL}/market/trade"
        return await self._request("get", uri, params=params)

    async def future_batch_trade_history(self, symbol, size):
        """
        批量获取市场最近成交记录
        symbol	true	string	合约标识，不填返回全部合约的最优挂单信息
        如"BTC_CW"表示BTC当周合约，"BTC_NW"表示BTC次周合约，"BTC_CQ"表示BTC当季合约 ，"BTC_NQ"表示BTC次季度合约。
        支持使用合约code来查询数据， 例如："BTC200918"(当周)，"BTC200925"(次周)，"BTC201225"(季度)，"BTC210326"(次季度)。
        size	true	int	获取数量	150	[1,2000]
        """
        params = package_data(remove_key(locals()))
        uri = f"{self.API_FUTURE_URL}/market/history/trade"
        return await self._request("get", uri, params=params)

    async def future_liquidation_orders(self, symbol, trade_type, create_date, page_index=1, page_size=20):
        """
        获取强平订单
        symbol	true	string	品种代码		支持大小写，"BTC","ETH"...
        trade_type	true	int	交易类型		0:全部,5: 卖出强平,6: 买入强平
        create_date	true	int	日期		7，90（7天或者90天）
        page_index	false	int	页码,不填默认第1页	1
        page_size	false	int	不填默认20，不得多于50	20	[1-50]
        """
        params = package_data(remove_key(locals()))
        uri = self._create_future_api_uri("contract_liquidation_orders")
        return await self._request("get", uri, params=params)

    async def future_basis_data(self, symbol, period, basis_price_type=constants.BasisPriceType.OPEN, size=100):
        """
        获取基差数据
        symbol	true	string	合约名称		支持大小写，如"BTC_CW"表示BTC当周合约，"BTC_NW"表示BTC次周合约，"BTC_CQ"表示BTC当季合约, "BTC_NQ"表示次季度合约"
        period	true	string	周期		仅支持小写，1min,5min, 15min, 30min, 60min,4hour,1day,1mon
        basis_price_type	false	string	基差价格类型，表示在周期内计算基差使用的价格类型	不填，默认使用开盘价	仅支持小写，开盘价：open，收盘价：close，最高价：high，最低价：low，平均价=（最高价+最低价）/2：average
        size	true	int	基差获取数量		[1,2000]
        """
        params = package_data(remove_key(locals()))
        uri = f"{self.API_FUTURE_URL}/index/market/history/basis"
        return await self._request("get", uri, params=params)

    #### 合约资产 #####

    async def future_balance_valuation(self, valuation_asset="BTC"):
        """
        获取账户总资产估值
        valuation_asset	false	string	资产估值币种，即按该币种为单位进行估值，不填默认"BTC"	"BTC","USD","CNY","EUR","GBP","VND","HKD","TWD","MYR","SGD","KRW","RUB","TRY"
        """
        data = {"valuation_asset": valuation_asset}
        return await self._request_future_private_api("post", "contract_balance_valuation", data=data)

    async def future_account_info(self, symbol):
        """
        获取账户信息
        symbol	false	string	品种代码		支持大小写,"BTC","ETH"...如果缺省，默认返回所有品种
        """
        data = package_data(remove_key(locals()))
        rst = await self._request_future_private_api("post", "contract_account_info", data=data)
        if rst.status == 'ok' and rst.data and symbol:
            new_data = None
            for item in rst.data:
                if item['symbol'].upper() == symbol.upper():
                    new_data = item
                    break
            return Result(rst.code, rst.status, rst.msg, new_data)
        return rst

    async def future_position_info(self, symbol):
        """
        获取持仓信息
        symbol	false	string	品种代码		支持大小写,"BTC","ETH"...如果缺省，默认返回所有品种
        """
        data = package_data(remove_key(locals()))
        return await self._request_future_private_api("post", "contract_position_info", data=data)

    async def future_fee(self, symbol=None):
        """
        查询用户当前的手续费费率
        symbol	false	string	品种代码		支持大小写,"BTC","ETH"...如果缺省，默认返回所有品种
        """
        data = package_data(remove_key(locals()))
        return await self._request_future_private_api("post", "contract_fee", data=data)

    async def future_position_limit(self, symbol=None):
        """
        用户持仓量限制的查询
        symbol	false	string	品种代码		支持大小写,"BTC","ETH"...如果缺省，默认返回所有品种
        """
        data = package_data(remove_key(locals()))
        return await self._request_future_private_api("post", "contract_position_limit", data=data)

    async def future_account_position_info(self, symbol):
        """
        查询用户账户和持仓信息
        symbol	true	string	品种代码		支持大小写,"BTC","ETH"...如果缺省，默认返回所有品种
        """
        params = {"symbol": symbol}
        return await self._request_future_private_api("post", "contract_account_position_info", params=params)

    #### 合约交易接口 ####
    async def future_create_order(
            self, direction, volume: int, offset, order_price_type, lever_rate=None, symbol=None, contract_type=None,
            contract_code=None, client_order_id=None, price=None, tp_trigger_price=None, tp_order_price=None,
            tp_order_price_type=None, sl_trigger_price=None, sl_order_price=None, sl_order_price_type=None):
        """
        开单
        symbol	string	false	支持大小写,"BTC","ETH"...
        contract_type	string	false	合约类型 ("this_week":当周 "next_week":下周 "quarter":当季 "next_quarter":次季)
        contract_code	string	false	BTC180914
        client_order_id	long	false	客户自己填写和维护，必须为数字,请注意必须小于等于9223372036854775807
        price	decimal	false	价格
        volume	long	true	委托数量(张)
        direction	string	true	"buy":买 "sell":卖
        offset	string	true	"open":开 "close":平
        lever_rate	int	true	杠杆倍数[“开仓”若有10倍多单，就不能再下20倍多单, "平仓"可以不填杠杆倍数;首次使用高倍杠杆(>20倍)，请使用主账号登录web端同意高倍杠杆协议后，才能使用接口下高倍杠杆(>20倍)]
        order_price_type	string	true	订单报价类型 "limit":限价，"opponent":对手价 ，"post_only":只做maker单,post only下单只受用户持仓数量限制,"optimal_5"：最优5档，"optimal_10"：最优10档，"optimal_20"：最优20档，"ioc":IOC订单，"fok"：FOK订单, "opponent_ioc"： 对手价-IOC下单，"optimal_5_ioc"：最优5档-IOC下单，"optimal_10_ioc"：最优10档-IOC下单，"optimal_20_ioc"：最优20档-IOC下单,"opponent_fok"： 对手价-FOK下单，"optimal_5_fok"：最优5档-FOK下单，"optimal_10_fok"：最优10档-FOK下单，"optimal_20_fok"：最优20档-FOK下单
        tp_trigger_price	decimal	false	止盈触发价格
        tp_order_price	decimal	false	止盈委托价格（最优N档委托类型时无需填写价格）
        tp_order_price_type	string	false	止盈委托类型 不填默认为limit; 限价：limit ，最优5档：optimal_5，最优10档：optimal_10，最优20档：optimal_20
        sl_trigger_price	decimal	false	止损触发价格
        sl_order_price	decimal	false	止损委托价格（最优N档委托类型时无需填写价格）
        sl_order_price_type	string	false	止损委托类型 不填默认为limit; 限价：limit ，最优5档：optimal_5，最优10档：optimal_10，最优20档：optimal_20

        备注
        如果contract_code填了值，那就按照contract_code去下单，如果contract_code没有填值，则按照symbol+contract_type去下单。

        对手价下单price价格参数不用传，对手价下单价格是买一和卖一价,optimal_5：最优5档、optimal_10：最优10档、optimal_20：最优20档下单price价格参数不用传，"limit":限价，"post_only":只做maker单 需要传价格，"fok"：全部成交或立即取消，"ioc":立即成交并取消剩余。

        Post only(也叫maker only订单，只下maker单)每个周期合约的开仓/平仓的下单数量限制为500000，同时也会受到用户持仓数量限制。

        若存在持仓，那么下单时杠杆倍数必须与持仓杠杆相同，否则下单失败。若需使用新杠杆下单，则必须先使用切换杠杆接口将持仓杠杆切换成功后再下单。

        只有开仓订单才支持设置止盈止损。

        止盈触发价格为设置止盈单必填字段，止损触发价格为设置止损单必填字段；若缺省触发价格字段则不会设置对应的止盈单或止损单。

        开平方向
        开多：买入开多(direction用buy、offset用open)

        平多：卖出平多(direction用sell、offset用close)

        开空：卖出开空(direction用sell、offset用open)

        平空：买入平空(direction用buy、offset用close)
        """
        data = package_data(remove_key(locals()))
        return await self._request_future_private_api("post", "contract_order", data=data)

    async def future_batch_create_order(self, orders_data: list):
        """
        批量开单
        :param orders_data: 参数同开单接口
        :return:
        """
        return await self._request_future_private_api("post", "contract_batchorder", data={"orders_data": orders_data})

    async def future_cancel_order(self, symbol, order_id=None, client_order_id=None):
        """
        撤销订单
        order_id	false (请看备注)	string	订单ID(多个订单ID中间以","分隔,一次最多允许撤消10个订单)
        client_order_id	false (请看备注)	string	客户订单ID(多个订单ID中间以","分隔,一次最多允许撤消10个订单)
        symbol	true	string	支持大小写,"BTC","ETH"...

        备注：
        order_id和client_order_id都可以用来撤单，至少要填写一个,同时只可以设置其中一种，如果设置了两种，默认以order_id来撤单。

        撤单接口返回结果只代表撤单命令发送成功，建议根据订单查询接口查询订单的状态来确定订单是否已真正撤销。

        client_order_id，24小时有效，超过24小时的订单根据client_order_id将查询不到
        """
        assert symbol is not None
        data = package_data(remove_key(locals()))
        return await self._request_future_private_api("post", "contract_cancel", data=data)

    async def future_cancel_all(self, symbol, contract_code=None, contract_type=None, direction=None, offset=None):
        """
        全部撤单
        symbol	true	string	品种代码，支持大小写，如"BTC","ETH"...
        contract_code	false	string	合约code
        contract_type	false	string	合约类型
        direction	false	string	买卖方向（不填默认全部） "buy":买 "sell":卖
        offset	false	string	开平方向（不填默认全部）"open":开 "close":平

        备注
        只传symbol，撤销该品种下所有周期的合约
        只要有contract_code，则撤销该code的合约
        只传symbol+contract_type， 则撤销二者拼接所成的合约订单
        direction与offset可只填其一，只填其一则按对应的条件去撤单。（如用户只传了direction=buy，则撤销所有买单，包括开仓和平仓）
        """
        data = package_data(remove_key(locals()))
        return await self._request_future_private_api("post", "contract_cancelall", data=data)

    async def future_switch_lever_rate(self, symbol, lever_rate: int):
        """
        切换杠杆
        备注
        只有在单个品种下只有持仓，且没有挂单的场景下，才可以切换该品种当前的倍数。
        接口限制请求次数为每3秒一次。
        """
        data = package_data(remove_key(locals()))
        return await self._request_future_private_api("post", "contract_switch_lever_rate", data=data)

    async def future_order_info(self, symbol, order_id=None, client_order_id=None):
        """
        订单信息
        参数名称	是否必须	类型	描述
        order_id	false（请看备注）	string	订单ID(多个订单ID中间以","分隔,一次最多允许查询50个订单)
        client_order_id	false（请看备注）	string	客户订单ID(多个订单ID中间以","分隔,一次最多允许查询50个订单)
        symbol	true	string	支持大小写，"BTC","ETH"...

        最多只能查询 4 小时内的撤单信息。
        order_id和client_order_id至少要填写一个。
        order_id和client_order_id都可以用来查询，同时只可以设置其中一种，如果设置了两种，默认以order_id来查询。每天结算或周五交割后，会把结束状态的订单（5部分成交已撤单 6全部成交 7已撤单）删除掉。
        client_order_id，24小时有效，超过24小时的订单根据client_order_id将查询不到。
        """
        data = package_data(remove_key(locals()))
        return await self._request_future_private_api("post", "contract_order_info", data=data)

    async def future_order_detail(self, symbol, order_id, create_at: int = None, order_type=None, page_index=None,
                                  page_size=None):
        """
        订单明细信息
        参数名称	是否必须	类型	描述
        symbol	true	string	支持大小写,"BTC","ETH"...
        order_id	true	long	订单id
        created_at	false	long	下单时间戳
        order_type	false	int	订单类型，1:报单 、 2:撤单 、 3:强平、4:交割
        page_index	false	int	第几页,不填第一页
        page_size	false	int	不填默认20,不得多于50

        获取订单明细接口查询撤单数据时，如果传“created_at”和“order_type”参数则能查询最近6小时数据，如果不传“created_at”和“order_type”参数只能查询到最近2小时数据。
        order_id返回是18位，nodejs和javascript默认解析18有问题，nodejs和javascript里面JSON.parse默认是int，超过18位的数字用json-bigint的包解析。
        created_at使用13位long类型时间戳（包含毫秒时间），如果输入准确的时间戳，查询性能将会提升。例如:"2019/10/18 10:26:22"转换为时间戳为：1571365582123。也可以直接从contract_order下单接口返回的ts中获取时间戳查询对应的订单。
        created_at禁止传0。
        """
        data = package_data(remove_key(locals()))
        return await self._request_future_private_api("post", "contract_order_detail", data=data)

    async def future_open_orders(self, symbol, page_index=1, page_size=20, sort_by="created_at", trade_type=0):
        """
        获取合约当前未成交委托

        参数名称	是否必须	类型	描述	默认值	取值范围
        symbol	true	string	品种代码		支持大小写, "BTC","ETH"...
        page_index	false	int	页码，不填默认第1页	1
        page_size	false	int	不填默认20，不得多于50	20	[1-50]
        sort_by	false	string	排序字段，不填默认按创建时间倒序	created_at	“created_at”(按照创建时间倒序)，“update_time”(按照更新时间倒序)
        trade_type	false	int	交易类型，不填默认查询全部	0	0:全部,1:买入 开多,2: 卖出开空,3: 买入平空,4: 卖出平多。
        """
        data = package_data(remove_key(locals()))
        return await self._request_future_private_api("post", "contract_openorders", data=data)

    async def future_contract_hisorders(self, symbol, trade_type, type, status, create_date, page_index=1, page_size=20,
                                        contract_code=None, order_type=None, sort_by="create_date"):
        """
        获取合约历史委托
        symbol	true	string	品种代码		支持大小写,"BTC","ETH"...
        trade_type	true	int	交易类型		0:全部,1:买入开多,2: 卖出开空,3: 买入平空,4: 卖出平多,5: 卖出强平,6: 买入强平,7:交割平多,8: 交割平空, 11:减仓平多，12:减仓平空
        type	true	int	类型		1:所有订单,2:结束状态的订单
        status	true	string	订单状态		可查询多个状态，"3,4,5" , 0:全部,3:未成交, 4: 部分成交,5: 部分成交已撤单,6: 全部成交,7:已撤单
        create_date	true	int	日期		可随意输入正整数, ，如果参数超过90则默认查询90天的数据
        page_index	false	int	页码，不填默认第1页	1
        page_size	false	int	每页条数，不填默认20,不得多于50	20	[1-50]
        contract_code	false	string	合约代码
        order_type	false	string	订单类型		1：限价单、3：对手价、4：闪电平仓、5：计划委托、6：post_only、7：最优5档、8：最优10档、9：最优20档、10：fok、11：ioc
        sort_by	false	string	排序字段（降序），不填默认按照create_date降序	create_date	"create_date"：按订单创建时间进行降序，"update_time"：按订单更新时间进行降序
        """
        data = package_data(remove_key(locals()))
        return await self._request_future_private_api("post", "contract_hisorders", data=data)

    async def future_contract_hisorders_exact(self, symbol, trade_type, type, status, contract_code=None,
                                              order_price_type=None, start_time=None, end_time=None, from_id=None,
                                              size=20, direct="prev"):
        """
        组合查询合约历史委托
        symbol 	true 	string	品种代码 	"BTC","ETH"...
        trade_type	true	int	交易类型	0:全部,1:买入开多,2: 卖出开空,3: 买入平空,4: 卖出平多,5: 卖出强平,6: 买入强平,7:交割平多,8: 交割平空, 11:减仓平多，12:减仓平空
        type	true	int	类型	1:所有订单,2:结束状态的订单
        status	true	string	订单状态	可查询多个状态，"3,4,5" , 0:全部,3:未成交, 4: 部分成交,5: 部分成交已撤单,6: 全部成交,7:已撤单
        contract_code	false	string	合约代码
        order_price_type	false	string	订单报价类型	订单报价类型 "limit":限价，"opponent":对手价 ，"post_only":只做maker单,post only下单只受用户持仓数量限制,"optimal_5"：最优5档，"optimal_10"：最优10档，"optimal_20"：最优20档，"ioc":IOC订单，"fok"：FOK订单, "opponent_ioc"： 对手价-IOC下单，"optimal_5_ioc"：最优5档-IOC下单，"optimal_10_ioc"：最优10档-IOC下单，"optimal_20_ioc"：最优20档-IOC下单,"opponent_fok"： 对手价-FOK下单，"optimal_5_fok"：最优5档-FOK下单，"optimal_10_fok"：最优10档-FOK下单，"optimal_20_fok"：最优20档-FOK下单
        start_time	false	long	起始时间（时间戳，单位毫秒）	详见备注
        end_time	false	long	结束时间（时间戳，单位毫秒）	详见备注
        from_id	false	long	查询起始id（取返回数据的query_id字段）
        size	false	int	数据条数，默认取20，最大50	[1-50]
        direct	false	string	查询方向	prev 向前；next 向后；默认值取prev
        """
        data = package_data(remove_key(locals()))
        return await self._request_future_private_api("post", "contract_hisorders_exact", data=data)

    async def future_match_result(self, symbol, trade_type, create_date, contract_code=None, page_index=1, page_size=20):
        """
        获取历史成交记录

        参数名称	是否必须	类型	描述	默认值	取值范围
        symbol	true	string	品种代码		支持大小写,"BTC","ETH"...
        trade_type	true	int	交易类型		0:全部,1:买入开多,2: 卖出开空,3: 买入平空,4: 卖出平多,5: 卖出强平,6: 买入强平
        create_date	true	int	日期		可随意输入正整数，如果参数超过90则默认查询90天的数据
        contract_code	false	string	合约code
        page_index	false	int	页码，不填默认第1页	1
        page_size	false	int	不填默认20，不得多于50	20	[1-50]
        """
        data = package_data(remove_key(locals()))
        return await self._request_future_private_api("post", "contract_matchresults", data=data)

    async def future_match_result_exact(self, symbol, trade_type, contract_code=None, start_time=None, end_time=None,
                                        from_id=None, size=20, direct="prev"):
        """
        组合查询历史成交记录接口
        symbol	true	string	品种代码	"BTC","ETH"...
        trade_type	true	int	交易类型	0:全部,1:买入开多,2: 卖出开空,3: 买入平空,4: 卖出平多,5: 卖出强平,6: 买入强平
        contract_code	false	string	合约code
        start_time	false	long	起始时间（时间戳，单位毫秒）	详见备注
        end_time	false	long	结束时间（时间戳，单位毫秒）	详见备注
        from_id	false	long	查询起始id（取返回数据的query_id字段）
        size	false	int	数据条数,默认取20，最大50	[1-50]
        direct	false	string	查询方向	prev 向前；next 向后；默认值取prev
        """
        data = package_data(remove_key(locals()))
        return await self._request_future_private_api("post", "contract_matchresults_exact", data=data)

    async def future_lightning_close_position(self, volume, direction, symbol=None, contract_type=None,
                                              contract_code=None, client_order_id=None,
                                              order_price_type=constants.OrderPriceType.LIGHTNING):
        """
        闪电平仓
        """
        data = package_data(remove_key(locals()))
        return await self._request_future_private_api("post", "lightning_close_position", data=data)

    #### 币本位永续合约行情接口 #####
    async def coin_margined_contract_info(self, contract_code=None):
        """
        合约信息
        contract_code	string	false	合约代码, 大小写均支持，"BTC-USD",不填查询所有合约
        """
        params = package_data(remove_key(locals()))
        uri = self._create_coin_margined_api_uri("swap_contract_info")
        return await self._request("get", uri, params=params)

    async def coin_margined_contract_index(self, contract_code=None):
        """
        合约指数信息
        contract_code	string	false	合约代码, 大小写均支持，"BTC-USD",不填查询所有合约
        """
        params = package_data(remove_key(locals()))
        uri = self._create_coin_margined_api_uri("swap_index")
        return await self._request("get", uri, params=params)

    async def coin_margined_open_interest(self, contract_code=None):
        """
        合约总持仓量
        contract_code	string	false	合约代码, 大小写均支持，"BTC-USD",不填查询所有合约
        """
        params = package_data(remove_key(locals()))
        uri = self._create_coin_margined_api_uri("swap_open_interest")
        return await self._request("get", uri, params=params)

    async def coin_margined_market_depth(self, contract_code, depth_type = constants.WS_DEPTH_5):
        """
        获取行情深度
        contract_code	string	true	合约代码，支持大小写, "BTC-USD" ...
        type	string	true	(150档数据) step0, step1, step2, step3, step4, step5, step14, step15, step16, step17（合并深度1-5,14-17）；step0时，不合并深度, (20档数据) step6, step7, step8, step9, step10, step11, step12, step13, step18, step19（合并深度7-13,18-19）；step6时，不合并深度
        """
        params = package_data(remove_key(locals()), replace_keys={"depth_type": "type"})
        uri = f"{self.API_FUTURE_URL}/swap-ex/market/depth"
        return await self._request("get", uri, params=params)

    async def coin_margined_market_bbo(self, contract_code=None):
        """
        获取最优挂单
        contract_code	false	string	合约代码，不填返回全部合约的市场最优挂单信息	"BTC-USD" ...
        """
        params = package_data(remove_key(locals()))
        uri = f"{self.API_FUTURE_URL}/swap-ex/market/bbo"
        return await self._request("get", uri, params=params)

    async def coin_margined_merged(self, contract_code):
        """
        获取聚合行情
        contract_code	true	string	合约代码	仅支持大写， "BTC-USD" ...
        """
        params = package_data(remove_key(locals()))
        uri = f"{self.API_FUTURE_URL}/swap-ex/market/detail/merged"
        return await self._request("get", uri, params=params)

    async def coin_margined_api_state(self, contract_code=None):
        """
        查询系统状态
        :param contract_code:
        :return:
        """
        params = package_data(remove_key(locals()))
        uri = self._create_coin_margined_api_uri("swap_api_state")
        return await self._request("get", uri, params=params)

    async def coin_margined_funding_rate(self, contract_code):
        """
        查询合约资金费率
        :param contract_code:
        :return:
        """
        params = package_data(remove_key(locals()))
        uri = self._create_coin_margined_api_uri("swap_funding_rate")
        return await self._request("get", uri, params=params)

    async def coin_margined_batch_funding_rate(self, contract_code=None):
        """
        批量查询合约资金费率
        :param contract_code:
        :return:
        """
        params = package_data(remove_key(locals()))
        uri = self._create_coin_margined_api_uri("swap_batch_funding_rate")
        return await self._request("get", uri, params=params)

    async def coin_margined_liquidation_orders(self, contract_code, trade_type, create_date, page_index=1, page_size=20):
        """
        获取强平订单
        contract_code	true	string	品种代码		支持大小写，"BTC-USD"
        trade_type	true	int	交易类型		0:全部,5: 卖出强平,6: 买入强平
        create_date	true	int	日期		7，90（7天或者90天）
        page_index	false	int	页码,不填默认第1页	1
        page_size	false	int	不填默认20，不得多于50	20	[1-50]
        """
        params = package_data(remove_key(locals()))
        uri = self._create_coin_margined_api_uri("swap_liquidation_orders")
        return await self._request("get", uri, params=params)

    async def coin_margined_premium_index_kline(self, contract_code, period, size):
        """
        合约的溢价指数K线
        参数名称	是否必须	类型	描述	取值范围
        contract_code	true	string	合约代码	支持大小写，"BTC-USD" ...
        period	true	string	K线类型	1min, 5min, 15min, 30min, 60min,4hour,1day, 1week,1mon
        size	true	int	K线获取数量	[1,2000] （最多2000）
        """
        params = package_data(remove_key(locals()))
        uri = f"{self.API_FUTURE_URL}/index/market/history/swap_premium_index_kline"
        return await self._request("get", uri, params=params)

    async def coin_margined_estimated_rate_kline(self, contract_code, period, size):
        """
        实时预测资金费率的K线数据
        参数名称	是否必须	类型	描述	取值范围
        contract_code	true	string	合约代码	支持大小写，"BTC-USD" ...
        period	true	string	K线类型	1min, 5min, 15min, 30min, 60min,4hour,1day, 1week,1mon
        size	true	int	K线获取数量	[1,2000] （最多2000）
        """
        params = package_data(remove_key(locals()))
        uri = f"{self.API_FUTURE_URL}/index/market/history/swap_estimated_rate_kline"
        return await self._request("get", uri, params=params)

    async def coin_margined_basis_data(self, contract_code, period, basis_price_type=constants.BasisPriceType.OPEN, size=100):
        """
        获取基差数据
        contract_code	true	string	合约代码		如"BTC-USD"
        period	true	string	周期		仅支持小写，1min,5min, 15min, 30min, 60min,4hour,1day,1mon
        basis_price_type	false	string	基差价格类型，表示在周期内计算基差使用的价格类型	不填，默认使用开盘价	仅支持小写，开盘价：open，收盘价：close，最高价：high，最低价：low，平均价=（最高价+最低价）/2：average
        size	true	int	基差获取数量		[1,2000]
        """
        params = package_data(remove_key(locals()))
        uri = f"{self.API_FUTURE_URL}/index/market/history/swap_basis"
        return await self._request("get", uri, params=params)

    #### 币本位永续合约资产接口 #####
    async def coin_margined_balance_valuation(self, valuation_asset="BTC"):
        """
        获取账户总资产估值
        valuation_asset	false	string	资产估值币种，即按该币种为单位进行估值，不填默认"BTC"	"BTC","USD","CNY","EUR","GBP","VND","HKD","TWD","MYR","SGD","KRW","RUB","TRY"
        """
        data = {"valuation_asset": valuation_asset}
        return await self._request_coin_margined_private_api("post", "swap_balance_valuation", data=data)

    async def coin_margined_account_info(self, contract_code):
        """
        获取账户信息
        contract_code	false	string	支持大小写, "BTC-USD"... ,如果缺省，默认返回所有合约
        """
        data = package_data(remove_key(locals()))
        rst = await self._request_coin_margined_private_api('post', "swap_account_info", data=data)
        if rst.status == 'ok' and rst.data and contract_code:
            new_data = None
            for item in rst.data:
                if item['contract_code'].upper() == contract_code.upper():
                    new_data = item
                    break
            return Result(rst.code, rst.status, rst.msg, new_data)
        return rst

    async def coin_margined_position_info(self, contract_code=None):
        """
        获取用户持仓信息
        contract_code	false	string	支持大小写, "BTC-USD"... ,如果缺省，默认返回所有合约
        """
        data = package_data(remove_key(locals()))
        return await self._request_coin_margined_private_api("post", "swap_position_info", data=data)

    async def coin_margined_account_position_info(self, contract_code):
        """
        获取用户账户和持仓信息
        contract_code	false	string	支持大小写, "BTC-USD"...
        """
        data = package_data(remove_key(locals()))
        return await self._request_coin_margined_private_api("post", "swap_account_position_info", data=data)

    async def coin_margined_fee(self, contract_code=None):
        """
        查询用户当前的手续费费率
        contract_code	false	string	支持大小写, "BTC-USD"... ,如果缺省，默认返回所有合约
        """
        data = package_data(remove_key(locals()))
        return await self._request_coin_margined_private_api("post", "swap_fee", data=data)

    async def coin_margined_api_trading_status(self):
        """
        获取用户的API指标禁用信息
        """
        data = package_data(remove_key(locals()))
        return await self._request_coin_margined_private_api("get", "swap_api_trading_status", data=data)

    #### 币本位永续合约交易接口 #####
    async def coin_margined_create_order(
            self, direction, volume: int, offset, order_price_type, lever_rate=None, contract_code=None,
            client_order_id=None, price=None, tp_trigger_price=None, tp_order_price=None,
            tp_order_price_type=None, sl_trigger_price=None, sl_order_price=None, sl_order_price_type=None):
        """
        开单
        contract_code	string	true	合约代码,支持大小写,"BTC-USD"
        client_order_id	long	false	客户自己填写和维护，必须为数字, 请注意必须小于等于9223372036854775807
        price	decimal	false	价格
        volume	long	true	委托数量(张)
        direction	string	true	"buy":买 "sell":卖
        offset	string	true	"open":开 "close":平
        lever_rate	int	true	杠杆倍数[“开仓”若有10倍多单，就不能再下20倍多单;首次使用高倍杠杆(>20倍)，请使用主账号登录web端同意高倍杠杆协议后，才能使用接口下高倍杠杆(>20倍)]
        order_price_type	string	true	订单报价类型 "limit":限价，"opponent":对手价 ，"post_only":只做maker单,post only下单只受用户持仓数量限制,"optimal_5"：最优5档，"optimal_10：最优10档，"optimal_20"：最优20档，"fok":FOK订单，"ioc":IOC订单, opponent_ioc"： 对手价-IOC下单，"optimal_5_ioc"：最优5档-IOC下单，"optimal_10_ioc"：最优10档-IOC下单，"optimal_20_ioc"：最优20档-IOC下单,"opponent_fok"： 对手价-FOK下单，"optimal_5_fok"：最优5档-FOK下单，"optimal_10_fok"：最优10档-FOK下单，"optimal_20_fok"：最优20档-FOK下单
        tp_trigger_price	decimal	false	止盈触发价格
        tp_order_price	decimal	false	止盈委托价格（最优N档委托类型时无需填写价格）
        tp_order_price_type	string	false	止盈委托类型 不填默认为limit; 限价：limit ，最优5档：optimal_5，最优10档：optimal_10，最优20档：optimal_20
        sl_trigger_price	decimal	false	止损触发价格
        sl_order_price	decimal	false	止损委托价格（最优N档委托类型时无需填写价格）
        sl_order_price_type	string	false	止损委托类型 不填默认为limit; 限价：limit ，最优5档：optimal_5，最优10档：optimal_10，最优20档：optimal_20

        备注
        对手价下单price价格参数不用传，对手价下单价格是买一和卖一价,"optimal_5"：最优5档，"optimal_10：最优10档，"optimal_20"：最优20档下单price价格参数不用传，"limit":限价，"post_only":只做maker单 需要传价格。
        若存在持仓，那么下单时杠杆倍数必须与持仓杠杆相同，否则下单失败。若需使用新杠杆下单，则必须先使用切换杠杆接口将持仓杠杆切换成功后再下单。
        只有开仓订单才支持设置止盈止损。
        止盈触发价格为设置止盈单必填字段，止损触发价格为设置止损单必填字段；若缺省触发价格字段则不会设置对应的止盈单或止损单。

        开平方向
        开多：买入开多(direction用buy、offset用open)

        平多：卖出平多(direction用sell、offset用close)

        开空：卖出开空(direction用sell、offset用open)

        平空：买入平空(direction用buy、offset用close)
        """
        data = package_data(remove_key(locals()))
        return await self._request_coin_margined_private_api("post", "swap_order", data=data)

    async def coin_margined_batch_create_order(self, orders_data: list):
        """
        批量开单
        :param orders_data: 参数同开单接口
        :return:
        """
        data = package_data(remove_key(locals()))
        return await self._request_coin_margined_private_api("post", "swap_batchorder", data=data)

    async def coin_margined_cancel_order(self, contract_code, order_id=None, client_order_id=None):
        """
        撤销订单
        order_id	false (请看备注)	string	订单ID(多个订单ID中间以","分隔,一次最多允许撤消10个订单)
        client_order_id	false (请看备注)	string	客户订单ID(多个订单ID中间以","分隔,一次最多允许撤消10个订单)
        contract_code	true	string	合约代码,支持大小写,"BTC-USD"

        备注：
        order_id和client_order_id都可以用来撤单，至少要填写一个,同时只可以设置其中一种，如果设置了两种，默认以order_id来撤单。
        撤单接口返回结果只代表撤单命令发送成功，建议根据订单查询接口查询订单的状态来确定订单是否已真正撤销。
        client_order_id，8 小时有效，超过 8 小时的订单根据client_order_id将查询不到。
        """
        assert contract_code is not None
        data = package_data(remove_key(locals()))
        return await self._request_coin_margined_private_api("post", "swap_cancel", data=data)

    async def coin_margined_cancel_all(self, contract_code, direction=None, offset=None):
        """
        全部撤单
        contract_code	true	string	合约代码,支持大小写，"BTC-USD"
        direction	false	string	买卖方向（不填默认全部） "buy":买 "sell":卖
        offset	false	string	开平方向（不填默认全部） "open":开 "close":平

        备注
        direction与offset可只填其一，只填其一则按对应的条件去撤单。（如用户只传了direction=buy，则撤销所有买单，包括开仓和平仓）
        """
        data = package_data(remove_key(locals()))
        return await self._request_coin_margined_private_api("post", "swap_cancelall", data=data)

    async def coin_margined_switch_lever_rate(self, contract_code, lever_rate: int):
        """
        切换杠杆
        contract_code	true	string	合约代码	比如“BTC-USD

        备注
        只有在单个品种下只有持仓，且没有挂单的场景下，才可以切换该品种当前的倍数。
        接口限制请求次数为每3秒一次。
        """
        data = package_data(remove_key(locals()))
        return await self._request_coin_margined_private_api("post", "swap_switch_lever_rate", data=data)

    async def coin_margined_order_info(self, contract_code, order_id=None, client_order_id=None):
        """
        订单信息
        参数名称	是否必须	类型	描述
        order_id	false（请看备注）	string	订单ID(多个订单ID中间以","分隔,一次最多允许查询50个订单)
        client_order_id	false（请看备注）	string	客户订单ID(多个订单ID中间以","分隔,一次最多允许查询50个订单)
        contract_code	true	string	合约代码,支持大小写,"BTC-USD"

        最多只能查询 2 小时内的撤单信息。
        order_id和client_order_id至少要填写一个。
        order_id和client_order_id都可以用来查询，同时只可以设置其中一种，如果设置了两种，默认以order_id来查询。结算后，会把结束状态的订单（5部分成交已撤单 6全部成交 7已撤单）删除掉。
        client_order_id，8 小时有效，超过 8 小时的订单根据client_order_id将查询不到。
        """
        data = package_data(remove_key(locals()))
        return await self._request_coin_margined_private_api("post", "swap_order_info", data=data)

    async def coin_margined_order_detail(self, contract_code, order_id, create_at: int = None, order_type=None,
                                         page_index=1, page_size=20):
        """
        订单明细信息
        参数名称	是否必须	类型	描述
        contract_code	true	string	合约代码,支持大小写,"BTC-USD"
        order_id	true	long	订单id
        created_at	false	long	下单时间戳
        order_type	false	int	订单类型，1:报单 、 2:撤单 、 3:强平、4:交割
        page_index	false	int	第几页,不填第一页
        page_size	false	int	不填默认20，不得多于50

        获取订单明细接口查询撤单数据时，如果传“created_at”和“order_type”参数则能查询最近6小时数据，如果不传“created_at”和“order_type”参数只能查询到最近2小时数据。
        order_id返回是18位，nodejs和javascript默认解析18有问题，nodejs和javascript里面JSON.parse默认是int，超过18位的数字用json-bigint的包解析。
        created_at使用13位long类型时间戳（包含毫秒时间），如果输入准确的时间戳，查询性能将会提升。例如:"2019/10/18 10:26:22"转换为时间戳为：1571365582123。也可以直接从contract_order下单接口返回的ts中获取时间戳查询对应的订单。
        created_at禁止传0。
        """
        data = package_data(remove_key(locals()))
        return await self._request_coin_margined_private_api("post", "swap_order_detail", data=data)

    async def coin_margined_open_orders(self, contract_code, page_index=1, page_size=20, sort_by="created_at", trade_type=0):
        """
        获取合约当前未成交委托

        参数名称	是否必须	类型	描述	默认值	取值范围
        contract_code	true	string	合约代码	支持大小写,"BTC-USD" ...
        page_index	false	int	页码，不填默认第1页	1
        page_size	false	int			不填默认20，不得多于50
        sort_by	false	string	排序字段，不填默认按创建时间倒序	created_at	“created_at”(按照创建时间倒序)，“update_time”(按照更新时间倒序)
        trade_type	false	int	交易类型，不填默认查询全部	0	0:全部,1:买入 开多,2: 卖出开空,3: 买入平空,4: 卖出平多。
        """
        data = package_data(remove_key(locals()))
        return await self._request_coin_margined_private_api("post", "swap_openorders", data=data)

    async def coin_margined_match_result(self, contract_code, trade_type, create_date, page_index=1, page_size=20):
        """
        获取历史成交记录

        参数名称	是否必须	类型	描述	默认值	取值范围
        contract_code	true	string	合约代码	支持大小写，"BTC-USD" ...
        trade_type	true	int	交易类型		0:全部,1:买入开多,2: 卖出开空,3: 买入平空,4: 卖出平多,5: 卖出强平,6: 买入强平
        create_date	true	int	日期		可随意输入正整数，如果参数超过90则默认查询90天的数据
        page_index	false	int	页码，不填默认第1页	1
        page_size	false	int	不填默认20，不得多于50	20
        """
        data = package_data(remove_key(locals()))
        return await self._request_coin_margined_private_api("post", "swap_matchresults", data=data)

    async def coin_margined_lightning_close_position(self, contract_code, volume, direction, client_order_id=None,
                                                     order_price_type=constants.OrderPriceType.LIGHTNING):
        """
        闪电平仓
        """
        data = package_data(remove_key(locals()))
        return await self._request_coin_margined_private_api("post", "swap_lightning_close_position", data=data)

    #### U本位永续合约交易接口 #####
    async def usd_margined_cancel_order(self, contract_code, order_id=None, client_order_id=None, cross=True):
        """
        【全仓】撤销订单
        """
        assert contract_code is not None
        data = package_data(remove_key(locals(), "self,cross"))
        return await self._request_usd_margined_private_api(
            "post", "swap_cross_cancel" if cross else "swap_cancel", data=data
        )


























