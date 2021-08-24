"""
导入本模块:
from kw618.k_finance.Arbitrage.binance_gateway import *
"""
import json
import pandas as pd
import websocket
import ssl

# 导入常用的固定路径(多平台通用)
from kw618._file_path import *
# 本脚本依赖很多 utils_requests的函数和模块, 直接用*  (注意要避免循环导入问题)
from kw618.k_requests.utils_requests import *
from kw618.k_requests.ocr import *
from kw618.k_python.utils_python import *
from kw618.k_pandas.utils_pandas import *

from kw618.k_finance.const import *
from kw618._file_path import *

req = myRequest().req
# client = pymongo.MongoClient(f'mongodb://kerwin:kw618@{HOST}:27017/')
# db_for_quant = client["quant"]
# remote_client = pymongo.MongoClient(f'mongodb://kerwin:kw618@{REMOTE_HOST}:27017/')
# remote_db_for_quant = remote_client["quant"]

class BinanceAccount(myRequest):
    """
        note:
            - 币安REST的API接口. 用于'一次性'访问 行情数据/ 账户数据/ 历史交易数据/ 订单数据 等
                (自己写的) (可以参考vnpy的网关模型优化)

            - 该类前半段用来实现请求数据的'打包'操作 (request), 后半段封装了官网常用的api接口 (通过'函数传参'方式调用)
            - 特别重要的4个接口:
                    // todo: 5个账户都可以共同使用一个函数api
                1. 下单接口:
                    send_order()
                        - 已经实现了5个账户共用一个api (现货/全仓杠杆/逐仓杠杆/u本位合约/币本位合约)
                2. 查询当前account余额/持仓:
                    req_account()
                        - 已经实现了5个账户共用一个api (现货/全仓杠杆/逐仓杠杆/u本位合约/币本位合约)
                3. 查询历史成交订单:
                    req_myTrades()
                4. 两个ws (行情ws+账户ws):
                    i. subscribe_market_data()
                    ii. subscribe_trade_data()

            - 命名规范:
                - req: 网络请求接口 (需要用到self.request的api)
                - get: 本地请求接口 (本身功能非网络请求, 但允许调用上面的网络接口)
                - cal: 计算接口
    """

    def __init__(self, settings):
        """
        usage:
            ba = BinanceAccount(LSH_BINANCE_SETTING)
        """
        # 基础的网络请求参数
        self.api_key = settings.get("key") # 哲丞的api
        self.secret_key = settings.get("secret")
        self.account_name = settings.get("account_name")
        self.user = self.account_name
        self.other_headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-MBX-APIKEY": self.api_key, # api key
        }
        # self.api_type = api_type


        # 1. 现货
        self.spot_host = "https://api.binance.com"
        # 2. u本位合约
        self.futures_host = "https://fapi.binance.com"
        dualSidePosition = self.req_positionSide(account_type="futures").get("dualSidePosition", True)
        self.futures_positionSide = "DOUBLE" if dualSidePosition else "SINGLE" #  // "true": 双向持仓模式；"false": 单向持仓模式
        # 3. 币本位合约
        self.dfutures_host = "https://dapi.binance.com"
        dualSidePosition = self.req_positionSide(account_type="dfutures").get("dualSidePosition", True)
        self.dfutures_positionSide = "DOUBLE" if dualSidePosition else "SINGLE" #  // "true": 双向持仓模式；"false": 单向持仓模式


        self.listen_key = ""
        # self.listen_keys的结构: {"listen_keys_spot":'abc', "listen_keys_fullMargin":"abcde", "listen_keys_isoMargin":{"BNBUSDT":'abc', "ETHUSDT":'xyz'}}
        self.listen_keys = {} #
    """
    notes:
    todo:
        1. [超级重要]req_account: 需要对5个账户分别进行处理, 并输出5个核心df (尽可能展示所有数据: 必须包含最重要的风控指标!!)
                        (原始数据接口5个+df数据接口5个+汇总df接口1个)
            - get_futures_account_df/ get_dfutures_account_df 函数的实现...
            - 当上面的函数实现后, 其实就可以让'每日报表导出'脚本 直接调用这些封装好的函数
        2. subscribe_trade_data: 现货可以订阅3个account_type, 币本位也要实现... (5个账户的listen_key也要每半小时keep下去)
        3. subscribe_market_data: 解决ws莫名其妙断开的问题...
        4. [也很着急] send_order:
            i. 如何让下单接口和价差率获取接口绑定 (当捕捉到某个价差率才下单...)
            ii. 实现类似k_vnpy的双边下单接口 (该接口也需要能check余额后再下单, 否则终止下单....)
            思考:
                - 自己写的框架可以完全脱离k_vnpy来进行套利吗? (灵活度更高, 耦合性更低)

    """
    # 一. 基础接口
    # ====================================================================
        # 1. 底层数据请求
    def request(self, host="", path="", query_dict={}, verify=False, req_method="get", proxies=None, is_obj=True):
        """
            notes: 该类专属的请求函数 (类似于robust_req函数) (不去覆盖myRequest.req函数)
            function:
            params:
                path: 在host后面的具体路径
                query_dict: dict格式的'请求参数' (在路径后面的query参数)
                verify: 是否需要签名 (币安api有明确标明)
                proxies: 默认是None. (之前需要用clash代理才能访问, 现在好像不需要了..)
        """

        # host = host if host else self.host
        # if need_timestamp is True:
        #     # 有些请求就不需要'时间戳', 带上了反而报错... (ticker/price路径...)
        #     query_dict.update({"timestamp" : self.get_binance_timestamp()})
        if verify != True:
            query_str = self.build_parameters(query_dict)
        elif verify is True:
            query_dict.update({"timestamp" : self.get_binance_timestamp()})
            query_str = self.build_parameters(query_dict)
            sign = self.get_binance_sign(query_str)
            query_str = query_str + f"&signature={sign}"
        url = host + path + '?' + query_str

        # r = requests.get(url, headers=self.other_headers)
        # print(r)
        # print("\n-----------------------\n")

        # 默认返回一个obj (因为后期需要通过resp_obj.status_code 来判断网络传输是否正常)
        resp_obj = self.req(
            url=url, other_headers=self.other_headers, req_method=req_method,
            proxies=proxies, is_obj=is_obj
        )
        return resp_obj

        # 2. 获取币安时间
    def get_binance_timestamp(self):
        "生成币安接口所需的时间戳数值 (类型:int, 单位:毫秒)"
        binance_timestamp = int(time.time() * 1000) # time.time()方法返回的时间戳单位是秒; 币安要求是毫秒, 所以*1000
        return binance_timestamp

        # 3. 获取币安签名
    def get_binance_sign(self, query_str, secret_key=""):
        """
            function: 生成币安的签名
            params:
                query_str: str格式的'原请求参数'
                secret_key: 使用 SECRETKEY 作为密钥
            return: str格式的'签名'
        """
        secret_key = secret_key if secret_key else self.secret_key
        signature = k_hmac_sha256(key=secret_key, data=query_str)
        # print(f"\n\n该请求的币安签名为: {signature}\n\n")
        return signature


    # 二. 核心数据请求接口
    # ====================================================================
    # 1. 订单处理
        # i. 下单
    # @timer # 计时器: 用于检测该请求的耗时
    def send_order(
            self, account_type="spot", symbol="ALPHAUSDT", offset="OPEN", direction="BUY", order_type="LIMIT",
            price=0, quantity=0, quoteOrderQty=0, stopPrice=0, icebergQty=0,
            timeInForce="GTC", newOrderRespType="ACK", ClientOrderId="",
            workingType=None, priceProtect=False,
        ):
        """
            functions:
                - '下单'
            args:
                (前面3个'yes'的参数是必须要传给服务器的)
                - symbol: 需要大写  (eg: BNBUSDT) [yes]
                - offset: "OPEN"/"CLOSE"
                    对应币安API接口的 positionSide: 持仓方向; (即: 这里的'买入'是'开仓'还是'平仓')
                                (单向持仓模式下非必填，默认且仅可填BOTH; 在双向持仓模式下必填,且仅可选择 LONG 或 SHORT)
                                (合约下单的话, 需要先确定'开仓'还是'平仓', 你说的'买入'和'卖出'才能明确真实的含义)
                - direction: "BUY"/"SELL" [yes]
                    对应币安API接口的 side: "BUY" or "SELL"
                - order_type: [yes]
                        0. 我自己习惯的表达:
                            "LIMIT": 限价单
                            "MARKET": 市价单
                            "STOP_LOSS_MARKET": 市价止损单
                            "STOP_LOSS_LIMIT": 限价止损单
                            "TAKE_PROFIT_MARKET": 市价止盈单
                            "TAKE_PROFIT_LIMIT": 限价止盈单
                            "LIMIT_MAKER": 限价只挂单 (如果一挂上就是吃掉别人, 那会撤销这笔交易)
                            "TRAILING_STOP_MARKET": 暂时还不知道干啥用的...
                        1. 现货:
                            "LIMIT": 限价单
                            "MARKET": 市价单
                            "STOP_LOSS": 市价止损单
                            "STOP_LOSS_LIMIT": 限价止损单
                            "TAKE_PROFIT": 市价止盈单
                            "TAKE_PROFIT_LIMIT": 限价止盈单
                            "LIMIT_MAKER": 限价只挂单 (如果一挂上就是吃掉别人, 那会撤销这笔交易)
                        2. 合约:
                            "LIMIT": 限价单
                            "MARKET": 市价单
                            "STOP_MARKET": 市价止损单
                            "STOP": 限价止损单
                            "TAKE_PROFIT_MARKET": 市价止盈单
                            "TAKE_PROFIT": 限价止盈单
                            "TRAILING_STOP_MARKET": 暂时还不知道干啥用的...
                - price: 价格
                - quantity: 数量 (标的资产的数量) (即: ETH/USDT中 ETH的数量)
                            // 如果是币本位, 这里的quantity代表'张数'
                - stopPrice: 止损价格 (也就是'触发价格') (只有'stop单'才需要这个参数)
                            (只有STOP_LOSS,STOP_LOSS_LIMIT,TAKE_PROFIT,TAKE_PROFIT_LIMIT需要这个参数)
                - icebergQty: 冰山委托数量 (只有'限价单'才需要这个参数) [测试了好几次, 没发现和普通限价单有什么区别?? 之后再测试]
                            (只有LIMIT,STOP_LOSS_LIMIT,TAKE_PROFIT_LIMIT需要这个参数)
                - quoteOrderQty: 想要买入的'计价币'的数量 (即: ETH/USDT中 USDT的数量)
                - timeInForce:
                                (只有限价单才需要, 市价单传递这个参数会报错)
                            GTC: 成交为止; 订单会一直有效，直到被成交或者取消。
                            IOC: 无法立即成交的部分就撤销; 订单在失效前会尽量多的成交
                            FOK: 无法全部立即成交就撤销; 如果无法全部成交，订单会失效 (可能适合双腿下单??)
                - newOrderRespType: ACK的返回速度最快; RESULT第二快, FULL最慢(返回吃单成交的详细信息)
                            ("MARKET"和" LIMIT"订单类型默认为"FULL"，所有其他订单默认为"ACK")
                - ClientOrderId: 客户自定义的唯一订单ID。 如果未发送，则自动生成; (便于后面撤单!!)
                - workingType: stopPrice 触发类型: MARK_PRICE(标记价格), CONTRACT_PRICE(合约最新价). 默认 CONTRACT_PRICE
                            (只有止盈/止损订单才需要这个参数)
                            # 用'标记价格'还是'最新价格'来决定止损/止盈价格线
                - priceProtect: 条件单触发保护："TRUE","FALSE", 默认"FALSE".
                                (仅 STOP, STOP_MARKET, TAKE_PROFIT, TAKE_PROFIT_MARKET 需要此参数)
                                达到触发价时，MARK_PRICE(标记价格)与CONTRACT_PRICE(合约最新价)之间的价差不能超过改symbol触发保护阈; 否则不触发交易
                - account_type: "spot"/ "fullMargin"/ "isoMargin" (杠杆账户专用参数)
                - isisolated: 是否为'逐仓账户' (杠杆账户专用参数)
                            ("TRUE"/"FALSE") 必须是字符串的形式

            notes:
                - 限价单: 必须要传递'timeInForce'这个参数!!
                - 市价单: 不能传price参数
                - 合约平仓单: 现货and合约都必须要有足够的资产才可以'挂卖单', 如果没有持仓就'挂卖单', 则会报错!!
                - 限制单的委托价限制范围一般都比较广..

            其他信息:
                LIMIT_MAKER是LIMIT订单，如果它们立即匹配并成为吃单方将被拒绝。
                当触发stopPrice时，STOP_LOSS和TAKE_PROFIT将执行MARKET订单。
                任何LIMIT或LIMIT_MAKER类型的订单都可以通过发送icebergQty而成为iceberg订单。 (冰山委托就是这么来的)
                任何带有icebergQty的订单都必须将timeInForce设置为GTC。
                使用 quantity 的市价单 MARKET 明确的是用户想用市价单买入或卖出的数量。
                    比如在BTCUSDT上下一个市价单, quantity用户指明能够买进或者卖出多少BTC。
                使用 quoteOrderQty 的市价单MARKET 明确的是通过买入(或卖出)想要花费(或获取)的报价资产数量; 此时的正确报单数量将会以市场流动性和quoteOrderQty被计算出来。
                    以BTCUSDT为例, quoteOrderQty=100:
                        下买单的时候, 订单会尽可能的买进价值100USDT的BTC.
                        下卖单的时候, 订单会尽可能的卖出价值100USDT的BTC.
                使用 quoteOrderQty 的市价单MARKET不会突破LOT_SIZE的限制规则; 报单会按给定的quoteOrderQty尽可能接近地被执行。
                除非之前的订单已经成交, 不然设置了相同的ClientOrderId订单会被拒绝。

            return:
                - 所有币种的交易规则: {}

            usage:
                # 左腿卖出
                ba.send_order(
                    account_type="isoMargin", symbol="DOGEUSDT", offset="OPEN", direction="SELL",
                    order_type="MARKET", price=None, quantity=20,
                )
                # 右腿买入
                ba.send_order(
                    account_type="futures", symbol="DOGEUSDT_PERP", offset="OPEN", direction="BUY",
                    order_type="MARKET", price=None, quantity=20,
                )

        """
        # 0.输入值检验
        if account_type not in ["spot", "fullMargin", "isoMargin", "futures", "dfutures"]:
            raise Exception(f"[输入异常] account_type:{account_type}")
        symbol = symbol.upper()
        if account_type == "futures":
            if "_PERP" in symbol:
                symbol, _ = symbol.split("_")
        offset = offset.upper()
        direction = direction.upper()
        order_type = order_type.upper()
        # 1. 制造/打包请求数据
        req_method = "post"
        query_dict = {
            "symbol" : symbol,
            "side" : DIRECTION_KW2BINANCES[direction],
            # "recvWindow" : 5000,
        }
        verify = True

        if account_type == "spot":
            host = self.spot_host
            path = "/api/v3/order"
            type = ORDERTYPE_SPOT_KW2BINANCE[order_type] # 将我习惯的order_type转变成binance的类型
            query_dict.update({"type":type})
        elif account_type == "fullMargin":
            host = self.spot_host
            path = "/sapi/v1/margin/order"
            type = ORDERTYPE_SPOT_KW2BINANCE[order_type] # 将我习惯的order_type转变成binance的类型
            isIsolated = "FALSE"
            query_dict.update({"type":type, "isIsolated":isIsolated})
        elif account_type == "isoMargin":
            host = self.spot_host
            path = "/sapi/v1/margin/order"
            type = ORDERTYPE_SPOT_KW2BINANCE[order_type] # 将我习惯的order_type转变成binance的类型
            isIsolated = "TRUE"
            query_dict.update({"type":type, "isIsolated":isIsolated})
        elif account_type == "futures":
            host = self.futures_host
            path = "/fapi/v1/order"
            type = ORDERTYPE_FUTURES_KW2BINANCE[order_type] # 将我习惯的order_type转变成binance的类型
            query_dict.update({"type":type})
        elif account_type == "dfutures":
            host = self.dfutures_host
            path = "/dapi/v1/order"
            type = ORDERTYPE_DFUTURES_KW2BINANCE[order_type] # 将我习惯的order_type转变成binance的类型
            query_dict.update({"type":type})
            # 请求内容 (参数需要参考官网API)
        if offset: # '开仓'还是'平仓'
            if account_type == "futures":
                if self.futures_positionSide == "DOUBLE":
                    query_dict["positionSide"] = OFFSET_KW2BINANCES[(offset, direction)]
                elif self.futures_positionSide == "SINGLE":
                    query_dict["positionSide"] = "BOTH"
                # query_dict["reduceOnly"] = False # 双开模式下, 传入该参数会报错...
            if account_type == "dfutures":
                if self.dfutures_positionSide == "DOUBLE":
                    query_dict["positionSide"] = OFFSET_KW2BINANCES[(offset, direction)]
                elif self.dfutures_positionSide == "SINGLE":
                    query_dict["positionSide"] = "BOTH"
                # query_dict["reduceOnly"] = False # 双开模式下, 传入该参数会报错...
        if price:
            if (order_type not in MARKET_ORDER_TYPES):
                query_dict["price"] = price # 只有'非市价单', 才需要传入price参数. (市价单传入price会报错)
        if quantity:
            query_dict["quantity"] = quantity # // 如果是币本位, 这里的quantity代表'张数'
        if stopPrice:
            query_dict["stopPrice"] = stopPrice
        if icebergQty:
            query_dict["icebergQty"] = icebergQty
        if timeInForce:
            # 只有限价单类型, 才需要这个传递'timeInForce'参数 (其他类型传递这个参数都会报错)
            if (order_type in LIMIT_ORDER_TYPES):
                query_dict["timeInForce"] = timeInForce # 默认是'GTC'  (订单一直持续有效)
        if ClientOrderId:
            query_dict["newClientOrderId"] = ClientOrderId
        if newOrderRespType:
            query_dict["newOrderRespType"] = newOrderRespType
        if workingType: # 用'标记价格'还是'最新价格'来决定止损/止盈价格线
            if (account_type == "futures") and (order_type in STOP_ORDER_TYPES):
                query_dict["workingType"] = workingType
        if priceProtect: # 是否开启价差保护
            if (account_type == "futures") and (order_type in STOP_ORDER_TYPES):
                query_dict["priceProtect"] = priceProtect

        # 2. 发送请求
        resp_obj = self.request(
            req_method = req_method,
            host = host,
            path = path,
            query_dict = query_dict,
            verify = verify,
        )
            # 检测1. 状态码必须是要 '2' 开头的才是正常的!!
        if resp_obj.status_code // 100 != 2:
            msg = f"获取数据失败，状态码：{resp_obj.status_code}，信息：{resp_obj.text}"
            print(msg)
            return {}
        else:
            data = resp_obj.json() # type: [[e, e],]
            # 检测2. 返回的数据要非空!
            if not data:
                msg = f"返回数据为空"
                logger.log(20, msg)
                return {}
            else:
                logger.log(logging.DEBUG, f'send_order成功: {data}')
                return data

        # ii. 撤销下单
    def cancel_order(self, account_type="spot", symbol="", orderId="", ClientOrderId=""):
        """
            function: 撤销下单
            args:
                - symbol: 需要大写  (eg: BNBUSDT)
                - orderId: '服务器端' 生成的 '订单id'
                - ClientOrderId: '本地客制化' 生成的 '订单id'

        """
        req_method = "delete"
        if (account_type == "spot") or (account_type == "fullMargin") or (account_type == "isoMargin"):
            host = self.spot_host
            path = "/api/v3/order"
        elif account_type == "futures":
            host = self.futures_host
            path = "/fapi/v1/order"
        elif account_type == "dfutures":
            host = self.futures_host
            path = "/dapi/v1/order"
        verify = True
            # 请求内容 (参数需要参考官网API)
        query_dict = {
            "symbol" : symbol.upper(),  # symbol需要大写
        }
        if orderId:
            query_dict["orderId"] = orderId
        if ClientOrderId:
            query_dict["origClientOrderId"] = ClientOrderId

        # 2. 发送请求
        resp_obj = self.request(
            req_method = req_method,
            host = host,
            path = path,
            query_dict = query_dict,
            verify = verify,
        )
            # 检测1. 状态码必须是要 '2' 开头的才是正常的!!
        canceled_order_dict = {}
        if resp_obj.status_code // 100 != 2: # eg: startTime填错了, status_code就会变成400.
            msg = f"获取数据失败，状态码：{resp_obj.status_code}，信息：{resp_obj.text}"
            print(msg)
            return canceled_order_dict
        else:
            data = resp_obj.json() # type: [[e, e],]
            # 检测2. 返回的数据要非空!
            if not data:
                msg = f"返回数据为空"
                logger.log(20, msg)
                return canceled_order_dict
            else:
                canceled_order_dict = resp_obj.json()
                logger.log(logging.DEBUG, f'cancel_order 成功: {canceled_order_dict}')
                return canceled_order_dict

    # 2. 账户查询
    def req_account(self, account_type="spot", is_obj=False):
        """
            function: 获取账户持仓数据

            notes:
                - 接口的数据结构:
                    asset_lst[0]:
                        # (其实asset_lst中只需要看USDT这个asset就行了, 因为这个是决定合约能开多少仓位的关键!! 因为保证金是按USDT来缴纳的)
                        asset                               USDT
                        walletBalance              9200.00186834  # 钱包余额 (即: 总保证金数) (也是平时计算资金费收入会看的值)
                        unrealizedProfit           1350.07208817  # 整个全仓账户中的'未实现盈亏'
                        marginBalance             10550.07395651  # 保证金余额  (即: 钱包余额+未实现盈亏)
                        maintMargin                 235.63444287  # 维持保证金
                        initialMargin              5812.82887979  # 初始保证金 (没啥用..不用管...)
                        positionInitialMargin      5812.82887979
                        openOrderInitialMargin        0.00000000
                        maxWithdrawAmount          4737.24507672  # 可用划转余额 (跟你现在的杠杆倍数有关) (该余额决定了合约还能开仓多少..)
                        crossWalletBalance         9200.00186834
                        crossUnPnl                 1350.07208817
                        availableBalance           4737.24507672  # 同上

                    position_lst[0]:
                        symbol                          LITUSDT
                        initialMargin               12.93981834  # 初始保证金
                        maintMargin                  2.58796366  # 维持保证金
                        unrealizedProfit             6.98523308  # 未实现盈亏 (浮盈)
                        positionInitialMargin       12.93981834  # 仓位初始保证金 ***(和上面有啥区别??)
                        openOrderInitialMargin                0
                        leverage                             20  # 杠杆倍数
                        isolated                          False
                        entryPrice                       9.4922  # 开仓价格 (即: 成本价)
                        maxNotional                       25000
                        positionSide                      SHORT
                        positionAmt                       -28.0  # 净持仓量
                        notional                  -258.79636692  # 当前的'名义市值' (即:持仓量*最新标记价格)
                        isolatedWallet                        0

                - 该接口的权重是5分
                - 现货每分钟的权重上限是1200分, 合约上限是2400分.
            usage:
                    # 现货
                d = ba.req_account(account_type="spot")
                    # 全仓
                d = ba.req_account(account_type="fullMargin")
                    # 逐仓
                d = ba.req_account(account_type="isoMargin")
                    # u本位
                d = ba.req_account(account_type="futures")
                    # 币本位
                d = ba.req_account(account_type="dfutures")


        """
        req_method = "get"
        verify = True
        query_dict = {
        }
        if account_type == "spot":
            host = self.spot_host
            path = "/api/v3/account"
        elif account_type == "fullMargin":
            host = self.spot_host
            path = "/sapi/v1/margin/account"
        elif account_type == "isoMargin":
            host = self.spot_host
            path = "/sapi/v1/margin/isolated/account"
        elif account_type == "futures":
            host = self.futures_host
            path = "/fapi/v2/account"
        elif account_type == "dfutures":
            host = self.dfutures_host
            path = "/dapi/v1/account"
            # 请求内容 (参数需要参考官网API)
        # 2. 发送请求
        response_obj = self.request(
            req_method = req_method,
            host = host,
            path = path,
            query_dict = query_dict,
            verify = verify,
        )
        if is_obj:
            # 直接返回对象, 可以取到response_obj.headers  (headers里可以看到最近这1分钟内花了多少权重...)
            return response_obj
        # 检测1. 状态码必须是要 '2' 开头的才是正常的!!
        if response_obj.status_code // 100 != 2:
            msg = f"获取数据失败，状态码：{response_obj.status_code}，信息：{response_obj.text}"
            print(msg)
            return {}
        else:
            response_dict = response_obj.json() # type: [[e, e],]
            # 检测2. 返回的数据要非空!
            if not response_dict:
                msg = f"返回数据为空"
                logger.log(20, msg)
                return {}
            else:
                # # 如果是合约的话, 就获取所有币种的仓位信息...
                # if self.api_type == "futures":
                #     position_lst = response_dict.get("positions")
                #     response_dict = {"assets":response_dict.get("assets"), "positions":[]}
                #     for position_dict in position_lst:
                #         if float(position_dict.get('positionAmt')):
                #             response_dict.get("positions").append(position_dict)
                logger.log(logging.DEBUG, f'req_account成功: {response_dict}')
                return response_dict # 统一返回'原生dict' (合约账户包含asset3个计价资产, 和所有position仓位)

    def get_spot_account_df(self, account_type="spot"):
        """
        usage:
            df = ba.get_spot_account_df()
        """
        d = self.req_account(account_type="spot")
        spot_balances_lst = d.get("balances")
            # free数量 + locked数量 = 总现货数量
        spot_balances_lst = [b for b in spot_balances_lst if float(b.get("free")) or float(b.get("locked"))] # 挂着委托单会被lock
        df = pd.DataFrame(spot_balances_lst)
        if len(df):
            df[["free", "locked"]] = df[["free", "locked"]].apply(pd.to_numeric)
        else:
            df = pd.DataFrame()
        df["现货-总数量"] = df["free"] + df["locked"]
        # df["account_type"] = "现货"
        # df["asset_type"] = "余额"
        return df

    def get_fullMargin_account_df(self, account_type="fullMargin"):
        """
        usage:
            df = ba.get_fullMargin_account_df()
        """
        d = self.req_account(account_type="fullMargin")
        fullMargin_riskRate = float(d.get("marginLevel", 999)) # 风险率 (越高越好, 币安这个英文命名太误导人了...)
        userAssets = d.get("userAssets")
            # 坑点:
                # - 这里的free就是指 "可用资产", 不是'总资产'!!!!
                # - 所以, 挂着委托单的币, 就会被locked (从'free'中的数量转移到'locked'中)
                # - 全仓杠杆中的'总资产' = free + locked
                # - 全仓杠杆中的'净资产' = free + locked - borrowed - interest      (netAsset)  [即: 余额]
                    # (只要上面4个数据中, 有一个非空, 就应该获取下来, 整合计算余额) (borrowed和interest作为负值)
        fullMargin_asset_lst = []
        for asset in userAssets:
            if float(asset.get("free")) or float(asset.get("locked")) or float(asset.get("borrowed")) or float(asset.get("interest")):
                fullMargin_asset_lst.append(asset)
        if fullMargin_asset_lst:
            # 生成df (数字数字化)
            df = pd.DataFrame(fullMargin_asset_lst)
            df[["free", "locked", "borrowed", "interest"]] = df[["free", "locked", "borrowed", "interest"]].apply(pd.to_numeric)
            # 获取资产的usdt计价表
            asset_price_df = self.req_asset_price()
            # 全仓资产数量
            df["全仓_总数量"] = df["free"] + df["locked"]
            df["全仓_总借款量"] = df["borrowed"]
            df["全仓_总利息量"] = df["interest"]
            df["全仓_净数量"] = df["free"] + df["locked"] - df["borrowed"] - df["interest"]
            # 获取全仓资产价格 & 计算资产市值
            df = pd.merge(df, asset_price_df, how="left", on="asset")
            df["全仓_总市值"] = df["全仓_总数量"] * df["price"]
            df["全仓_净市值"] = df["全仓_净数量"] * df["price"]
            df["全仓_借款市值"] = df["全仓_总借款量"] * df["price"]
            df["全仓_利息市值"] = df["全仓_总利息量"] * df["price"]
            df["全仓_风险率"] = fullMargin_riskRate
            df = df.sort_values("全仓_净市值", ascending=False)
            df = df.reset_index(drop=True)
        else:
            df = pd.DataFrame()
        return df

    def get_isoMargin_account_df(self, account_type="isoMargin"):
        """
        usage:
            df = ba.get_isoMargin_account_df()
        """
        d = self.req_account(account_type="isoMargin")
        isoMargin_balances = []
        for doc in d.get("assets"):
            baseAsset = doc.get("baseAsset") # 标的资产的dict
            quoteAsset = doc.get("quoteAsset") # 计价资产的dict
            symbol = doc.get("symbol")
            isoMargin_riskRate = doc.get("marginLevel") # 风险率 (越高越好, 币安这个英文命名太误导人了...)
            liquidatePrice = doc.get("liquidatePrice") # 爆仓价格
            liquidateRate = doc.get("liquidateRate") # 爆仓涨幅
                # i. 标的资产
            base_asset = baseAsset.get("asset")
            base_free = baseAsset.get("free")
            base_locked = baseAsset.get("locked")
            base_borrowed = baseAsset.get("borrowed")
            base_interest = baseAsset.get("interest")
                # ii. 计价资产
            quote_asset = quoteAsset.get("asset")
            quote_free = quoteAsset.get("free")
            quote_locked = quoteAsset.get("locked")
            quote_borrowed = quoteAsset.get("borrowed")
            quote_interest = quoteAsset.get("interest")
            dic = {
                "symbol":symbol, "逐仓_风险率":isoMargin_riskRate, "逐仓_爆仓价格":liquidatePrice, "逐仓_爆仓涨幅(%)":liquidateRate,
                "base_asset":base_asset, "base_free":base_free, "base_locked":base_locked, "base_borrowed":base_borrowed, "base_interest":base_interest,
                "quote_asset":quote_asset, "quote_free":quote_free, "quote_locked":quote_locked, "quote_borrowed":quote_borrowed, "quote_interest":quote_interest,
            }
            isoMargin_balances.append(dic)
        if isoMargin_balances:
            # 生成df (数字数字化)
            df = pd.DataFrame(isoMargin_balances)
            need_to_apply_numeric_columns = [
                "base_free", "base_locked", "base_borrowed", "base_interest",
                "quote_free", "quote_locked", "quote_borrowed", "quote_interest",
            ]
            df[need_to_apply_numeric_columns] = df[need_to_apply_numeric_columns].apply(pd.to_numeric)
            # 获取资产的usdt计价表
            asset_price_df = self.req_asset_price()
            asset_price_df["base_asset"] = asset_price_df["asset"] # (添加两列) 目的:为了方便后面merge
            asset_price_df["quote_asset"] = asset_price_df["asset"] # (添加两列) 目的:为了方便后面merge
            # i. 标的资产
            df["base_asset"] = df["base_asset"]
            df["逐仓标的_总数量"] = df["base_free"] + df["base_locked"]
            df["逐仓标的_总借款量"] = df["base_borrowed"]
            df["逐仓标的_总利息量"] = df["base_interest"]
            df["逐仓标的_净数量"] = df["base_free"] + df["base_locked"] - df["base_borrowed"] - df["base_interest"]
                # 获取标的资产的 '价格&市值'
            df = pd.merge(df, asset_price_df[["base_asset", "price"]], how="left", on="base_asset")
            df = df.rename(columns={"price":"逐仓标的_价格"})
            df["逐仓标的_总市值"] = df["逐仓标的_总数量"] * df["逐仓标的_价格"]
            df["逐仓标的_净市值"] = df["逐仓标的_净数量"] * df["逐仓标的_价格"]
            df["逐仓标的_借款市值"] = df["逐仓标的_总借款量"] * df["逐仓标的_价格"]
            df["逐仓标的_利息市值"] = df["逐仓标的_总利息量"] * df["逐仓标的_价格"]
            # ii. 计价资产
            df["quote_asset"] = df["quote_asset"]
            df["逐仓计价_总数量"] = df["quote_free"] + df["quote_locked"]
            df["逐仓计价_总借款量"] = df["quote_borrowed"]
            df["逐仓计价_总利息量"] = df["quote_interest"]
            df["逐仓计价_净数量"] = df["quote_free"] + df["quote_locked"] - df["quote_borrowed"] - df["quote_interest"]
                # 获取计价资产的 '价格&市值'
            df = pd.merge(df, asset_price_df[["quote_asset", "price"]], how="left", on="quote_asset")
            df = df.rename(columns={"price":"逐仓计价_价格"})
            df["逐仓计价_总市值"] = df["逐仓计价_总数量"] * df["逐仓计价_价格"]
            df["逐仓计价_净市值"] = df["逐仓计价_净数量"] * df["逐仓计价_价格"]
            df["逐仓计价_借款市值"] = df["逐仓计价_总借款量"] * df["逐仓计价_价格"]
            df["逐仓计价_利息市值"] = df["逐仓计价_总利息量"] * df["逐仓计价_价格"]
            # iii. 两个资产汇总
            df["逐仓_总市值"] = df["逐仓标的_总市值"] + df["逐仓计价_总市值"]
            df["逐仓_净市值"] = df["逐仓标的_净市值"] + df["逐仓计价_净市值"]
            df["逐仓_借款市值"] = df["逐仓标的_借款市值"] + df["逐仓计价_借款市值"]
            df["逐仓_利息市值"] = df["逐仓标的_利息市值"] + df["逐仓计价_利息市值"]
            df = df.sort_values("逐仓_净市值", ascending=False)
            df = df.reset_index(drop=True)
        else:
            df = pd.DataFrame()
        return df

    def get_futures_account_df(self, account_type="futures"):
        """
        usage:
            df = ba.get_futures_account_df()
        """
        d = self.req_account(account_type="futures") # u本位合约账户account

    def get_dfutures_account_df(self, account_type="dfutures"):
        """
        usage:
            df = ba.get_dfutures_account_df()
        """
        d = self.req_account(account_type="dfutures") # 币本位合约账户account

    # 3. 历史成交订单
    def req_myTrades(self, account_type="spot", symbol="", start_time=None, end_time=None, pair="", limit=1000, is_obj=False): # 使用币安官网的命名
        """
            functions:
                - 查询某币种的近期最新成交数据 (毫秒级的'逐笔'成交)
            args:
                - symbol: 需要大写  (eg: BNBUSDT)
                                    // 如果是币本位, 则格式为: BTCUSD_200626
                - pair: 币本位专用! (ADAUSDT)
            return:
                - 多笔交易的列表: [{}, {}]
            usage:
                s_d = ba.req_myTrades(account_type="spot", symbol="BTCUSDT", start_time="2021-05-24")
                s_d = ba.req_myTrades(account_type="isoMargin", symbol="MTLUSDT", start_time="2021-06-08 00:00:00", is_obj=True)

                s_d = ba.req_myTrades(account_type="isoMargin", symbol="MANAUSDT", start_time="2021-06-08 00:00:00")
                f_d = ba.req_myTrades(account_type="futures", symbol="MANAUSDT", start_time="2021-06-08 00:00:00")

                f_d = ba.req_myTrades(account_type="futures", symbol="ADAUSDT", start_time="2021-06-08 00:00:00")
        """
        # 0.输入值检验
        if account_type not in ["spot", "fullMargin", "isoMargin", "futures", "dfutures"]:
            raise Exception(f"[输入异常] account_type:{account_type}")
        symbol = symbol.upper()
        if account_type == "futures":
            if "_PERP" in symbol:
                symbol, _ = symbol.split("_")
        # 1. 制造/打包请求数据
        req_method = "get"
        verify = True
        query_dict = {
        }
        if account_type == "spot":
            host = self.spot_host
            path = "/api/v3/myTrades"
            query_dict.update({"limit" : min(1000, limit)})
        elif account_type == "fullMargin":
            host = self.spot_host
            path = "/sapi/v1/margin/myTrades"
            query_dict.update({"limit" : min(1000, limit), "isIsolated":"FALSE"})
        elif account_type == "isoMargin":
            host = self.spot_host
            path = "/sapi/v1/margin/myTrades"
            query_dict.update({"limit" : min(1000, limit), "isIsolated":"TRUE"})
        elif account_type == "futures":
            host = self.futures_host
            path = "/fapi/v1/userTrades"
            query_dict.update({"limit" : min(1000, limit)})
        elif account_type == "dfutures":
            # symbol 或 pair 其中一个必传 // symbol是只具体的合约,如: BTCUSD_200626;  pair是只标的相关合约对,如:BTCUSD
            # symbol 和 pair 不可同时提供
            # fromId 和 pair 不可同时提供
            host = self.dfutures_host
            path = "/dapi/v1/userTrades"
            query_dict.update({"limit" : min(100, limit)})

        if symbol:
            query_dict.update({"symbol" : symbol.upper()})
        if pair: # 币本位专用参数!
            query_dict.update({"pair" : pair.upper()})
        if start_time:
            query_dict.update({"startTime":int(get_timestamp(f"{start_time}").timestamp()*1000)})
        if end_time:
            query_dict.update({"endTime":int(get_timestamp(f"{end_time}").timestamp()*1000)})

        # 2. 发送请求
        resp_obj = self.request(
            req_method = req_method,
            host = host,
            path = path,
            query_dict = query_dict,
            verify = verify,
        )

        # 3. 处理返回数据
            # 检测1. 状态码必须是要 '2' 开头的才是正常的!!
        trades_dict = {}
        if resp_obj.status_code // 100 != 2:
            msg = f"获取数据失败，状态码：{resp_obj.status_code}，信息：{resp_obj.text}"
            print(msg)
            return trades_dict
        else:
            data = resp_obj.json() # type: [[e, e],]
            # 检测2. 返回的数据要非空!
            if not data:
                msg = f"返回数据为空"
                logger.log(20, msg)
                return trades_dict
            else:
                if is_obj:
                    # 直接返回对象, 可以取到resp_obj.headers  (headers里可以看到最近这1分钟内花了多少权重...)
                    return resp_obj
                else:
                    buf = []
                    lst = resp_obj.json()
                    for d in lst:
                        buf.append({
                            "symbol": d.get("symbol"),
                            "orderId" : d.get("orderId"),
                            "side": d.get("side"), # 买卖方向 (只有u本位和币本位才有这个字段)
                            "price" : d.get("price"),
                            "qty" : d.get("qty"), # u本位是币的成交数量;  币本位是合约的成交张数
                            "quoteQty" : d.get("quoteQty"), # 计价资产的数量 (即: usdt的数量)
                            "baseQty" : d.get("baseQty"), # 标的资产的数量 (即: 币的数量)
                            "datetime" : get_timestamp(d.get("time")/1000),
                            "isBuyer": d.get("isBuyer") or d.get("buyer"),
                            "isMaker": d.get("isMaker") or d.get("maker"),
                            "positionSide": d.get("positionSide"),
                            "commission": d.get("commission"),
                            "commissionAsset": d.get("commissionAsset"),
                            "realizedPnl": d.get("realizedPnl"),
                            # "orderListId": d.get("orderListId"),
                        })
                    return buf

    def req_myTrades_df(self, account_type="spot", symbol="", start_time=None, end_time=None, pair="", limit=1000, is_obj=False):
        """
        usage:
            s_df = ba.req_myTrades_df(account_type="spot", symbol="BTCUSDT", start_time="2021-05-24")
            s_df = ba.req_myTrades_df(account_type="isoMargin", symbol="MTLUSDT", start_time="2021-06-08 00:00:00", is_obj=True)
            s_df = ba.req_myTrades_df(account_type="isoMargin", symbol="MTLUSDT", start_time="2021-06-08 00:00:00")
            f_df = ba.req_myTrades_df(account_type="futures", symbol="MTLUSDT", start_time="2021-06-08 00:00:00")

            s_df = ba.req_myTrades_df(account_type="spot", symbol="waxpUSDT", start_time="2021-08-24 13:00:00")

            s_df = ba.req_myTrades_df(account_type="spot", symbol="dogeUSDT", start_time="today")
            f_df = ba.req_myTrades_df(account_type="futures", symbol="ethUSDT", start_time="2021-01-09 20:00:00")

            # 计算价差率
            symbol = "dgbUSDT"
            start_time = "2021-06-22 20:00:00"
            s_df = ba.req_myTrades_df(account_type="spot", symbol=symbol, start_time=start_time)
            # s_df = ba.req_myTrades_df(account_type="isoMargin", symbol=symbol, start_time=start_time)
            # s_df = ba.req_myTrades_df(account_type="fullMargin", symbol=symbol, start_time=start_time)
            s_df["quoteQty"] = s_df["price"] * s_df["qty"]  # 全仓/逐仓杠杆账户的交易记录不会返回'quoteQty'字段, 需要自行计算...
            f_df = ba.req_myTrades_df(account_type="futures", symbol=symbol, start_time=start_time)
            s_avg_price = s_df["quoteQty"].sum() / s_df["qty"].sum()
            f_avg_price = f_df["quoteQty"].sum() / f_df["qty"].sum()
            spread_rate = (s_avg_price - f_avg_price) / f_avg_price
            print(f"价差率:{spread_rate:.3%}")

            s_df = s_df.query("isBuyer!=True")
            f_df = f_df.query("isBuyer==True")

        """
        d = self.req_myTrades(account_type=account_type, symbol=symbol, start_time=start_time, end_time=end_time, pair=pair, limit=limit, is_obj=is_obj)
        if not d:
            msg = f"[没有历史成交数据] d:{d}"
            raise Exception(msg)
        df = pd.DataFrame(d)
        df[["price", "qty", "quoteQty", "commission"]] = df[["price", "qty", "quoteQty", "commission"]].apply(pd.to_numeric)
        return df

    # 4. 订阅ws推送
    # i. 行情-ws
    def subscribe_market_data(self, account_type="spot", channels=["ethusdt@bookTicker"]):
        """
            function: 订阅市场行情数据
            args:
                channels: ["ethusdt@bookTicker", "ethusdt@ticker", "ethusdt@depth5", "ethusdt@depth", "ethusdt@depth@100ms"]
                channels = ["ethusdt@kline_1m"]
            return: ws对象
            notes:
                stream名称中所有交易对,标的交易对,合约类型均为小写
            usage:
                ba.subscribe_market_data()
                ba.subscribe_market_data(account_type="spot", channels=["ethusdt@bookTicker@1s"])
                ba.subscribe_market_data(account_type="futures", channels=["!markPrice@arr@1s"]) # 有些时候1s和1000ms不能互换 (api文档写的也不清晰...)
        """
        if account_type == "spot":
            url = f"wss://stream.binance.com:9443/stream?streams={'/'.join(channels)}"
        elif account_type == "fullMargin":
            url = f"wss://stream.binance.com:9443/stream?streams={'/'.join(channels)}" # "全仓&逐仓"的行情数据和'spot'是一样的
        elif account_type == "isoMargin":
            url = f"wss://stream.binance.com:9443/stream?streams={'/'.join(channels)}" # "全仓&逐仓"的行情数据和'spot'是一样的
        elif account_type == "futures":
            url = f"wss://fstream.binance.com/stream?streams={'/'.join(channels)}"
        elif account_type == "dfutures":
            url = f"wss://dstream.binance.com/stream?streams={'/'.join(channels)}"

        ws = websocket.create_connection( # 该函数比 ws.connect()好用, 返回的也是一个ws对象
            url,
            sslopt={"cert_reqs": ssl.CERT_NONE}, # 我也不知道干啥用的, 不传递也能订阅成功的..
            http_proxy_host=http_proxy_host, # 代理一定要传递, 不然订阅不成功 (一直没搞懂, 为啥要翻墙才行...)
            http_proxy_port=http_proxy_port,
            # header="" # 币安接口不需要传递header
        )
        self.market_ws = ws
        # self.market_ws.recv()
        # self.market_ws.close()
        return ws

    # ii. 账户-ws
        # 获取listen_key
    def req_listen_key(self, account_type="spot"):
        req_method = "post"
            # 请求内容 (参数需要参考官网API)
        query_dict = {
        }
        verify = False # 虽然不需要sign, 但是我的header中已经有api-key了...
        if account_type == "spot":
            host = self.spot_host
            path = "/api/v3/userDataStream"
        elif account_type == "fullMargin":
            host = self.spot_host
            path = "/sapi/v1/userDataStream"
        elif account_type == "isoMargin":
            host = self.spot_host
            path = "/sapi/v1/userDataStream/isolated"
        elif account_type == "futures":
            host = self.futures_host
            path = "/fapi/v1/listenKey"
        elif account_type == "dfutures":
            host = self.dfutures_host
            path = "/dapi/v1/listenKey"
        # 2. 发送请求
        resp_obj = self.request(
            req_method = req_method,
            host = host,
            path = path,
            query_dict = query_dict,
            verify = verify,
        )
            # 检测1. 状态码必须是要 '2' 开头的才是正常的!!
        listenkey_dict = {}
        if resp_obj.status_code // 100 != 2: # eg: startTime填错了, status_code就会变成400.
            msg = f"获取数据失败，状态码：{resp_obj.status_code}，信息：{resp_obj.text}"
            print(msg)
            return listenkey_dict
        else:
            data = resp_obj.json() # type: [[e, e],]
            # 检测2. 返回的数据要非空!
            if not data:
                msg = f"返回数据为空"
                logger.log(20, msg)
                return listenkey_dict
            else:
                listenkey_dict = resp_obj.json()
                logger.log(logging.DEBUG, f'req_listen_key 成功: {listenkey_dict}')
                listen_key = listenkey_dict.get("listenKey")
                if account_type == "spot":
                    self.listen_keys.update({"listen_key_spot":listen_key})
                elif account_type == "fullMargin":
                    self.listen_keys.update({"listen_key_fullMargin":listen_key})
                elif account_type == "isoMargin":
                    self.listen_keys.update({"listen_key_isoMargin":listen_key})
                elif account_type == "futures":
                    self.listen_keys.update({"listen_key_futures":listen_key})
                elif account_type == "dfutures":
                    self.listen_keys.update({"listen_key_dfutures":listen_key})
                return listenkey_dict

        # 延长listen_key的有效性
    def keep_listen_key(self, account_type="spot"):
        req_method = "put"
        if account_type == "spot":
            host = self.spot_host
            path = "/api/v3/userDataStream"
            listen_key = self.listen_keys.get("listen_key_spot")
            if not listen_key:
                self.req_listen_key(account_type=account_type)
            listen_key = self.listen_keys.get("listen_key_spot")
        elif account_type == "fullMargin":
            host = self.spot_host
            path = "/sapi/v1/userDataStream"
            listen_key = self.listen_keys.get("listen_key_fullMargin")
            if not listen_key:
                self.req_listen_key(account_type=account_type)
            listen_key = self.listen_keys.get("listen_key_fullMargin")
        elif account_type == "isoMargin":
            host = self.spot_host
            path = "/sapi/v1/userDataStream/isolated"
            listen_key = self.listen_keys.get("listen_key_isoMargin")
            if not listen_key:
                self.req_listen_key(account_type=account_type)
            listen_key = self.listen_keys.get("listen_key_isoMargin")
        elif account_type == "futures":
            host = self.futures_host
            path = "/fapi/v1/listenKey"
            listen_key = self.listen_keys.get("listen_key_futures")
            if not listen_key:
                self.req_listen_key(account_type=account_type)
            listen_key = self.listen_keys.get("listen_key_futures")
        elif account_type == "dfutures":
            host = self.dfutures_host
            path = "/dapi/v1/listenKey"
            listen_key = self.listen_keys.get("listen_key_dfutures")
            if not listen_key:
                self.req_listen_key(account_type=account_type)
            listen_key = self.listen_keys.get("listen_key_dfutures")
        verify = False # 虽然不需要sign, 但是我的header中已经有api-key了...
            # 请求内容 (参数需要参考官网API)
        query_dict = {
            "listenKey" : listen_key
        }
        # 2. 发送请求
        resp_obj = self.request(
            req_method = req_method,
            host = host,
            path = path,
            query_dict = query_dict,
            verify = verify,
        )
            # 检测1. 状态码必须是要 '2' 开头的才是正常的!!
        listenkey_dict = {}
        if resp_obj.status_code // 100 != 2: # eg: startTime填错了, status_code就会变成400.
            msg = f"获取数据失败，状态码：{resp_obj.status_code}，信息：{resp_obj.text}"
            print(msg)
            return listenkey_dict
        else:
            data = resp_obj.json() # type: [[e, e],]
            # 检测2. 返回的数据要非空!
            if not data:
                msg = f"返回数据为空"
                logger.log(20, msg)
                return listenkey_dict
            else:
                listenkey_dict = resp_obj.json()
                logger.log(logging.DEBUG, f'req_listen_key 成功: {listenkey_dict}')
                # self.listen_key = listenkey_dict.get("listenKey")
                return listenkey_dict

        # 订阅ws
    def subscribe_trade_data(self, account_type="spot"):
        """
            function: 订阅账户交易数据 (资产变动等)
            return: ws对象
            notes:
                - 接口的数据结构:
                    ACCOUNT_UPDATE 事件:
                        {'e': 'ACCOUNT_UPDATE',
                         'T': 1617203864641,
                         'E': 1617203864645,
                         'a': {
                            'B': [
                                {'a': 'USDT', 'wb': '9199.78470835', 'cw': '9199.78470835'}, # cw: 除去逐仓仓位保证金的钱包余额(没懂啥意思..)
                                {'a': 'BNB', 'wb': '0.50072039', 'cw': '0'}
                            ],
                            'P': [
                                {
                                    's': 'COTIUSDT', # 为啥有两个一样symbol的数据, 第一个还是空的....? 一直没搞懂...
                                    'pa': '0',
                                    'ep': '0.00000',
                                    'cr': '0',
                                    'up': '0',
                                    'mt': 'cross',
                                    'iw': '0',
                                    'ps': 'BOTH',  # 是因为持仓方向和下面的不一样吗...?
                                    'ma': 'USDT'
                                },
                               {
                                    's': 'COTIUSDT', # 交易对
                                    'pa': '10',      # 仓位 (即: 仓位变动后, 当前最新的持仓情况)
                                    'ep': '0.46664', # 开仓价格 (即:成本价)
                                    'cr': '-0.21715999', # 累计实现损益 **(貌似是该币种从开户到现在的所有收益的汇总)
                                    'up': '-0.00962280', # 持仓未实现盈亏 (即: 仓位变动后, 当前最新仓位的浮盈)
                                    'mt': 'cross',
                                    'iw': '0',
                                    'ps': 'LONG',
                                    'ma': 'USDT'
                                }
                            ],
                            'm': 'ORDER'
                            }
                        }

                    ORDER_TRADE_UPDATE 事件: # 该事件会更新'订单状态'
                        {'e': 'ORDER_TRADE_UPDATE',
                         'T': 1617203864641,
                         'E': 1617203864645,
                         'o': {
                          's': 'COTIUSDT',
                          'c': 'ios_sNwlLlQg34KMKan0BRGs', # 客户自定义的orderId
                          'S': 'SELL',
                          'o': 'MARKET',
                          'f': 'GTC', # 有效方式
                          'q': '2',  # 数量
                          'p': '0',  # 订单原始价格  (为啥是0????) (市价单的原始价格都为0, 限价单则为限价)
                          'ap': '0.46539', # 订单平均价格
                          'sp': '0', # 条件订单触发价格，对追踪止损单无效 (即: 触发价格)
                          'x': 'TRADE', # 本次事件的具体执行类型
                          'X': 'FILLED', # 订单的当前状态; FILLED表示完全成交
                          'i': 101034613, # 订单id (币安服务器发配的)
                          'l': '2', # 订单末次成交量
                          'z': '2', # 订单累计已成交量
                          'L': '0.46539', # 订单末次成交价格
                          'n': '0.00000108', # 手续费数量
                          'N': 'BNB',  # 手续费资产类型
                          'T': 1617203864641,
                          't': 4136785,
                          'b': '0',
                          'a': '0',
                          'm': False, # 是否为挂单
                          'R': True, # 是否是只减仓单
                          'wt': 'CONTRACT_PRICE', # 触发价类型
                          'ot': 'MARKET',
                          'ps': 'LONG',
                          'cp': False, # 是否为触发平仓单; 仅在条件订单情况下会推送此字段
                          'rp': '-0.00250000', # 该笔交易实现的盈亏
                          'pP': False,  # 官网文档没有该字段
                          'si': 0,      # 官网文档没有该字段
                          'ss': 0}     # 官网文档没有该字段
                         }
        usage:
            bra_spot.subscribe_trade_data()

        """
        if account_type == "spot":
            host = f"wss://stream.binance.com:9443/stream?streams="
            listen_key = self.listen_keys.get("listen_key_spot")
            if not listen_key:
                self.req_listen_key(account_type=account_type)
            listen_key = self.listen_keys.get("listen_key_spot")
        elif account_type == "fullMargin":
            host = f"wss://stream.binance.com:9443/stream?streams="
            listen_key = self.listen_keys.get("listen_key_fullMargin")
            if not listen_key:
                self.req_listen_key(account_type=account_type)
            listen_key = self.listen_keys.get("listen_key_fullMargin")
        elif account_type == "isoMargin":
            host = f"wss://stream.binance.com:9443/stream?streams="
            listen_key = self.listen_keys.get("listen_key_isoMargin")
            if not listen_key:
                self.req_listen_key(account_type=account_type)
            listen_key = self.listen_keys.get("listen_key_isoMargin")
        elif self.api_type == "futures":
            host = f"wss://fstream.binance.com/stream"
            listen_key = self.listen_keys.get("listen_key_futures")
            if not listen_key:
                self.req_listen_key(account_type=account_type)
            listen_key = self.listen_keys.get("listen_key_futures")
        elif self.api_type == "dfutures":
            host = f"wss://dstream.binance.com/stream"
            listen_key = self.listen_keys.get("listen_key_dfutures")
            if not listen_key:
                self.req_listen_key(account_type=account_type)
            listen_key = self.listen_keys.get("listen_key_dfutures")

        listen_key_lst = []
        for name, listen_key in self.listen_keys.items():
            if listen_key:
                listen_key_lst.append(str(listen_key))
        path = "/".join(listen_key_lst)

        url = f"{host}{path}"
            # 可以同时在一个ws中订阅'现货'和'杠杆'的ws
        # url = f"wss://stream.binance.com:9443/stream?streams=hjiS18GGY5PXQ46niTsLs76Mx9tvuRydvODCNTFHh1XwzC4ISgw0rlLBdcaA/QCRuQqX8Z63ULcpDTdM33vlSbM6eorrWUFLYy15Ls5CdAVkq9d5QR2czfNQM"

        ws = websocket.create_connection( # 该函数比 ws.connect()好用, 返回的也是一个ws对象
            url,
            sslopt={"cert_reqs": ssl.CERT_NONE}, # 我也不知道干啥用的, 不传递也能订阅成功的..
            http_proxy_host=http_proxy_host, # 代理一定要传递, 不然订阅不成功 (一直没搞懂, 没啥要翻墙才行...)
            http_proxy_port=http_proxy_port,
            # header="" # 币安接口不需要传递header
        )
        self.trade_ws = ws
        # self.trade_ws.recv()
        # self.trade_ws.close()
        return ws

    # iii. 溢价指数-ws
    def subscribe_premium_index(self, account_type="futures", symbols=["ETHUSDT", "BTCUSDT"]):
        """
            function: 订阅市场行情数据
            args:
                channels: ["ethusdt@bookTicker", "ethusdt@ticker", "ethusdt@depth5", "ethusdt@depth", "ethusdt@depth@100ms"]
                channels = ["ethusdt@kline_1m"]
            notes:
                - 目前只支持'u本位的溢价指数'
            return: ws对象
        """
        # url = f"wss://fstream.yshyqxx.com/stream?streams=p1000SHIBUSDT@kline_1m"
        channels = [f"p{symbol.upper()}@kline_1m" for symbol in symbols]
        url = f"wss://fstream.yshyqxx.com/stream?streams={'/'.join(channels)}"

        ws = websocket.create_connection( # 该函数比 ws.connect()好用, 返回的也是一个ws对象
            url,
            sslopt={"cert_reqs": ssl.CERT_NONE}, # 我也不知道干啥用的, 不传递也能订阅成功的..
            http_proxy_host=http_proxy_host, # 代理一定要传递, 不然订阅不成功 (一直没搞懂, 没啥要翻墙才行...)
            http_proxy_port=http_proxy_port,
            # header="" # 币安接口不需要传递header
        )
        self.premiumIndex_ws = ws
        # self.market_ws.recv()
        # self.market_ws.close()
        return ws


    # 三. 行情-数据请求接口 (market)
    # ====================================================================
    # 1. 获取最新价格
        # i. 现货价格
    def req_spot_price(self, account_type="spot"):
        """
            function: "获取所有现货币种的最新价格"
            notes:
                - 返回结果中没有asset字段, 但是现货的币对的计价资产有很多, 需要自行挑出asset字段
            return:
                4列: symbol, price, base_asset, quote_asset  (**会存在"DAIUSDT"这样的币对)
            usage:
                df = bra_spot.req_spot_price()
        """
            # 1. '现货'的最新价格
        spot_url = "https://api.binance.com/api/v3/ticker/price"
        spot_last_price_lst = req(spot_url, is_obj=True).json()
        spot_last_price_dict = {d.get("symbol"):d.get("price") for d in spot_last_price_lst}
        spot_last_price_df = pd.DataFrame(spot_last_price_lst)
        spot_last_price_df["price"] = spot_last_price_df["price"].apply(pd.to_numeric)
            # 筛选出asset字段
        def foo(row):
            symbol = row.get("symbol")
            for quote_assetName in QUOTE_ASSETS:
                if quote_assetName in symbol[1:]:
                    # print(symbol, quote_assetName)
                    # base_asset, quote_asset = symbol.split(quote_assetName)
                    base_asset = symbol[:-len(quote_assetName)]
                    quote_asset = symbol[-len(quote_assetName):]
                    row["base_asset"] = base_asset
                    row["quote_asset"] = quote_asset
                    return row
        # spot_last_price_df[["base_asset", "quote_asset"]] = spot_last_price_df["symbol"].apply(foo, axis=1)
        df = spot_last_price_df.apply(foo, axis=1)
        df = df.query("symbol.notnull()")
        df = df.reset_index(drop=True)

        # 把这个特殊的币也算上!   (那其他的稳定币要算吗?) // 不用, 其他稳定币都会有固定的usdt币对 (即: 存在'BUSDUSDT'的币对)
        df = df.append({"symbol":"USDTUSDT", "price":1, "base_asset":"USDT", "quote_asset":"USDT"}, ignore_index=True)
        return df

        # ii. 获取资产的usdt计价表
    def req_asset_price(self, account_type="spot"):
        """
        function:
            - 获取资产的现货价格!!  (默认以USDT为计价方式!!)
        return:
            2列: asset, price
        usage:
            df = bra_spot.req_asset_price()
        """
        spot_price_df = self.req_spot_price()
        asset_price_df = spot_price_df.query("quote_asset == 'USDT'")
        asset_price_df = asset_price_df[["base_asset", "price"]]
        asset_price_df = asset_price_df.rename(columns={"base_asset":"asset"})
        asset_price_df = asset_price_df.sort_values("price", ascending=False)
        asset_price_df = asset_price_df.reset_index(drop=True)
        return asset_price_df

        # iii. 获取所有u本位币种的最新价格&费率
    def req_futures_price(self, account_type="futures"):
        """
            function: "获取所有u本位币种的最新价格&费率"
            notes:
            usage:
                df = bra_futures.req_futures_price()
        """
            # 2. 'U本位合约'的最新价格
        futures_url = "https://fapi.binance.com/fapi/v1/premiumIndex" # 标记价格&资金费率
        futures_last_price_lst = req(futures_url, is_obj=True).json()
        futures_last_price_dict = {d.get("symbol"):d.get("markPrice") for d in futures_last_price_lst}
        futures_last_price_df = pd.DataFrame(futures_last_price_lst)
        futures_last_price_df = futures_last_price_df[["symbol", "markPrice", "lastFundingRate"]]
        futures_last_price_df = futures_last_price_df.rename(columns={"markPrice":"price", "lastFundingRate":"funding_rate"})
        futures_last_price_df[["price", "funding_rate"]] = futures_last_price_df[["price", "funding_rate"]].apply(pd.to_numeric)
            # 筛选出asset字段
        def foo(x):
            if "_" in x:
                _symbol = x.split("_")[0]
            else:
                _symbol = x
            assetName = _symbol[:-4]
            return assetName
        futures_last_price_df["asset"] = futures_last_price_df["symbol"].apply(foo)
        return futures_last_price_df

        # iv. 获取所有币本位币种的最新价格&费率
    def req_dfutures_price(self, account_type="dfutures"):
        """
            function: "获取所有币本位币种的最新价格&费率"
            notes:
            usage:
                df = bra_dfutures.req_dfutures_price()
        """
            # 3. '币本位合约'的最新价格
        dfutures_url = "https://dapi.binance.com/dapi/v1/premiumIndex" # 标记价格&资金费率
        dfutures_last_price_lst = req(dfutures_url, is_obj=True).json()
        dfutures_last_price_dict = {d.get("symbol"):d.get("markPrice") for d in dfutures_last_price_lst}
        dfutures_last_price_df = pd.DataFrame(dfutures_last_price_lst)
        dfutures_last_price_df = dfutures_last_price_df[["symbol", "markPrice", "lastFundingRate"]]
        dfutures_last_price_df = dfutures_last_price_df.rename(columns={"markPrice":"price", "lastFundingRate":"funding_rate"})
        dfutures_last_price_df[["price", "funding_rate"]] = dfutures_last_price_df[["price", "funding_rate"]].apply(pd.to_numeric)
            # 筛选出asset字段
        def foo(x):
            if "_" in x:
                _symbol = x.split("_")[0]
            else:
                _symbol = x
            assetName = _symbol[:-3]
            return assetName
        dfutures_last_price_df["asset"] = dfutures_last_price_df["symbol"].apply(foo)
        return dfutures_last_price_df

    # 2. 获取历史k线 (最细是1分钟)
    def req_klines(self, account_type="spot", binance_symbol="BTCUSDT", interval="1m", start_time=None, end_time=None): # 使用币安官网的命名
        """
            functions:
                - 查询某币种的历史k线 (最细是1分钟级别的)
            args:
                - binance_symbol: 需要大写  (eg: BNBUSDT)
                - interval: '1m', '3m', '5m', '15m', '30m', '1h', '4h', '8h', '1d', '3d', '1w', '1M'
                    - 若是聚合分钟线, 这个分钟数需要能把60整除. (15m可以, 16m就不行)
                    - 若是聚合小时线, 随便几小时都可以
                - start_time: 开始时间 (以'ms'为单位的时间戳)
                - end_time: 截止时间 (以'ms'为单位的时间戳)
                    (开始时间和截止时间都可以没有)
                        如果有开始时间: 在开始时间后取1000条数据
                        如果有截止时间: 在截止时间前取1000条数据
            return:
                - 多个bar的列表: [BinanceBarData(), BinanceBarData()]
        """
        # 1. 制造/打包请求数据
        req_method = "get"
        if (account_type == "spot") or (account_type == "fullMargin") or (account_type == "isoMargin"):
            host = self.spot_host
            path = "/api/v3/klines"
        elif account_type == "futures":
            host = self.futures_host
            path = "/fapi/v1/klines"
        elif account_type == "dfutures":
            host = self.dfutures_host
            path = "/dapi/v1/klines"
        verify = False
            # 币安接口中的startTime必须是 'ms'为单位的int型 (eg: 1234567890123)
        # start_time = start_time if start_time else int(get_timestamp("today").timestamp()*1000)  # 如果没有传入start_time, 则用今天0点的时间戳传入
        query_dict = {
            "symbol" : binance_symbol.upper(),  # binance_symbol需要大写
            "interval" : interval,
            "limit" : 1000,  # 币安接口最大支持1000
        }
        if start_time:
            query_dict.update({"startTime":start_time})
        if end_time:
            query_dict.update({"endTime":end_time})

        # 2. 发送request, 检验response
        resp_obj = self.request(
            req_method = req_method,
            host = host,
            path = path,
            query_dict = query_dict,
            verify = verify,
        )
            # 检测1. 状态码必须是要 '2' 开头的才是正常的!!
        history_bar_data = []
        if resp_obj.status_code // 100 != 2: # eg: startTime填错了, status_code就会变成400.
            msg = f"获取数据失败，状态码：{resp_obj.status_code}，信息：{resp_obj.text}"
            print(msg)
            return history_bar_data
        else:
            data = resp_obj.json() # type: [[e, e],]
            # 检测2. 返回的数据要非空!
            if not data:
                msg = f"获取历史数据为空，开始时间：{start_time}"
                print(msg)
                return history_bar_data

        # 3. 处理返回数据 (前提: 通过上面的检测, 这里的数据假设已经正常)
        for l in data:
            bar = BinanceBarData(
                gateway_name = "kerwin_self",
                exchange = Exchange.BINANCE,
                symbol = binance_symbol.upper(),
                interval = Interval.MINUTE,
                datetime = get_timestamp(l[0]/1000), # 用这分钟的开盘时间作为这个bar的时间
                open_price = round(float(l[1]), 4), # 精度可以调整 (这里默认保留4位小数)
                high_price = round(float(l[2]), 4),
                low_price = round(float(l[3]), 4),
                close_price = round(float(l[4]), 4),
                volume = round(float(l[5]), 4), # 总交易额

                # 原生BarData对象中没有的部分
                trans_num = round(float(l[8]), 0), # 总成交笔数
                buy_volume = round(float(l[9]), 4), # 主动买入交易量
                buy_turnover = round(float(l[10]), 4), # 主动买入交易额
            )
            history_bar_data.append(bar)
        return history_bar_data # 所有历史bar数据

    # 3. 价格指数的k线数据
    def req_indexPriceKlines(self, account_type="futures", pair="", interval="1m", limit=1000, start_time=None, end_time=None, is_obj=False):
        """
            function: 价格指数K线数据
            args:
                - pair: # "DOGEUSDT"

            usage:
                # 下午4点45分服务器维护结束
                start_time = int(get_timestamp("2021-04-25 16:45:00").timestamp()*1000)
                end_time = int(get_timestamp("2021-04-25 16:45:10").timestamp()*1000)
                d = bra_spot.req_aggTrades(symbol="LUNAUSDT", start_time=start_time, end_time=end_time)
                df = pd.DataFrame(d)
                df["T"] = pd.to_datetime(df['T'], unit="ms").dt.tz_localize('UTC').dt.tz_convert('hongkong') # 转化成东八区的时间


        """
        req_method = "get"
        if account_type == "futures":
            host = self.futures_host
            path = "/fapi/v1/indexPriceKlines"
        verify = False
        query_dict = {
            "pair" : pair,
            "interval" : interval,
            "limit" : limit,
        }
        if start_time:
            query_dict.update({"startTime":start_time})
        if end_time:
            query_dict.update({"endTime":end_time})
        # 2. 发送请求
        resp_obj = self.request(
            req_method = req_method,
            host = host,
            path = path,
            query_dict = query_dict,
            verify = verify,
        )
        if is_obj:
            return resp_obj
            # 检测1. 状态码必须是要 '2' 开头的才是正常的!!
        response_dict = {}
        if resp_obj.status_code // 100 != 2: # eg: startTime填错了, status_code就会变成400.
            msg = f"获取数据失败，状态码：{resp_obj.status_code}，信息：{resp_obj.text}"
            print(msg)
            return response_dict
        else:
            data = resp_obj.json() # type: [[e, e],]
            # 检测2. 返回的数据要非空!
            if not data:
                msg = f"返回数据为空"
                logger.log(20, msg)
                # True:双向持仓, False:单向持仓
                return response_dict
            else:
                response_dict = resp_obj.json()
                logger.log(logging.DEBUG, f'请求成功: {response_dict}')
                return response_dict

    # 4. 获取交易规则和交易对信息
    def req_exchange_info(self, account_type="spot"):
        """
            functions:
                - 查询'获取交易规则和交易对信息'
            args:
            return:
                - 所有币种的交易规则: {}
        """
        # 1. 制造/打包请求数据
        req_method = "get"
        if (account_type == "spot") or (account_type == "fullMargin") or (account_type == "isoMargin"):
            host = self.spot_host
            path = "/api/v3/exchangeInfo"
        elif account_type == "futures":
            host = self.futures_host
            path = "/fapi/v1/exchangeInfo"
        elif account_type == "dfutures":
            host = self.dfutures_host
            path = "/dapi/v1/exchangeInfo"
        verify = False
            # 请求内容 (参数需要参考官网API)
        query_dict = {
        }

        # 2. 发送请求
        resp_obj = self.request(
            req_method = req_method,
            host = host,
            path = path,
            query_dict = query_dict,
            verify = verify,
        )
            # 检测1. 状态码必须是要 '2' 开头的才是正常的!!
        contract_dict = {}
        if resp_obj.status_code // 100 != 2:
            msg = f"获取数据失败，状态码：{resp_obj.status_code}，信息：{resp_obj.text}"
            print(msg)
            return contract_dict
        else:
            data = resp_obj.json() # type: [[e, e],]
            # 检测2. 返回的数据要非空!
            if not data:
                msg = f"返回数据为空"
                logger.log(20, msg)
                return contract_dict
            else:
                contract_dict = resp_obj.json()
                logger.log(logging.DEBUG, '获取contract成功')
                return contract_dict

    # 5. 查询历史逐笔成交!!! (看秒级别价格变化) (看插针情况)
    def req_aggTrades(self, account_type="spot", symbol="", fromId=None, limit=1000, start_time=None, end_time=None, is_obj=False):
        """
            # 查询历史逐笔成交!!! (看秒级别价格变化) (看插针情况)
            function: 近期成交(归集)
            notes:
                - 归集交易与逐笔交易的区别在于，同一价格、同一方向、同一时间的trade会被聚合为一条
                - 如果发送startTime和endTime，间隔必须小于一小时。
                - 如果没有发送任何筛选参数(fromId, startTime,endTime)，默认返回最近的成交记录
                [注意]: 该函数如果传入了 'start_time', 就必须同时传入 'end_time'

            args:
                fromId: 从哪一条成交id开始返回. 缺省返回最近的成交记录。

            usage:
                # 下午4点45分服务器维护结束
                start_time = int(get_timestamp("2021-04-25 16:45:00").timestamp()*1000)
                end_time = int(get_timestamp("2021-04-25 16:45:10").timestamp()*1000)
                d = bra_spot.req_aggTrades(symbol="LUNAUSDT", start_time=start_time, end_time=end_time)
                df = pd.DataFrame(d)
                df["T"] = pd.to_datetime(df['T'], unit="ms").dt.tz_localize('UTC').dt.tz_convert('hongkong') # 转化成东八区的时间

                # 打新
                r = ba.req_aggTrades(account_type="spot", symbol="WAXPUSDT", start_time="2021-08-23 14:30:00", end_time="2021-08-23 14:30:01")
                df = pd.DataFrame(r)
                df["T"] = pd.to_datetime(df['T'], unit="ms").dt.tz_localize('UTC').dt.tz_convert('hongkong') # 转化成东八区的时间
                output_data(df)

        """
        req_method = "get"
        if (account_type == "spot") or (account_type == "fullMargin") or (account_type == "isoMargin"):
            host = self.spot_host
            path = "/api/v3/aggTrades"
        elif account_type == "futures":
            host = self.futures_host
            path = "/fapi/v1/aggTrades"
        elif account_type == "dfutures":
            host = self.dfutures_host
            path = "/dapi/v1/aggTrades"
        verify = False
        query_dict = {
            "symbol" : symbol,
            "limit" : limit,
        }
        if fromId:
            query_dict.update({"fromId":fromId})
        if start_time:
            query_dict.update({"startTime":int(get_timestamp(f"{start_time}").timestamp()*1000)})
        if end_time:
            query_dict.update({"endTime":int(get_timestamp(f"{end_time}").timestamp()*1000)})
        # 2. 发送请求
        resp_obj = self.request(
            req_method = req_method,
            host = host,
            path = path,
            query_dict = query_dict,
            verify = verify,
        )
        if is_obj:
            return resp_obj
            # 检测1. 状态码必须是要 '2' 开头的才是正常的!!
        response_dict = {}
        if resp_obj.status_code // 100 != 2: # eg: startTime填错了, status_code就会变成400.
            msg = f"获取数据失败，状态码：{resp_obj.status_code}，信息：{resp_obj.text}"
            print(msg)
            return response_dict
        else:
            data = resp_obj.json() # type: [[e, e],]
            # 检测2. 返回的数据要非空!
            if not data:
                msg = f"返回数据为空"
                logger.log(20, msg)
                # True:双向持仓, False:单向持仓
                return response_dict
            else:
                response_dict = resp_obj.json()
                logger.log(logging.DEBUG, f'请求成功: {response_dict}')
                return response_dict

    # 6. 获取杠杆借贷利息 (筛选出'负费率套利'时, 日化收益最高的币种)
        # i. '全仓杠杆'的利率表
    def req_fullMargin_interestRate(self, account_type="fullMargin"):
        """
            notes:
                - 网页版爬取'全仓杠杆'的不同vip等级的所有"币对pair"的利息
            notice:
                - [注意]:
                    测试发现, 全仓和逐仓的借贷利率是一样的, 但是最大借款额度是不一样的
                            (有些是全仓额度高, 有些是逐仓额度高, 主要还看币安的库存情况...)
        """
        # url = "https://www.binancezh.co/bapi/margin/v1/friendly/margin/vip/spec/list-all" # 域名后缀1
        url = "https://www.binancezh.sh/bapi/margin/v1/friendly/margin/vip/spec/list-all" # 域名后缀2
        response_text = req(url)
        response_dict = json.loads(response_text)
        data = response_dict.get("data", {})
        new_d_lst = []
        for d in data:
            base_assetName = d.get("assetName")
            base_interest_lst = d.get("specs")
            if base_interest_lst:
                base_interest_dic = base_interest_lst[0]
                base_maxBorrowable = base_interest_dic.get("borrowLimit")
                base_daily_interestRate = base_interest_dic.get("dailyInterestRate")
            else:
                base_maxBorrowable = None
                base_daily_interestRate = None
            new_d = {
                "base_assetName":base_assetName, "base_daily_interestRate":base_daily_interestRate, "base_maxBorrowable":base_maxBorrowable,
            }
            new_d_lst.append(new_d)
        fullMargin_interestRate_df = pd.DataFrame(new_d_lst) # 逐仓的借贷利息表
        fullMargin_interestRate_df[["base_daily_interestRate", "base_maxBorrowable"]] = fullMargin_interestRate_df[["base_daily_interestRate", "base_maxBorrowable"]].apply(pd.to_numeric)
        fullMargin_interestRate_df = fullMargin_interestRate_df.sort_values("base_daily_interestRate")
        fullMargin_interestRate_df = fullMargin_interestRate_df.reset_index(drop=True)
        return fullMargin_interestRate_df

        # ii. '逐仓杠杆'的利率表
    def req_isoMargin_interestRate(self, account_type="isoMargin"):
        """
            notes:
                - 网页版爬取'逐仓杠杆'的不同vip等级的所有"币对pair"的利息
                    (有个问题: 这个域名经常被ban, 导致请求数据失败!!)
                        [这个接口不能与其他核心接口耦合!!]
            usage:
                df1 = bra_spot.req_isoMargin_interestRate()
        """
        # url = "https://www.binancezh.co/bapi/margin/v1/friendly/isolated-margin/pair/vip-level" # 域名后缀1
        url = "https://www.binancezh.sh/bapi/margin/v1/friendly/isolated-margin/pair/vip-level" # 域名后缀1
        response_text = req(url)
        response_dict = json.loads(response_text)
        data = response_dict.get("data", {})
        new_d_lst = []
        for d in data:
            base_d = d.get("base")
            # i. 标的资产
            base_assetName = base_d.get("assetName")
            base_interest_lst = base_d.get("levelDetails")
            if base_interest_lst:
                base_interest_dic = base_interest_lst[0] # 第0个元素是指vip0的利率
                base_daily_interestRate = base_interest_dic.get("interestRate")
                base_maxBorrowable = base_interest_dic.get("maxBorrowable")
            else:
                base_daily_interestRate = None
                base_maxBorrowable = None
            # ii. 计价资产
            quote_d = d.get("quote")
            quote_assetName = quote_d.get("assetName")
            quote_interest_lst = quote_d.get("levelDetails")
            if quote_interest_lst:
                quote_interest_dic = quote_interest_lst[0] # 第0个元素是指vip0的利率
                quote_daily_interestRate = quote_interest_dic.get("interestRate")
                quote_maxBorrowable = quote_interest_dic.get("maxBorrowable")
            else:
                quote_daily_interestRate = None
                quote_maxBorrowable = None
            symbol = f"{base_assetName}{quote_assetName}"
            new_d = {
                "symbol":symbol, "base_assetName":base_assetName, "quote_assetName":quote_assetName,
                "base_daily_interestRate":base_daily_interestRate, "base_maxBorrowable":base_maxBorrowable,
                "quote_daily_interestRate":quote_daily_interestRate, "quote_maxBorrowable":quote_maxBorrowable,
            }
            new_d_lst.append(new_d)
        isoMargin_interestRate_df = pd.DataFrame(new_d_lst) # 逐仓的借贷利息表
        isoMargin_interestRate_df[["base_daily_interestRate", "base_maxBorrowable"]] = isoMargin_interestRate_df[["base_daily_interestRate", "base_maxBorrowable"]].apply(pd.to_numeric)
        isoMargin_interestRate_df = isoMargin_interestRate_df.sort_values("base_daily_interestRate")
        isoMargin_interestRate_df = isoMargin_interestRate_df.reset_index(drop=True)
        return isoMargin_interestRate_df

        # iii. '全仓杠杆'日收益排序表
    def get_maxProfit_fullMargin_df(self, account_type="fullMargin"):
        """
        function:
            - 得到一个: 除去借贷利息后的套利'日收益'df表 (降序排列) [全仓]
                (方便得知: 如果是负费率的话, 用哪个币的现货做空比较划算..)
        notes:
            - 不管是bra_spot还是bra_futures都可以访问该接口
        """
        df1 = self.req_futures_price() # u本位合约的'价格&费率'表
        df2 = self.req_fullMargin_interestRate() # 全仓杠杆的'利率表'
        df2 = df2.rename(
            columns={"base_assetName":"asset", "base_daily_interestRate":"daily_interestRate", "base_maxBorrowable":"maxBorrowable"
            }) # 这里只考虑base_asset, 改名是为了和下面的df1merge
        df = pd.merge(df1, df2, how="left", on="asset")
        df["daily_profit"] = abs(df["funding_rate"])*3 - df["daily_interestRate"]
        df["maxBorrowable_marketValue"] = df["price"] * df["maxBorrowable"]
        df = df.sort_values("daily_profit", ascending=False)
        df = df.reset_index(drop=True)
        return df

        # iv. '逐仓杠杆'日收益排序表
    def get_maxProfit_isoMargin_df(self, account_type="isoMargin"):
        """
        function:
            - 得到一个: 除去借贷利息后的套利'日收益'df表 (降序排列) [逐仓]
                (方便得知: 如果是负费率的话, 用哪个币的现货做空比较划算..)
        notes:
            - 不管是bra_spot还是bra_futures都可以访问该接口
        """
        df1 = self.req_futures_price() # u本位合约的'价格&费率'表
        df2 = self.req_isoMargin_interestRate() # 逐仓杠杆的'利率表'
        df2 = df2[["base_assetName", "base_daily_interestRate", "base_maxBorrowable"]]
        df2 = df2.drop_duplicates("base_assetName") # 因为逐仓中, 同一个base_asset可以有多个quote_asset, 这里不考虑quote_asset
        df2 = df2.rename(
            columns={"base_assetName":"asset", "base_daily_interestRate":"daily_interestRate", "base_maxBorrowable":"maxBorrowable"
            }) # 这里只考虑base_asset, 改名是为了和下面的df1merge
        df = pd.merge(df1, df2, how="left", on="asset")
        df["daily_profit"] = abs(df["funding_rate"])*3 - df["daily_interestRate"]
        df["maxBorrowable_marketValue"] = df["price"] * df["maxBorrowable"]
        df = df.sort_values("daily_profit", ascending=False)
        df = df.reset_index(drop=True)
        return df

        # v. '全仓&逐仓杠杆'日收益排序表 [其实只要调用这个函数就可以了!!] [负费率套利时, 很重要的"利率, 最大借款额"等借贷数据]
    def get_maxProfit_df(self, account_type="fullMargin", sort_type="逐仓_日收益"):
        """
        function:
            - 得到一个: 除去借贷利息后的u本位套利'日收益'df表 (降序排列) [全仓+逐仓]
                (方便得知: 如果是负费率的话, 用哪个币的现货做空比较划算..)
        notes:
            - 不管是bra_spot还是bra_futures都可以访问该接口
        usage:
            df = ba.get_maxProfit_df()
            df[:30]
        """
        df1 = self.req_futures_price() # u本位合约的'价格&费率'表
        df2 = self.req_fullMargin_interestRate() # 全仓杠杆的'利率表'
        df2 = df2.rename(
            columns={"base_assetName":"asset", "base_daily_interestRate":"full_daily_interestRate", "base_maxBorrowable":"full_maxBorrowable"
            }) # 这里只考虑base_asset, 改名是为了和下面的df1merge
        df3 = self.req_isoMargin_interestRate() # 逐仓杠杆的'利率表'
        df3 = df3.drop_duplicates("base_assetName") # 因为逐仓中, 同一个base_asset可以有多个quote_asset, 这里不考虑quote_asset
        df3 = df3[["base_assetName", "base_daily_interestRate", "base_maxBorrowable"]]
        df3 = df3.rename(
            columns={"base_assetName":"asset", "base_daily_interestRate":"iso_daily_interestRate", "base_maxBorrowable":"iso_maxBorrowable"
            }) # 这里只考虑base_asset, 改名是为了和下面的df1merge
        df = pd.merge(df1, df2, how="left", on="asset")
        df = pd.merge(df, df3, how="left", on="asset")
        df["全仓_日收益"] = abs(df["funding_rate"])*3 - df["full_daily_interestRate"]
        df["全仓_最大借款市值"] = df["price"] * df["full_maxBorrowable"]
        df["逐仓_日收益"] = abs(df["funding_rate"])*3 - df["iso_daily_interestRate"]
        df["逐仓_最大借款市值"] = df["price"] * df["iso_maxBorrowable"]
        # df = df.sort_values("全仓_日收益", ascending=False)
        # df = df.sort_values("逐仓_日收益", ascending=False)
        df = df.sort_values(sort_type, ascending=False)
        df = df.reset_index(drop=True)
        return df

        # vi. 获取最近3天所有币种的平均资金费率 (升序排列) [费率参考依据]
    def get_avg_fundingRate(self, account_type="futures", binance_symbol="", limit=1000):
        """
        notes:获取最近3天所有币种的平均资金费率 (升序排列)
        args:
            - binance_symbol: 当传入单个symbol参数时, 只返回该symbol的历史资金费率
        usage:
            df = ba.get_avg_fundingRate(account_type="futures", binance_symbol="", limit=1000) # 全币种
            df = ba.get_avg_fundingRate(account_type="futures", binance_symbol="kncUSDT", limit=30) # 单币种,近30次
            df = ba.get_avg_fundingRate(account_type="futures", binance_symbol="kavaUSDT", limit=30) # 单币种,近30次
            df = ba.get_avg_fundingRate(account_type="futures", binance_symbol="grtUSDT", limit=30) # 单币种,近30次
            df = ba.get_avg_fundingRate(account_type="futures", binance_symbol="1inchUSDT", limit=100) # 单币种,近30次
        """
        l = self.req_hist_funding_rate(account_type=account_type, binance_symbol=binance_symbol, limit=limit) # 所有币种
        df = pd.DataFrame(l)
        df["fundingRate"] = df["fundingRate"].apply(pd.to_numeric)
        df = df.pivot_table(index="symbol", aggfunc={"fundingRate":"mean", "fundingTime":"count"})
        df = df.rename(columns={"fundingRate":"avg_fundingRate", "fundingTime":"calCount"})
        df = df.sort_values("avg_fundingRate")
        df = df.reset_index()
        maxProfit_df = self.get_maxProfit_df()
        df = pd.merge(df, maxProfit_df, how="left", on="symbol")
        return df


    # 四. 账户&交易-数据请求接口 (account&trade)
    # ====================================================================
    # 1. 查询所有订单 (有效/无效都有)
    def req_allOrders(self, account_type="spot", binance_symbol="", orderId=None, limit=1000, start_time=None, end_time=None, is_obj=False):
        """
            function: 查询所有订单 获取所有帐户订单； 有效，已取消或已完成
            notes:
                - 归集交易与逐笔交易的区别在于，同一价格、同一方向、同一时间的trade会被聚合为一条
                - 如果发送startTime和endTime，间隔必须小于一小时。
                - 如果没有发送任何筛选参数(fromId, startTime,endTime)，默认返回最近的成交记录
            args:
                fromId: 从哪一条成交id开始返回. 缺省返回最近的成交记录。
            usage:
                f_d = ba.req_allOrders(account_type="futures", binance_symbol="adaUSDT", start_time="2021-06-08 00:00:00")


        """
        req_method = "get"
        verify = True
        query_dict = {
            "symbol" : binance_symbol,
            "limit" : limit,
        }
        if account_type == "spot":
            host = self.spot_host
            path = "/api/v3/allOrders"
        elif account_type == "fullMargin":
            host = self.fullMargin_host
            path = "/sapi/v1/margin/allOrders"
            query_dict.update({"isIsolated":"FALSE"})
        elif account_type == "isoMargin":
            host = self.isoMargin_host
            path = "/sapi/v1/margin/allOrders"
            query_dict.update({"isIsolated":"TRUE"})
        elif account_type == "futures":
            host = self.futures_host
            path = "/fapi/v1/allOrders"
        elif account_type == "dfutures":
            host = self.dfutures_host
            path = "/dapi/v1/allOrders"
        if orderId:
            query_dict.update({"orderId":orderId})
        if start_time:
            query_dict.update({"startTime":int(get_timestamp(f"{start_time}").timestamp()*1000)})
        if end_time:
            query_dict.update({"endTime":int(get_timestamp(f"{end_time}").timestamp()*1000)})
        # 2. 发送请求
        resp_obj = self.request(
            req_method = req_method,
            host = host,
            path = path,
            query_dict = query_dict,
            verify = verify,
        )
        if is_obj:
            return resp_obj
            # 检测1. 状态码必须是要 '2' 开头的才是正常的!!
        response_dict = {}
        if resp_obj.status_code // 100 != 2: # eg: startTime填错了, status_code就会变成400.
            msg = f"获取数据失败，状态码：{resp_obj.status_code}，信息：{resp_obj.text}"
            print(msg)
            return response_dict
        else:
            data = resp_obj.json() # type: [[e, e],]
            # 检测2. 返回的数据要非空!
            if not data:
                msg = f"返回数据为空"
                logger.log(20, msg)
                # True:双向持仓, False:单向持仓
                return response_dict
            else:
                response_dict = resp_obj.json()
                logger.log(logging.DEBUG, f'请求成功: {response_dict}')
                return response_dict

    # 2. 获取合约账户资金流水的记录
    def get_income(self, account_type="futures", income_type="FUNDING_FEE", start_time=None, end_time=None, is_obj=False):
        """
            function: 获取合约账户资金流水的记录
            args:
                income_type:  "TRANSFER"，"WELCOME_BONUS", "REALIZED_PNL"，"FUNDING_FEE", "COMMISSION", and "INSURANCE_CLEAR"
        """
        req_method = "get"
        if account_type == "futures":
            host = self.futures_host
            path = "/fapi/v1/income"
        elif account_type == "dfutures":
            host = self.dfutures_host
            path = "/dapi/v1/income"
        else:
            raise Exception("现货没有此接口..")
        verify = True
        query_dict = {
            "incomeType" : income_type,
            "limit" : 1000,
        }
        #     # 币安接口中的startTime必须是 'ms'为单位的int型 (eg: 1234567890123)
        # start_time = start_time if start_time else int(get_timestamp("today").timestamp()*1000)  # 如果没有传入start_time, 则用今天0点的时间戳传入
        # end_time = end_time if end_time else int(get_timestamp("now").timestamp()*1000)  # 如果没有传入end_time, 则用当前的时间戳传入
        if start_time:
            query_dict.update({"startTime":start_time})
        if end_time:
            query_dict.update({"endTime":end_time})
        # 2. 发送请求
        resp_obj = self.request(
            req_method = req_method,
            host = host,
            path = path,
            query_dict = query_dict,
            verify = verify,
        )
        if is_obj:
            return resp_obj
            # 检测1. 状态码必须是要 '2' 开头的才是正常的!!
        hist_transcation_dict = {}
        if resp_obj.status_code // 100 != 2: # eg: startTime填错了, status_code就会变成400.
            msg = f"获取数据失败，状态码：{resp_obj.status_code}，信息：{resp_obj.text}"
            print(msg)
            return hist_transcation_dict
        else:
            data = resp_obj.json() # type: [[e, e],]
            # 检测2. 返回的数据要非空!
            if not data:
                msg = f"返回数据为空"
                logger.log(20, msg)
                # True:双向持仓, False:单向持仓
                return hist_transcation_dict
            else:
                hist_transcation_dict = resp_obj.json()
                logger.log(logging.DEBUG, f'get_income 成功: {hist_transcation_dict}')
                return hist_transcation_dict

    # 3. 展示资金费用收入
    def show_income(self, account_type="futures", last=True, start_time="today", end_time="now"):
        """
            function: 展示资金费用收入
            args:
                last: True/False  (设置为True, 则展示最近8小时的资金费用收入...)
                start_date/end_time: 字符串表示的时间  ("2021-03-12 08:03:33")
            usages:
                ba.show_income()
        """
        d = self.get_income(account_type=account_type, income_type="FUNDING_FEE")
        df = pd.DataFrame(d)
        df["time"] = pd.to_datetime(df['time'], unit="ms").dt.tz_localize('UTC').dt.tz_convert('hongkong') # 转化成东八区的时间
        if last == True:
            start_time = get_timestamp("now") - get_timedelta("8h") # 也就是开始时间是8小时前
        # query_df = df.query(f"'{get_timestamp('2021-04-16 7:00:00')}'<time<'{get_timestamp('2021-04-16 8:00:02')}'")
        query_df = df.query(f"'{get_timestamp(start_time)}'<=time<='{get_timestamp(end_time)}'")
        query_df[['income']] = query_df[['income']].apply(pd.to_numeric)
        return query_df

    # 4. 获取U本位/币本位的'持仓模式'
    def req_positionSide(self, account_type="futures"):
        """
            function:
                查询用户目前在'所有symbol'合约上的持仓模式：双向持仓或单向持仓
            return:
                True:双向持仓, False:单向持仓
            notes:
                合约下单前必须要知道该账户的'持仓模式', 不同持仓模式的下单参数不同, 一定要做好区分!!!
        """
        req_method = "get"
        if account_type == "futures":
            host = self.futures_host
            path = "/fapi/v1/positionSide/dual"
        elif account_type == "dfutures":
            host = self.dfutures_host
            path = "/dapi/v1/positionSide/dual"
        verify = True
            # 请求内容 (参数需要参考官网API)
        query_dict = {
        }
        # 2. 发送请求
        resp_obj = self.request(
            host = host,
            req_method = req_method,
            path = path,
            query_dict = query_dict,
            verify = verify,
        )
            # 检测1. 状态码必须是要 '2' 开头的才是正常的!!
        positionSide_dict = {}
        if resp_obj.status_code // 100 != 2:
            msg = f"获取数据失败，状态码：{resp_obj.status_code}，信息：{resp_obj.text}"
            print(msg)
            return {"dualSidePosition":True} # 如果该接口请求出错, 则默认返回'双向模式' (因为我自己的账号都是双向的..)
        else:
            data = resp_obj.json() # type: [[e, e],]
            # 检测2. 返回的数据要非空!
            if not data:
                msg = f"返回数据为空"
                logger.log(20, msg)
                # True:双向持仓, False:单向持仓
                return positionSide_dict
            else:
                positionSide_dict = resp_obj.json()
                logger.log(logging.DEBUG, f'req_positionSide成功: {positionSide_dict}')
                return positionSide_dict


    # 五. 其他次要-数据请求接口 (不太常用..)
    # ====================================================================
    # 查询'当前最优挂单' (restful接口)
    def req_bookTicker(self, account_type="spot", binance_symbol="BTCUSDT"):
        """
            functions:
                - 查询'当前最优挂单' (即: 买一价和卖一价)
            args:
                - binance_symbol: 需要大写  (eg: BNBUSDT)
            return:
                - 该币种买一卖一数据的dict: {}

            tips:
                - 通过循环60次访问, 发现耗时18s, 平均一次请求访问耗时在0.3s左右
        """
        # 1. 制造/打包请求数据
        req_method = "get"
        if (account_type == "spot") or (account_type == "fullMargin") or (account_type == "isoMargin"):
            host = self.spot_host
            path = "/api/v3/ticker/bookTicker"
        elif account_type == "futures":
            host = self.futures_host
            path = "/fapi/v1/ticker/bookTicker"
        elif account_type == "dfutures":
            host = self.dfutures_host
            path = "/dapi/v1/ticker/bookTicker"
        verify = False
            # 请求内容 (参数需要参考官网API)
        query_dict = {
            "symbol" : binance_symbol.upper(),  # binance_symbol需要大写
        }

        # 2. 发送请求
        resp_obj = self.request(
            req_method = req_method,
            host = host,
            path = path,
            query_dict = query_dict,
            verify = verify,
        )
            # 检测1. 状态码必须是要 '2' 开头的才是正常的!!
        bookTicker_dict = {}
        if resp_obj.status_code // 100 != 2:
            msg = f"获取数据失败，状态码：{resp_obj.status_code}，信息：{resp_obj.text}"
            print(msg)
            return bookTicker_dict
        else:
            data = resp_obj.json() # type: [[e, e],]
            # 检测2. 返回的数据要非空!
            if not data:
                msg = f"返回数据为空"
                logger.log(20, msg)
                return bookTicker_dict
            else:
                bookTicker_dict = resp_obj.json()
                logger.log(logging.DEBUG, f'req_bookTicker成功: {bookTicker_dict}')
                return bookTicker_dict

    # 用户持仓风险V2
    def req_positionRisk(self, account_type="spot"):
        """
            function: 获取账户持仓数据(包含强平价格)

            notes:
                - 接口的数据结构:
                    position_lst[0]:
                        symbol                    LITUSDT
                        positionAmt                 -28.0 # 净持仓量
                        entryPrice                 9.4922 # 开仓价格 (即: 成本价)
                        markPrice              9.44280371 # 当前标记价格
                        unRealizedProfit       1.38309612 # 未实现盈亏
                        liquidationPrice     369.27287258 # 强平价格
                        leverage                       20
                        maxNotionalValue            25000
                        marginType                  cross
                        isolatedMargin         0.00000000
                        isAutoAddMargin             false
                        positionSide                SHORT
                        notional            -264.39850388 # 当前名义市值 (即: 净持仓量*当前标记价格)
                        isolatedWallet                  0


        """
        req_method = "get"
        if account_type == "spot":
            msg = f"现货网关不能访问'positionRisk'"
            raise Exception(msg)
        elif account_type == "futures":
            host = self.futures_host
            path = "/fapi/v2/positionRisk"
        elif account_type == "dfutures":
            host = self.dfutures_host
            path = "/dapi/v1/positionRisk"
        verify = True
            # 请求内容 (参数需要参考官网API)
        query_dict = {
        }
        # 2. 发送请求
        resp_obj = self.request(
            req_method = req_method,
            host = host,
            path = path,
            query_dict = query_dict,
            verify = verify,
        )
            # 检测1. 状态码必须是要 '2' 开头的才是正常的!!
        position_lst = {}
        if resp_obj.status_code // 100 != 2:
            msg = f"获取数据失败，状态码：{resp_obj.status_code}，信息：{resp_obj.text}"
            print(msg)
            return position_lst
        else:
            data = resp_obj.json() # type: [[e, e],]
            # 检测2. 返回的数据要非空!
            if not data:
                msg = f"返回数据为空"
                logger.log(20, msg)
                return position_lst
            else:
                position_lst = resp_obj.json()
                # # 如果是合约的话, 就获取所有币种的仓位信息...
                # if self.api_type == "futures":
                #     _lst = []
                #     for position_dict in position_lst:
                #         if float(position_dict.get('positionAmt')):
                #             _lst.append(position_dict)
                #     position_lst = _lst
                logger.log(logging.DEBUG, f'req_positionRisk成功: {position_lst}')
                return position_lst

    # 获取U本位/币本位的'历史资金费率'
    def req_hist_funding_rate(self, account_type="futures", binance_symbol="", start_time=None, end_time=None, limit=1000, is_obj=False):
        """
            function:
                获取每个币种的历史'资金费率'
            args:
                binance_symbol: 币种 (币安需要大写)
                start_time: 起始时间 (需要毫秒为单位的int型数值) # api允许接受None值
                end_time: 结束时间 (需要毫秒为单位的int型数值) # api允许接受None值
                limit: 限制数据条数 (币安官网最大只支持1000条)
                    - 如果 startTime 和 endTime 都未发送, 返回最近 limit 条数据.
                    - 如果 startTime 和 endTime 之间的数据量大于 limit, 返回 startTime + limit情况下的数据。
            return:
                - 返回结果的时间排序是降序的 (即: 最近的时间在上面, 最早的时间在下面)
            usage:
                bra_futures.req_hist_funding_rate(limit=10) #
                bra_futures.req_hist_funding_rate(limit=1000) # 所有币种
                bra_futures.req_hist_funding_rate("ENJUSDT", limit=10) # ENJUSDTu本位永续合约最近10次的资金费率
                bra_dfutures.req_hist_funding_rate("adaUSD_PERP", limit=10)
        """
        req_method = "get"
        if (account_type == "spot") or (account_type == "fullMargin") or (account_type == "isoMargin"):
            msg = "现货不存在'资金费率'的概念..."
            raise Exception(msg)
        elif account_type == "futures":
            host = self.futures_host
            path = "/fapi/v1/fundingRate"
        elif account_type == "dfutures":
            host = self.dfutures_host
            path = "/dapi/v1/fundingRate"
        verify = False
        query_dict = {
            "limit" : limit,
        }
        if binance_symbol:
            query_dict.update({"symbol":binance_symbol.upper()})
        #     # 币安接口中的startTime必须是 'ms'为单位的int型 (eg: 1234567890123)
        # start_time = start_time if start_time else int(get_timestamp("today").timestamp()*1000)  # 如果没有传入start_time, 则用今天0点的时间戳传入
        # end_time = end_time if end_time else int(get_timestamp("now").timestamp()*1000)  # 如果没有传入end_time, 则用当前的时间戳传入
        if start_time:
            query_dict.update({"startTime":start_time})
        if end_time:
            query_dict.update({"endTime":end_time})
        # 2. 发送请求
        resp_obj = self.request(
            req_method = req_method,
            host = host,
            path = path,
            query_dict = query_dict,
            verify = verify,
        )
        if is_obj:
            return resp_obj
            # 检测1. 状态码必须是要 '2' 开头的才是正常的!!
        markprice_dict = {}
        if resp_obj.status_code // 100 != 2: # eg: startTime填错了, status_code就会变成400.
            msg = f"获取数据失败，状态码：{resp_obj.status_code}，信息：{resp_obj.text}"
            print(msg)
            return markprice_dict
        else:
            data = resp_obj.json() # type: [[e, e],]
            # 检测2. 返回的数据要非空!
            if not data:
                msg = f"返回数据为空"
                logger.log(20, msg)
                # True:双向持仓, False:单向持仓
                return markprice_dict
            else:
                markprice_dict = resp_obj.json()
                logger.log(logging.DEBUG, f'req_markprice 成功: {markprice_dict}')
                return markprice_dict

    # 获取万向划转的历史记录
    def get_hist_transfer(self, account_type="spot", t_type="MAIN_UMFUTURE", is_obj=False):
        """
            function: 获取万向划转的历史记录
            notes:
                主要的type划转类型:
                    MAIN_UMFUTURE 现货钱包转向U本位合约钱包
                    UMFUTURE_MAIN U本位合约钱包转向现货钱包
                    MAIN_C2C 现货钱包转向C2C钱包
                    C2C_MAIN C2C钱包转向现货钱包
            usage:
                bra_spot.get_hist_transfer(t_type="MAIN_UMFUTURE")
        """
        req_method = "get"
        if account_type == "spot":
            host = self.spot_host
            path = "/sapi/v1/asset/transfer"
        elif account_type == "futures":
            raise Exception("万向划转只能用于现货bra_spot, 不能用于合约bra_futures")
        verify = True
        query_dict = {
            "type" : t_type,
        }
        # 2. 发送请求
        resp_obj = self.request(
            req_method = req_method,
            host = host,
            path = path,
            query_dict = query_dict,
            verify = verify,
        )
        if is_obj:
            return resp_obj
            # 检测1. 状态码必须是要 '2' 开头的才是正常的!!
        hist_transcation_dict = {}
        if resp_obj.status_code // 100 != 2: # eg: startTime填错了, status_code就会变成400.
            msg = f"获取数据失败，状态码：{resp_obj.status_code}，信息：{resp_obj.text}"
            print(msg)
            return hist_transcation_dict
        else:
            data = resp_obj.json() # type: [[e, e],]
            # 检测2. 返回的数据要非空!
            if not data:
                msg = f"返回数据为空"
                logger.log(20, msg)
                # True:双向持仓, False:单向持仓
                return hist_transcation_dict
            else:
                hist_transcation_dict = resp_obj.json()
                logger.log(logging.DEBUG, f'get_hist_transfer 成功: {hist_transcation_dict}')
                return hist_transcation_dict

    # 查询每日资产快照
    def get_accountSnapshot(self, account_type="spot", limit=30, start_time=None, is_obj=False):
        """
            function: 查询每日资产快照
                    (每个快照都是UTC时间的'23:59:59'照的!![即:东八区早上7:59:59] 所以今天的快照只能明天才会出来; )
                    (但是开始时间输入一个昨天下午4:00的时间, 也会出来当天的快照)
                    [注意]: 传入时间也要参考UTC时间
                        - 假设我传入的是 Hong Kong时间: 21日3:00:00(即: UTC时间20日19:00:00), 而币安会返回UTC时间的20日数据
            notes:
                主要的account_type类型:
                    "spot": 现货
                    "fullMargin": 全仓杠杆账户
                    "isoMargin": 逐仓杠杆账户
                    "futures": u本位合约
                    "dfutures": 币本位合约
            usage:
                ba.get_accountSnapshot(account_type="spot")
        """
        req_method = "get"
        if (account_type == "spot") or (account_type == "fullMargin") or (account_type == "isoMargin"):
            host = self.spot_host
            path = "/sapi/v1/accountSnapshot"
        elif (account_type == "futures") or (account_type == "dfutures"):
            raise Exception("合约账户没有该api接口")
        verify = True
        query_dict = {
            "type" : account_type,
            "limit" : limit,
        }
        if start_time:
            query_dict.update({"startTime":start_time})
        # 2. 发送请求
        resp_obj = self.request(
            req_method = req_method,
            host = host,
            path = path,
            query_dict = query_dict,
            verify = verify,
        )
        if is_obj:
            return resp_obj
            # 检测1. 状态码必须是要 '2' 开头的才是正常的!!
        response_dict = {}
        if resp_obj.status_code // 100 != 2: # eg: startTime填错了, status_code就会变成400.
            msg = f"获取数据失败，状态码：{resp_obj.status_code}，信息：{resp_obj.text}"
            print(msg)
            return response_dict
        else:
            data = resp_obj.json() # type: [[e, e],]
            # 检测2. 返回的数据要非空!
            if not data:
                msg = f"返回数据为空"
                logger.log(20, msg)
                # True:双向持仓, False:单向持仓
                return response_dict
            else:
                response_dict = resp_obj.json()
                logger.log(logging.DEBUG, f'get_accountSnapshot 成功: {response_dict}')
                return response_dict

    # 按指定symbol获取最新价格 (区别于req_spot_price等)
    def req_last_price(self, account_type="spot", symbol=None, is_obj=False):
        """
            function: 获取最新价格
            args:
                symbol: 不发送交易对参数，则会返回所有交易对信息
            usage:
                bra_spot.get_last_price(symbol="LUNAUSDT")
        """
        req_method = "get"
        if (account_type == "spot") or (account_type == "fullMargin") or (account_type == "isoMargin"):
            host = self.spot_host
            path = "/api/v3/ticker/price"
        elif account_type == "futures":
            host = self.futures_host
            path = "/fapi/v1/ticker/price"
        elif account_type == "dfutures":
            host = self.dfutures_host
            path = "/dapi/v1/ticker/price"
        verify = False
        query_dict = {
        }
        if symbol:
            query_dict.update({"symbol":symbol})
        # 2. 发送请求
        resp_obj = self.request(
            req_method = req_method,
            host = host,
            path = path,
            query_dict = query_dict,
            verify = verify,
        )
        if is_obj:
            return resp_obj
            # 检测1. 状态码必须是要 '2' 开头的才是正常的!!
        response_dict = {}
        if resp_obj.status_code // 100 != 2: # eg: startTime填错了, status_code就会变成400.
            msg = f"获取数据失败，状态码：{resp_obj.status_code}，信息：{resp_obj.text}"
            print(msg)
            return response_dict
        else:
            data = resp_obj.json() # type: [[e, e],]
            # 检测2. 返回的数据要非空!
            if not data:
                msg = f"返回数据为空"
                logger.log(20, msg)
                return response_dict
            else:
                response_dict = resp_obj.json()
                logger.log(logging.DEBUG, f'请求成功: {response_dict}')
                return response_dict

    # 获取杠杆账户历史利息 (没用待删)
    def req_margin_interestHistory(self, account_type="fullMargin", isolatedSymbol=None, size=100, start_time=None, end_time=None, is_obj=False):
        """
            function: 获取利息历史
            args:
                isolatedSymbol:
                    不传: 则返回全仓的所有利息历史;
                    传入逐仓symbol: 返回对应symbol的逐仓利息 (eg: BNBUSDT; DOGEUSDT)
                size: 币安默认是10; 最大是100 (10表示: 只返回最近10小时的利息)
            notes:
                响应返回为降序排列。
                如果发送isolatedSymbol，返回指定逐仓symbol的记录。
                如果想查询6个月以前数据，设置 archived 为 true。
                返回的type数据有4种类型:
                PERIODIC 每小时收的利息
                ON_BORROW 借款的时候第一次收的利息
                PERIODIC_CONVERTED 每小时收的利息，用BNB抵扣
                ON_BORROW_CONVERTED 借款的时候第一次收的利息，用BNB抵扣

            返回参数说明:
                asset: 借款资产
                principal: 借款资产的借款数量
                interest: 借款资产的利息
                    (接的什么资产, 利息就按这个资产去计算, 最后应该可以统一转成bnb来还)
                    - 必须要把 bnb 转入对应的全仓杠杆账户/逐仓杠杆账户, 才可以...
                        (只有全仓账户的bnb, 不能用于逐仓账户的bnb利息结算)
                interestRate: 日利率
                type: 利息结算的类型
                isolatedSymbol:

            notices:
                [坑点]:
                    - 不传入isolatedSymbol: 可以获取全仓账户所有币种的利息
                    - 传入isolatedSymbol: 只能获取该币对的利息
                                            (没有办法获取逐仓中所有币对的利息..贼坑)
                                            (app版本可以, 但是需要自己做逆向模拟登录, 维护token就很麻烦)

        """
        req_method = "get"
        if account_type == "fullMargin":
            host = self.spot_host
            path = "/sapi/v1/margin/interestHistory"
        else:
            raise Exception("除全仓外都没有此api接口...")
        verify = True
        query_dict = {
            "size": size,
        }
        if isolatedSymbol:
            query_dict.update({"isolatedSymbol":isolatedSymbol})
        if start_time:
            query_dict.update({"startTime":start_time})
        if end_time:
            query_dict.update({"endTime":end_time})
        # 2. 发送请求
        resp_obj = self.request(
            req_method = req_method,
            host = host,
            path = path,
            query_dict = query_dict,
            verify = verify,
        )
        if is_obj:
            return resp_obj
            # 检测1. 状态码必须是要 '2' 开头的才是正常的!!
        response_dict = {}
        if resp_obj.status_code // 100 != 2: # eg: startTime填错了, status_code就会变成400.
            msg = f"获取数据失败，状态码：{resp_obj.status_code}，信息：{resp_obj.text}"
            print(msg)
            return response_dict
        else:
            data = resp_obj.json() # type: [[e, e],]
            # 检测2. 返回的数据要非空!
            if not data:
                msg = f"返回数据为空"
                logger.log(20, msg)
                # True:双向持仓, False:单向持仓
                return response_dict
            else:
                lst = resp_obj.json()
                lst = lst["rows"]
                df = pd.DataFrame(lst)
                df[["interest", "interestRate"]] = df[["interest", "interestRate"]].apply(pd.to_numeric)
                logger.log(logging.DEBUG, f'请求成功: {df}')
                return df

    # 市场深度信息
    def req_depth(self, account_type="spot", symbol="", limit=1000, is_obj=False):
        """
            function: 深度信息
            args:
                - limit: 	默认 100; 最大 5000. 可选值:[5, 10, 20, 50, 100, 500, 1000, 5000]
        """
        req_method = "get"
        if (account_type == "spot") or (account_type == "fullMargin") or (account_type == "isoMargin"):
            host = self.spot_host
            path = "/api/v3/depth"
        elif account_type == "futures":
            host = self.futures_host
            path = "/fapi/v1/depth"
        elif account_type == "dfutures":
            host = self.dfutures_host
            path = "/dapi/v1/depth"
        verify = False
        query_dict = {
            "symbol" : symbol,
            "limit" : limit,
        }
        # 2. 发送请求
        resp_obj = self.request(
            req_method = req_method,
            host = host,
            path = path,
            query_dict = query_dict,
            verify = verify,
        )
        if is_obj:
            return resp_obj
            # 检测1. 状态码必须是要 '2' 开头的才是正常的!!
        response_dict = {}
        if resp_obj.status_code // 100 != 2: # eg: startTime填错了, status_code就会变成400.
            msg = f"获取数据失败，状态码：{resp_obj.status_code}，信息：{resp_obj.text}"
            print(msg)
            return response_dict
        else:
            data = resp_obj.json() # type: [[e, e],]
            # 检测2. 返回的数据要非空!
            if not data:
                msg = f"返回数据为空"
                logger.log(20, msg)
                # True:双向持仓, False:单向持仓
                return response_dict
            else:
                response_dict = resp_obj.json()
                logger.log(logging.DEBUG, f'请求成功: {response_dict}')
                return response_dict

    # 获取服务器时间
    def req_time(self, account_type="spot", is_obj=False):
        """
            function: 获取服务器时间
        """
        req_method = "get"
        if account_type == "spot":
            host = self.spot_host
            path = "/api/v3/time"
        elif account_type == "futures":
            host = self.futures_host
            path = "/fapi/v1/time"
        elif account_type == "dfutures":
            host = self.dfutures_host
            path = "/dapi/v1/time"
        verify = False
        query_dict = {
        }
        # 2. 发送请求
        resp_obj = self.request(
            req_method = req_method,
            host = host,
            path = path,
            query_dict = query_dict,
            verify = verify,
        )
        if is_obj:
            return resp_obj
            # 检测1. 状态码必须是要 '2' 开头的才是正常的!!
        response_dict = {}
        if resp_obj.status_code // 100 != 2: # eg: startTime填错了, status_code就会变成400.
            msg = f"获取数据失败，状态码：{resp_obj.status_code}，信息：{resp_obj.text}"
            print(msg)
            return response_dict
        else:
            data = resp_obj.json() # type: [[e, e],]
            # 检测2. 返回的数据要非空!
            if not data:
                msg = f"返回数据为空"
                logger.log(20, msg)
                # True:双向持仓, False:单向持仓
                return response_dict
            else:
                response_dict = resp_obj.json()
                response_dict.update({"time":get_datetime_us(response_dict["serverTime"]/1000)})
                logger.log(logging.DEBUG, f'请求成功: {response_dict}')
                return response_dict

    # 万向划转
    def transfer(self, account_type="spot", t_type="MAIN_UMFUTURE", asset="USDT", amount=1, symbol=None, is_obj=False):
        """
            function: 万向划转
            args:
                - t_type: 划转方向
                - asset: 资产
                - amount: 资产数量
                - symbol: 逐仓账户的币对 (只有逐仓划转才需要此参数..)
            notes:
                主要的type划转类型:
                    万向划转:
                        MAIN_UMFUTURE 现货钱包转向U本位合约钱包
                        UMFUTURE_MAIN U本位合约钱包转向现货钱包
                        MAIN_C2C 现货钱包转向C2C钱包
                        C2C_MAIN C2C钱包转向现货钱包
                        MAIN_MINING 现货钱包转向矿池钱包
                        MINING_MAIN 矿池钱包转向现货钱包
                        MARGIN_MAIN 杠杆全仓钱包转向现货钱包
                    杠杆逐仓账户划转:
                            (杠杆逐仓账户只能和'现货账户'相互划转, 不能直接划转至'u本位合约账户')
                        MAIN_ISOMARGIN: 现货 -> 杠杆逐仓
                        ISOMARGIN_MAIN: 杠杆逐仓 -> 现货
            usage:
                ba.transfer(t_type="MAIN_UMFUTURE", amount=1)
                ba.transfer(t_type="UMFUTURE_MAIN", asset="USDT", amount=20)
                ba.transfer(t_type="MAIN_UMFUTURE", asset="USDT", amount=1000)
                ba.transfer(t_type="MAIN_MARGIN", asset="USDT", amount=10)
                ba.transfer(t_type="UMFUTURE_MARGIN", asset="USDT", amount=3000)
                ba.transfer(t_type="MAIN_ISOMARGIN", asset="USDT", amount=10, symbol="XRPUSDT")
                ba.transfer(t_type="MAIN_ISOMARGIN", asset="USDT", amount=1500, symbol="XRPUSDT")

                ba.transfer(t_type="MAIN_MARGIN", asset="BNB", amount=0.2, symbol="XRPUSDT")
                ba.transfer(t_type="MAIN_UMFUTURE", asset="BNB", amount=0.2, symbol="XRPUSDT")
        """
        req_method = "post"
        if account_type == "spot":
            host = self.spot_host
            transFrom, transTo = t_type.split("_")
            if transFrom == "ISOMARGIN" or transTo == "ISOMARGIN":
                path = "/sapi/v1/margin/isolated/transfer"
                if transFrom == "ISOMARGIN":
                    transFrom = "ISOLATED_MARGIN"
                    transTo = "SPOT"
                elif transTo == "ISOMARGIN":
                    transTo = "ISOLATED_MARGIN"
                    transFrom = "SPOT"
                query_dict = {
                    "transFrom" : transFrom,
                    "transTo" : transTo,
                    "asset" : asset, # USDT
                    "symbol" : symbol,  # XRPUSDT
                    "amount" : amount,
                }
            else:
                path = "/sapi/v1/asset/transfer"
                query_dict = {
                    "type" : t_type,
                    "asset" : asset,
                    "amount" : amount,
                }
        else:
            raise Exception("万向划转只能用于现货ba, 不能用于合约bra_futures")
        verify = True
        # 2. 发送请求
        resp_obj = self.request(
            req_method = req_method,
            host = host,
            path = path,
            query_dict = query_dict,
            verify = verify,
        )
        if is_obj:
            return resp_obj
            # 检测1. 状态码必须是要 '2' 开头的才是正常的!!
        transactionId_dict = {}
        if resp_obj.status_code // 100 != 2: # eg: startTime填错了, status_code就会变成400.
            msg = f"获取数据失败，状态码：{resp_obj.status_code}，信息：{resp_obj.text}"
            print(msg)
            return resp_obj.json()
        else:
            data = resp_obj.json() # type: [[e, e],]
            # 检测2. 返回的数据要非空!
            if not data:
                msg = f"返回数据为空"
                logger.log(20, msg)
                # True:双向持仓, False:单向持仓
                return transactionId_dict
            else:
                transactionId_dict = resp_obj.json()
                logger.log(logging.DEBUG, f'transfer 成功: {transactionId_dict}')
                return transactionId_dict

    # 全仓/逐仓的借款
    def loan(self, account_type="fullMargin", asset="USDT", amount=10, symbol="", is_obj=False):
        """
            function: 杠杆账户借贷 (MARGIN)
            args:
                account_type: "fullMargin"/ "isoMargin"
                symbol: 逐仓账户的币对 (只有'逐仓'才需要这个参数, 所以上面的参数要填'isoMargin')
                isisolated: 是否为'逐仓账户'
                    ("TRUE"/"FALSE") 必须是字符串的形式
            usage:
                ba.loan(asset="USDT", amount=0.1, account_type="fullMargin") # 全仓账户借款
                ba.loan(asset="1INCH", amount=1, account_type="fullMargin") # 全仓账户借款
                # 循环借币-全仓
                for i in range(30):
                    ba.loan(asset="MTL", amount=100, account_type="fullMargin")
                    time.sleep(1)
                ba.loan(asset="USDT", amount=0.1, account_type="isoMargin", symbol="XRPUSDT") # 逐仓账户借款
                ba.loan(asset="XRP", amount=0.1, account_type="isoMargin", symbol="XRPUSDT") # 逐仓账户借款
                ba.loan(asset="MTL", amount=100, account_type="isoMargin", symbol="MTLUSDT") # 逐仓账户借款
                # 循环借币-逐仓
                for i in range(100):
                    ba.loan(asset="MTL", amount=100, account_type="isoMargin", symbol="MTLUSDT") # 逐仓账户借款
                    time.sleep(1)
        """
        req_method = "post"
        verify = True
        query_dict = {
            "asset" : asset.upper(),
            "amount" : amount,
        }
        if account_type == "fullMargin":
            host = self.spot_host
            path = "/sapi/v1/margin/loan"
            query_dict.update({"isIsolated":"FALSE"})
        elif account_type == "isoMargin":
            host = self.spot_host
            path = "/sapi/v1/margin/loan"
            query_dict.update({"isIsolated":"TRUE", "symbol":symbol})
        else:
            raise Exception("只有杠杆账户有这个接口...")
        # 2. 发送请求
        resp_obj = self.request(
            req_method = req_method,
            host = host,
            path = path,
            query_dict = query_dict,
            verify = verify,
        )
        if is_obj:
            return resp_obj
            # 检测1. 状态码必须是要 '2' 开头的才是正常的!!
        response_dict = {}
        if resp_obj.status_code // 100 != 2: # eg: startTime填错了, status_code就会变成400.
            msg = f"获取数据失败，状态码：{resp_obj.status_code}，信息：{resp_obj.text}"
            print(msg)
            return resp_obj.json()
        else:
            data = resp_obj.json() # type: [[e, e],]
            # 检测2. 返回的数据要非空!
            if not data:
                msg = f"返回数据为空"
                logger.log(20, msg)
                # True:双向持仓, False:单向持仓
                return response_dict
            else:
                response_dict = resp_obj.json()
                logger.log(logging.DEBUG, f'请求成功: {response_dict}')
                return response_dict

    # 全仓/逐仓的还款
    def repay(self, account_type="fullMargin", asset="USDT", amount=10, symbol="", is_obj=False):
        """
            function: 杠杆账户归还借贷 (MARGIN)
            args:
                account_type: "fullMargin"/ "isoMargin"
                symbol: 逐仓账户的币对 (只有'逐仓'才需要这个参数, 所以上面的参数要填'isoMargin')
                isIsolated: 是否为'逐仓账户'
                    ("TRUE"/"FALSE") 必须是字符串的形式 (大小写不敏感)
            usage:
                bra_spot.repay(asset="USDT", amount=100, account_type="fullMargin") # 全仓还款USDT
                bra_spot.repay(asset="USDT", amount=1, account_type="isoMargin", symbol="xrpUSDT") # XRPUSDT逐仓还款USDT
                bra_spot.repay(asset="1INCH", amount=1, account_type="isoMargin", symbol="1inchUSDT") # 1INCHUSDT逐仓还款1INCH

                bra_spot.repay(asset="BNB", amount=1, account_type="fullMargin")
                    # 使用BNB归还全仓账户的利息 (可以设置一个小时定时任务: 每小时归还一次)
                    # 若不定期归还利息, 利息的'复利'也是很亏的...

            notice:
                - 逐仓账户还款会首先将利息还清, 再还借款
                - 逐仓账户貌似不能用bnb抵扣利息
                - 全仓账户中如果使用bnb抵扣利息, bnb利息的还款需要手动还... (定期还款, 别忘了)
                - 还款的amount如果超过'已借款数量', 则退回多余数量
            问题:
                - 逐仓账户可以用bnb来抵扣利息吗? 需要bnb转到逐仓账户吗? // 不能! (借了什么币就需要还什么币)
        """
        req_method = "post"
        verify = True
        query_dict = {
            "asset" : asset,
            "amount" : amount,
        }
        if account_type == "fullMargin":
            host = self.spot_host
            path = "/sapi/v1/margin/repay"
            query_dict.update({"isIsolated":"FALSE"})
        elif account_type == "isoMargin":
            host = self.spot_host
            path = "/sapi/v1/margin/repay"
            query_dict.update({"isIsolated":"TRUE", "symbol":symbol})
        else:
            raise Exception("只有杠杆账户有这个接口...")
        # 2. 发送请求
        resp_obj = self.request(
            req_method = req_method,
            host = host,
            path = path,
            query_dict = query_dict,
            verify = verify,
        )
        if is_obj:
            return resp_obj
            # 检测1. 状态码必须是要 '2' 开头的才是正常的!!
        response_dict = {}
        if resp_obj.status_code // 100 != 2: # eg: startTime填错了, status_code就会变成400.
            msg = f"获取数据失败，状态码：{resp_obj.status_code}，信息：{resp_obj.text}"
            print(msg)
            return response_dict
        else:
            data = resp_obj.json() # type: [[e, e],]
            # 检测2. 返回的数据要非空!
            if not data:
                msg = f"返回数据为空"
                logger.log(20, msg)
                # True:双向持仓, False:单向持仓
                return response_dict
            else:
                response_dict = resp_obj.json()
                logger.log(logging.DEBUG, f'请求成功: {response_dict}')
                return response_dict

    # 混合保证金 (btc质押..)
    def req_futures_loan_wallet(self, account_type="spot", is_obj=False):
        """
            function: 混合保证金钱包V2
            notes:
                - 暂没使用...
        """
        req_method = "get"
        host = self.spot_host
        path = "/sapi/v2/futures/loan/wallet"
        verify = True
        query_dict = {
        }
        # 2. 发送请求
        resp_obj = self.request(
            req_method = req_method,
            host = host,
            path = path,
            query_dict = query_dict,
            verify = verify,
        )
        if is_obj:
            return resp_obj
            # 检测1. 状态码必须是要 '2' 开头的才是正常的!!
        response_dict = {}
        if resp_obj.status_code // 100 != 2: # eg: startTime填错了, status_code就会变成400.
            msg = f"获取数据失败，状态码：{resp_obj.status_code}，信息：{resp_obj.text}"
            print(msg)
            return response_dict
        else:
            data = resp_obj.json() # type: [[e, e],]
            # 检测2. 返回的数据要非空!
            if not data:
                msg = f"返回数据为空"
                logger.log(20, msg)
                # True:双向持仓, False:单向持仓
                return response_dict
            else:
                response_dict = resp_obj.json()
                return response_dict






class SpreadData():
    """
        notes:
            - 套利中特殊使用的'价差数据结构'
        (类上面必须加装饰器. 通过装饰器, 来定义这个类是一个'数据结构'的类)
        args:
            direction: 1:开仓, -1:平仓 (open/close)
    """
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.spread_data_lst = []
        self.open_spread_rate_lst = []
        self.close_spread_rate_lst = []

    def get_spread_rate(self, direction: int, spot_price_dic: dict, future_price_dic: dict):
        """"""
        # 1. 如果是开仓的话: 市价开仓的价差选择: "future买一价" - "spot卖一价"
        open_spread = float(future_price_dic.get("bidPrice")) - float(spot_price_dic.get("askPrice"))
        open_spread_rate = open_spread / float(spot_price_dic.get("askPrice"))

        # 2. 如果是平仓的话: 市价平仓的价差选择: "future卖一价" - "spot买一价"
        close_spread = float(future_price_dic.get("askPrice")) - float(spot_price_dic.get("bidPrice"))
        close_spread_rate = close_spread / float(spot_price_dic.get("bidPrice"))

        if direction == 1:
            spread = open_spread
            spread_rate = open_spread_rate
            if len(self.open_spread_rate_lst) >= 60:
                if spread_rate > np.average(self.open_spread_rate_lst):
                    msg = "当前价差率大于近期平均价差率, 适合开仓! [此处应实现开仓操作]"
                    print(msg)
        elif direction == -1:
            spread = close_spread
            spread_rate = close_spread_rate
            if len(self.close_spread_rate_lst) >= 60:
                if spread_rate < np.average(self.close_spread_rate_lst):
                    msg = "当前价差率小于近期平均价差率, 适合平仓! [此处应实现平仓操作]"
                    print(msg)

        # 统计历史平均值
        self.open_spread_rate_lst.append(open_spread_rate)
        self.close_spread_rate_lst.append(close_spread_rate)
        spread_data = {"direction":direction, "spread":spread, "spread_rate":spread_rate}
        self.spread_data_lst.append(spread_data)
        msg = f"价差率数据: {spread_data}"
        logger.log(logging.INFO, msg)
        return spread_data


















"""

# [现货下单]
bra_spot = BinanceRestApi(api_type="spot", settings=lsh)
# 1. 限价单-买入
bra_spot.send_order("LUNAUSDT", direction="BUY", order_type="LIMIT", price=11, quantity=1)
# 2. 市价单-买入 (确定'标的资产'的数量)
bra_spot.send_order("LUNAUSDT", direction="BUY", order_type="MARKET", quantity=1) # 市价单比限价单少'price'和'timeInForce'参数
# 3. 市价单-买入 (确定'计价资产'的数量)
bra_spot.send_order("LUNAUSDT", direction="BUY", order_type="MARKET", quoteOrderQty=10)
# 4. 限价单-买入 (冰山委托) (但是我没发现和'普通限价单'的区别在哪)
bra_spot.send_order("LUNAUSDT", direction="BUY", order_type="LIMIT", price=11, quantity=20, icebergQty=2)
# 5. 限价止损单-卖出 (stopPrice和price与quantity的乘积, 都不能小于10u; 交易所有最新小单数量的限制)(MIN_NOTIONAL)
bra_spot.send_order("LUNAUSDT", direction="SELL", order_type="STOP_LOSS_LIMIT", stopPrice=11, price=10, quantity=1) # 该币种支持限价止损单
# 6. 市价止损单-卖出 (该币种不支持!!)
bra_spot.send_order("LUNAUSDT", direction="SELL", order_type="STOP_LOSS_MARKET", stopPrice=5, quantity=1) # 该币种不支持: Stop loss orders are not supported for this symbol
# 7. 限价止盈单-卖出 (stopPrice和price与quantity的乘积, 都不能小于10u; 交易所有最新小单数量的限制)(MIN_NOTIONAL)
bra_spot.send_order("LUNAUSDT", direction="SELL", order_type="TAKE_PROFIT_LIMIT", stopPrice=20, price=10, quantity=1) # 该币种支持限价止损单
# 8. 市价止盈单-卖出 (该币种不支持!!)
bra_spot.send_order("LUNAUSDT", direction="SELL", order_type="TAKE_PROFIT_MARKET", stopPrice=20, quantity=1) # 该币种不支持: Stop loss orders are not supported for this symbol


# [合约下单]
bra_futures = BinanceRestApi(api_type="futures", settings=lsh)
# 1. 限价单-买入
bra_futures.send_order("LUNAUSDT", offset="LONG", direction="BUY", order_type="LIMIT", price=11, quantity=1)
# 2. 市价单-买入 (确定'标的资产'的数量)
bra_futures.send_order("LUNAUSDT", offset="LONG", direction="BUY", order_type="MARKET", quantity=1) # 市价单比限价单少'price'和'timeInForce'参数
# 3. 市价单-买入 (确定'计价资产'的数量)
bra_futures.send_order("LUNAUSDT", offset="LONG", direction="BUY", order_type="MARKET", quoteOrderQty=10)
# 4. 限价单-买入 (冰山委托) (但是我没发现和'普通限价单'的区别在哪)
bra_futures.send_order("LUNAUSDT", offset="LONG", direction="BUY", order_type="LIMIT", price=11, quantity=20, icebergQty=2)
# 5. 限价止损单-卖出 (stopPrice和price与quantity的乘积, 都不能小于10u; 交易所有最新小单数量的限制)(MIN_NOTIONAL)
bra_futures.send_order("LUNAUSDT", offset="LONG", direction="SELL", order_type="STOP_LOSS_LIMIT", stopPrice=11, price=10, quantity=1) # 该币种支持限价止损单
# 6. 市价止损单-卖出 (该币种不支持!!)
bra_futures.send_order("LUNAUSDT", offset="LONG", direction="SELL", order_type="STOP_LOSS_MARKET", stopPrice=5, quantity=1) # 该币种不支持: Stop loss orders are not supported for this symbol
# 7. 限价止盈单-卖出 (stopPrice和price与quantity的乘积, 都不能小于10u; 交易所有最新小单数量的限制)(MIN_NOTIONAL)
bra_futures.send_order("LUNAUSDT", offset="LONG", direction="SELL", order_type="TAKE_PROFIT_LIMIT", stopPrice=20, price=10, quantity=1) # 该币种支持限价止损单
# 8. 市价止盈单-卖出 (该币种不支持!!)
bra_futures.send_order("LUNAUSDT", offset="LONG", direction="SELL", order_type="TAKE_PROFIT_MARKET", stopPrice=20, quantity=1) # 该币种不支持: Stop loss orders are not supported for this symbol

'开多'
bra_futures.send_order("BANDUSDT", offset="OPEN", direction="BUY", order_type="MARKET", price=10, quantity=1)
'开空'
bra_futures.send_order("BANDUSDT", offset="OPEN", direction="SELL", order_type="MARKET", price=40, quantity=1)
'平空'
bra_futures.send_order("BANDUSDT", offset="CLOSE", direction="BUY", order_type="MARKET", price=10, quantity=1)
'平多'
bra_futures.send_order("BANDUSDT", offset="CLOSE", direction="SELL", order_type="MARKET", price=40, quantity=1)


# [现货撤单]
bra_spot.send_order("LUNAUSDT", positionSide="LONG", side="BUY", order_type="LIMIT", price=12, quantity=1, ClientOrderId="123")
bra_spot.cancel_order("LUNAUSDT", ClientOrderId="123")

# [合约撤单]
bra_futures.send_order("LUNAUSDT", positionSide="LONG", side="BUY", order_type="LIMIT", price=12, quantity=1, ClientOrderId="123")
bra_futures.cancel_order("LUNAUSDT", ClientOrderId="123")




"""







def main():

    ba = BinanceAccount(settings=LSH_BINANCE_SETTING)

    ba = BinanceAccount(settings=ZL_BINANCE_SETTING)

    ba = BinanceAccount(settings=LB_BINANCE_SETTING)

    ba = BinanceAccount(settings=WYH_BINANCE_SETTING)

    ba = BinanceAccount(settings=MF_BINANCE_SETTING)



if __name__ == '__main__':
    print("Start test!\n\n")
    main()
    print("\n\n\nIt's over!")
