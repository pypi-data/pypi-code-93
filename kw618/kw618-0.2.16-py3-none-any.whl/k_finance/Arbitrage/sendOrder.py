"""
    导入本模块: from kw618.k_finance.Arbitrage.sendOrder import *
    notes:
        1. 借助了vnpy的框架来下单 (使用vnpy引擎来处理下单后的服务器返回数据)
            - 主要使用vnpy的两个模块:
                i. 主引擎/事件引擎/oms引擎 (异步数据处理框架)
                ii. 币安的'现货/合约'网关 (用于下单)
"""
from logging import INFO
import threading
import multiprocessing
import sys
from datetime import datetime
import time

# 这里的vnpy直接是导入site-packages里的python包. (而不是在我'量化'目录下的项目!!) (所以要修改的话, 去到源文件去改!!)
from vnpy.trader.setting import SETTINGS
from vnpy.event import EventEngine, Event, EVENT_TIMER
from vnpy.trader.engine import MainEngine
from vnpy.trader.engine import EmailEngine
from vnpy.trader.event import EVENT_TICK
from vnpy.trader.object import *
from vnpy.trader.constant import *
# 每个网关都内含REST和Websocket两个API. (网关是数据的来源, 只要导入网关就可以获取币安所有数据.)
# from vnpy.gateway.ctp import CtpGateway # ctp网关需要用到米匡, 暂时用不了
from vnpy.gateway.binance import BinanceGateway
from vnpy.gateway.binances import BinancesGateway
from vnpy.app.cta_strategy import CtaStrategyApp, CtaEngine
from vnpy.app.cta_strategy.base import EVENT_CTA_LOG

from kw618._file_path import *
from kw618.k_finance.Arbitrage.binance_gateway import *
from kw618.k_finance.Arbitrage.getData import *
from kw618.k_finance.Arbitrage.calData import *



SETTINGS["log.active"] = True
SETTINGS["log.level"] = 10
SETTINGS["log.console"] = True



def init_main_engine(engines=[CtaEngine], gateway_setting=LSH_BINANCE_SETTING):
    """
        function: 初始化一个添加好网关的main_engine
        args:
            setting: 网关连接的参数
            engines: [<engine_class>, <engine_class>] # 可以传入多个engine对象, 不是str
    """
    # 1. 实例化主引擎和事件引擎
    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)
    main_engine.account_name = gateway_setting.get("account_name").upper()
    main_engine.user = main_engine.account_name # 助记

    # 2. 实例化主引擎和事件引擎
    for engine in engines:
        main_engine.add_engine(engine)

    # 3. 添加网关实例, 并connect它 (即: ui中的连接选项)
    gateways = gateway_setting.get("gateways")
    for gateway in gateways:
        # 添加网关类后, 会返回这个实例化后的'网关对象' (此时才有 gateway_name这个属性)
        gateway_obj = main_engine.add_gateway(gateway)
        # 把这个settings参数传递给对应gateway_name的网关实例, 供其建立连接
        main_engine.connect(setting=gateway_setting, gateway_name=gateway_obj.gateway_name)

    # 4. 因为连接是异步的, 要确保连接完成后才能进行下面的步骤, 所以这里要睡10s.  等待主引擎连接网关
    time.sleep(15) # 经过测试, 10s还不够connect两个网关, 需要15s才算较为足够...

    # 5. 添加常用变量名
    main_engine.oms = main_engine.engines["oms"]
    main_engine.spot_rest_api = main_engine.gateways.get("BINANCE").rest_api
    main_engine.futures_rest_api = main_engine.gateways.get("BINANCES").rest_api
    main_engine.spot_trade_ws_api = main_engine.gateways.get("BINANCE").trade_ws_api
    main_engine.futures_trade_ws_api = main_engine.gateways.get("BINANCES").trade_ws_api
    main_engine.spot_market_ws_api = main_engine.gateways.get("BINANCE").market_ws_api
    main_engine.futures_market_ws_api = main_engine.gateways.get("BINANCES").market_ws_api

    return main_engine



class DataModule():
    """
        notes:
            - 自下而上的功能结构: (是有顺序的, 后一层功能是建立在前一层基础上的)
                pairs (所有我们关注的'币对')
                subscribe  (订阅ws的行情数据)
                cal (计算价差率)
                print (打印价差率)
                run   (下单)



    """
    def __init__(self, main_engine, client):
        """
            notes:
                - 1. 数据系统
        """
        # 1. 初始化vnpy中的组件
        self.main_engine = main_engine
        self.oms = main_engine.engines["oms"]
        self.Client = client

        # 2. 初始化SC.Data模块所需用到的变量
            # 套利币对的基本信息
        self.pairs = {}
            # 用于记录价差率相关数据 (测试当时捕捉的价差率和实际成交价差率的偏差)
        self.record_dict = {}
            # 记录'关键爆仓指数'
        self.futures_index = {}
            # main_print()函数需要打印的三块内容:
                # 1. 存放各个币对的资金费率
        self.funding_rate_dict = {}
                # 2. 存放各个币对的开仓价差率
        self.spread_rate_open_dict = {}
                # 3. 存放各个币对的平仓价差率
        self.spread_rate_close_dict = {}
            # 子线程控制的开关
        self.alive = True # 初始状态是: '不在计算价差率'
            # 存放所有现货的'最新价格' (每10s更新一次)
        self.spot_last_price_lst = []
            # 存放所有合约的'最新价格' (每10s更新一次)
        self.futures_last_price_lst = []
            # 现货/合约的最新价格的df
        self.spot_last_price_df = pd.DataFrame()
        self.futures_last_price_df = pd.DataFrame()

        # 3. 执行一些初始启动函数
        pass

    def _check_pair_name(self, pair_name):
        """
            function: 鉴于我经常把这个symbol/exchange拼错, 导致的各种bug... 提前先在oms.contract中检查...
            return: 如果名称无误, 则返回True
        """
        # 1. 拆分: 得到'交易所'和'币对'
        pair_name = pair_name.upper()
        exchange_name, symbol = pair_name.split(".")

        # 2. '交易所名称'检查
        for ex in Exchange:
            if exchange_name == ex.name:
                exchange = ex
        if not exchange:
            msg = f"没有该交易所, 请检查..."
            raise Exception(msg)

        # 3. '币对名称'检查
        contracts_lst = list(self.oms.contracts)
        success = False
        for contract in contracts_lst:
            _sy, _ex = contract.split(".") # contract: 'wbtceth.BINANCE'
            if symbol == _sy:
                success = True
        if not success:
            msg = f"oms.contract中不存在该symbol: {symbol}"
            raise Exception(msg)
        else:
            return True

    def _split_pair_name(self, pair_name):
        """
            note:
                - 拆分'交易所名称'和'币对名称', 返回的都是大写
                - 凡是会输入 "pair_name"参数的函数, 第一件事情就是调用该函数验证pair_name
            return: ("BINANCE.LUNAUSDT", "BINANCE", "LUNAUSDT", "ETH") # 返回一个元组
        """
        # 1. 核验pair名称
        self.Data._check_pair_name(pair_name=pair_name)
        # 2. 拆分pair名称
        pair_name = pair_name.upper()
        exchange_name, symbol = pair_name.split(".")
        asset_name = symbol[:-4]
        return (pair_name, exchange_name, symbol, asset_name) # ("BINANCE.LUNAUSDT", "BINANCE", "LUNAUSDT", "ETH") 返回一个元组

    def _check_tick(self, pair_lst):
        """
            function: 核对该币对的tick数据是否已经开始被收到...  (很多后续操作需要依赖tick数据)
                        [oms有tick数据是前置条件]
                    - 既核验了'pair_name', 又核验了'tick数据'
            notes:
                - [注意]: 该函数的调用最好是放在'循环外' (否则每秒执行一遍, 挺没意义的...)
                            # 因为 _check_balance等 很多函数都是在捕捉到合适价差率马上下单前执行的, 这个窗口期很短, 尽量减少该函数的重复工作, 提高性能!!
                - 什么函数需要用到tick? 需要在用tick前执行该check函数?
                    1. self.Data.main_cal()
                    2. self.Trade._check_balance() # 需要用到最新价last_price (而 get_last_price()是需要用到self.oms.ticks中的数据的)

        """
        need_to_add_pair_lst = []
        for pair_name in pair_lst:
            # 1. 校验pair_name
            (pair_name, exchange_name, symbol, asset_name) = self.Data._split_pair_name(pair_name=pair_name)

            # 2. 校验2个点: i.是否已经存在于self.pairs中 ii.是否已经有tick数据
                # (一个条件没有满足, 都需要加入到 need_to_add_pair_lst 中, 需要重新add_pairs)
            if (not self.Data.pairs.get(pair_name)) or \
                (f"{symbol.lower()}.{exchange_name}" not in list(self.oms.ticks)) or \
                (f"{symbol.upper()}.{exchange_name}" not in list(self.oms.ticks)):
                # pairs中没有的币种才需要去add_pairs
                need_to_add_pair_lst.append(pair_name)

        # 3. 把所有'需要add_pairs'的pair_lst传入 (开始在self.Data中生成该pair的字典)
        if len(need_to_add_pair_lst) > 0:
            self.Data.add_pairs(pair_lst=need_to_add_pair_lst)

        # 最后核验: 前面的3个步骤是否成功完成 [未成功,则报错]
        for pair_name in pair_lst:
            (pair_name, exchange_name, symbol, asset_name) = self.Data._split_pair_name(pair_name=pair_name)
            if f"{symbol.lower()}.{exchange_name}" not in list(self.oms.ticks):
                msg = f"{symbol}-现货 的tick数据获取失败: 请检查网络... or 通过add_pairs函数订阅pair后, 睡眠一段时间再重试...."
                raise Exception(msg)
            if f"{symbol.upper()}.{exchange_name}" not in list(self.oms.ticks):
                msg = f"{symbol}-合约 的tick数据获取失败: 请检查网络... or 通过add_pairs函数订阅pair后, 睡眠一段时间再重试...."
                raise Exception(msg)

        return True # 未报错,则核验成功

    def _ensure_pairs(self, pair_lst):
        """
            function: 确保 main_cal()函数, 已经在计算pair_name的价差率了..
            notes:
                - 总共核验了3样数据:
                    1. exchange_name 和 symbol 有没有拼写错误
                    2. 是否已经同时订阅了该pair_name的 '期货和现货的tick数据'
                        (只要有tick推送, 资金费率就会被实时更新在self.Data.funding_rate_dict中)
                    3. 是否已经开始计算该pair_name的 '开/平仓价差率'
                            [本函数主要实现这个部分] [1/2是self._check_tick中实现的]
        """
        # 1. 核验1/2两点
        self.Data._check_tick(pair_lst=pair_lst)

        # 2. 核验是否已经开始计算该币种的价差率
        need_to_main_cal_pair_lst = [] # 需要'重新添加计算价差率的pair_name的lst'
        for pair_name in pair_lst:
            (pair_name, exchange_name, symbol, asset_name) = self.Data._split_pair_name(pair_name=pair_name)
            # 其实只需要校验'open_dict'和'close_dict'的其中一种即可
            if asset_name in self.Data.spread_rate_open_dict.keys():
                pass
            else:
                need_to_main_cal_pair_lst.append(pair_name)

        # 3. 一旦没有找到某个币种的'价差率', 则重新执行main_cal (即: 杀死所有线程, 重新启动)
        if len(need_to_main_cal_pair_lst) > 0:
            # 先杀死, 后重新开启全部币种的多线程, 计算价差率...
            self.Data.active()
        elif len(need_to_main_cal_pair_lst) == 0:
            return True

    def _cal_spread_rate(self, pair_name):
        """
            function: 传入一个pair_name, 得到该symbol现货和合约的'最优挂单信息', 返回'价差率'相关信息
            args:
                pair_name: # BINANCE.LUNAUSDT
            return: '开仓价差', '开仓价差率', '平仓价差', '平仓价差率'
        """
        # 1. 初始化
        (pair_name, exchange_name, symbol, asset_name) = self.Data._split_pair_name(pair_name=pair_name)
        oms = self.oms

        # 2. 获取两个实时'挂单信息' (得到现货/合约的买一/卖一价, 总共4个价格)
        spot_live = oms.ticks[f"{symbol.lower()}.{exchange_name}"].live # 获取到实时推送的'现货-最优挂单信息'
        futures_live = oms.ticks[f"{symbol.upper()}.{exchange_name}"].live # 获取到实时推送的'合约-最优挂单信息'
        spot_buy1_price = spot_live.get("bid_price_1") # 现货买一价
        spot_sell1_price = spot_live.get("ask_price_1") # 现货卖一价
        futures_buy1_price = futures_live.get("bid_price_1") # 合约买一价
        futures_sell1_price = futures_live.get("ask_price_1") # 合约卖一价
        # print(f"[{pair_name}]: --------spot_live:{spot_live}, futures_live:{futures_live}")

        # 3. 计算'价差率'
            # i. 开仓的价差率
        spread_open = futures_buy1_price - spot_sell1_price
        spread_rate_open = spread_open / spot_sell1_price
            # ii. 平仓的价差率
        spread_close = futures_sell1_price - spot_buy1_price
        spread_rate_close = spread_close / spot_buy1_price
        # print(f"[{pair_name}]: --------spread_rate_open:{spread_rate_open}, spread_rate_close:{spread_rate_close}")

        # 4. 将计算好的价差率存储到self.pairs对象中 (便于外部访问)
        self.Data.spread_rate_open_dict[asset_name] = spread_rate_open
        self.Data.spread_rate_close_dict[asset_name] = spread_rate_close
        return spread_open, spread_rate_open, spread_close, spread_rate_close

    def _req_spot_last_price(self):
        spot_url = "https://api.binance.com/api/v3/ticker/price"
        spot_last_price_lst = req(spot_url, is_obj=True).json()
        spot_last_price_dict = {d.get("symbol"):d.get("price") for d in spot_last_price_lst}
        spot_last_price_df = pd.DataFrame(spot_last_price_lst)
        spot_last_price_df["price"] = spot_last_price_df["price"].apply(pd.to_numeric)
        self.spot_last_price_df = spot_last_price_df

    def _req_futures_last_price(self):
        futures_url = "https://fapi.binance.com/fapi/v1/premiumIndex" # 标记价格&资金费率
        futures_last_price_lst = req(futures_url, is_obj=True).json()
        futures_last_price_dict = {d.get("symbol"):d.get("markPrice") for d in futures_last_price_lst}
        futures_last_price_df = pd.DataFrame(futures_last_price_lst)
        futures_last_price_df = futures_last_price_df[["symbol", "markPrice", "lastFundingRate"]]
        futures_last_price_df = futures_last_price_df.rename(columns={"markPrice":"price", "lastFundingRate":"funding_rate"})
        futures_last_price_df[["price", "funding_rate"]] = futures_last_price_df[["price", "funding_rate"]].apply(pd.to_numeric)
        futures_last_price_df["funding_rate"] = futures_last_price_df["funding_rate"].apply(lambda x: f"{x:.3%}")
        self.futures_last_price_df = futures_last_price_df

    def _cal_sum_open_notional(self):
        "待删: 不需要关注开仓时候的市值.. 关注最新市值就可以了"
        "计算: 开仓名义市值的总和"
        sum_open_notional = 0
        for k, v in self.oms.positions.items():
            sum_open_notional += abs(v.volume * v.price)
        return round(sum_open_notional, 6)

    def _live_update_funding_rate(self):
        """
            function: 实时更新各个币种的'资金费率'到 self.pairs中 (使用子线程在默默不断的更新)
            notes:
                - 每秒更新一次
        """
        ticks = self.oms.ticks
        if ticks:
            for k, v in ticks.items():
                symbol, exchange_name = k.split(".")
                asset = symbol[:-4]
                pair_name = f"{exchange_name}.{symbol}" # BINANCE.ethusdt是现货; BINANCE.LUNAUSDT是合约; (只有大写的合约才有'资金费率')
                if pair_name in self.pairs:
                    self.funding_rate_dict.update({asset:v.funding_rate})

    def _live_update_margin_rate(self):
        """
            functions: 每隔10s, 重新获取一次account数据, 并计算最新的'维持保证金率'
        """
        # 1. 请求account数据
        self.Client.futures_rest_api.query_account() # 平均耗时1s
        # 因为上面的请求是异步的, 而后面的处理都是基于上面的req返回的数据的, 所以必须要等待它请求完成才能继续
        time.sleep(1)

        # 2. 计算最新的'维持保证金率'
            # 1. 获取基础数据
        usdt_account = self.oms.accounts.get("futures").get("BINANCES.USDT", "") # 如果取不出数, 可能是网络问题导致上面的req请求还没得到resp (异步就有这种问题...)
            # i.如果合约账户有usdt保证金:
        if usdt_account:
            marginBalance = usdt_account.marginBalance # 保证金余额
            maintMargin = usdt_account.maintMargin # 维持保证金
            pnl = usdt_account.pnl # 未实现浮动盈亏
            usdt_balance = usdt_account.balance # usdt钱包余额
            availableBalance = usdt_account.availableBalance # 可用划转余额
            # sum_open_notional = self.Data._cal_sum_open_notional() # 开仓名义市值的总和
            # ii.如果合约账户没有usdt保证金:
        else:
            logger.log(50, "【警告】: #############  没有获取到合约的USDT账户, 请检查网络问题, 或者合约账户中是否还存在USDT!!")
            usdt_balance = 0
            pnl = 0
            marginBalance = 0
            maintMargin = 0
            availableBalance = 0
            # sum_open_notional = 0

            # 2. 计算4个核心爆仓指标
        if marginBalance == 0:
            margin_rate = 0
        else:
            # i. 维持保证金率
            margin_rate = maintMargin / marginBalance

        # 3. 将最新的'保证金率'相关数据, 存入oms的容器中
        self.futures_index = {
            "marginBalance" : marginBalance, # 保证金余额
            "maintMargin" : maintMargin, # 维持保证金
            "margin_rate" : margin_rate, # 维持保证金率 (维持保证金/保证金余额)
            "pnl" : pnl, # 未实现盈亏
            "usdt_balance" : usdt_balance, # usdt钱包余额
            "availableBalance" : availableBalance, # 可用划转余额
            "time" : datetime.now(),
        }

    def _live_update_delta_time(self):
        """
            function: 每隔1分钟, 去获取服务器时间, 与本地时间相减, 得到一个'delta_time'
                        (之后检查ws收到数据的时间戳和本地时间戳的差距, 来判断该ws推送的数据是否超过时效..)
        """
        agg_delta_time = get_timedelta(0)
        for i in range(3):
            msg = req("https://api.binance.com/api/v3/time")
            this_time = get_datetime_us()
            d = json.loads(msg)
            server_time = get_datetime_us(d.get("serverTime")/1000)
            # delta_time = get_timestamp(server_time) - get_timestamp(this_time)
            delta_time =  get_timestamp(this_time) - get_timestamp(server_time)
            print(f"[当前时间]: {this_time}")
            print(f"服务器时间戳: {server_time}\n")
            print(f"时间差: {delta_time}\n")
            agg_delta_time += delta_time
        avg_delta_time = agg_delta_time / 3
        self.delta_serverTime = avg_delta_time
        self.Client.delta_serverTime = avg_delta_time

    def req_last_price(self, pair_name, type="spot"):
        """
            function: 使用REST的方式获取last_price (网络请求)
        """
        (pair_name, exchange_name, symbol, asset_name) = self.Data._split_pair_name(pair_name=pair_name)
        # 使用req()函数, 直接访问请求得到'现货+合约'的最新价格
        if type == "spot":
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
            res_obj = req(url, is_obj=True)
            return float(res_obj.json().get("price"))
        elif type == "futures":
            url = f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={symbol}"
            res_obj = req(url, is_obj=True)
            return float(res_obj.json().get("price"))

    def get_last_price(self, pair_name, type="spot"):
        """
            note: 默认获取的是现货的最新价格
                - 优先使用 oms.ticks 来获取最新价格
                - 当 oms.ticks 没有该币种数据时, 则通过访问币安rest接口来获取最新价格 (耗时会比较久)
        """
        (pair_name, exchange_name, symbol, asset_name) = self.Data._split_pair_name(pair_name=pair_name)
        if type == "spot":
            if self.oms.ticks.get(f"{symbol.lower()}.{exchange_name}"):
                last_price = self.oms.ticks.get(f"{symbol.lower()}.{exchange_name}").last_price
            else:
                last_price = self.req_last_price(pair_name=pair_name, type="spot")
        elif type == "futures":
            if self.oms.ticks.get(f"{symbol.upper()}.{exchange_name}"):
                last_price = self.oms.ticks.get(f"{symbol.upper()}.{exchange_name}").last_price
            else:
                last_price = self.req_last_price(pair_name=pair_name, type="futures")
        return last_price

    def subscribe_many(self, pair_lst=["BINANCE.LUNAUSDT", "BINANCE.ALPHAUSDT"]):
        """
            notes:
                - 使用 futures_market_ws_api, spot_market_ws_api 中改写的 subscribe_many 很方便就可以同时订阅多币种
                - 这里不检验 pair_name的书写正确性, 是因为在 add_pairs中已经检测过了...
                - 也可以用于'重新订阅' (当服务器推送的时间戳与本地严重偏离时..)

            问题:
                - 发现同时订阅多个币种的时候, 会存在一个问题: 很多币种的tick数据更新很慢...延迟有好几秒的...
                    可能的原因:
                        1.网络延迟问题...(难以改善) (解决: aws东京节点)
                        2.订阅数量过多导致接收ws推送和计算速度跟不上的问题 (那只能减少同时订阅币种数) (解决: c5d 计算优化型)
                        3.币安服务器问题(没办法解决,别人也一样)
                    解决方案: 在aws东京节点试试网速, 如果延迟还是很久则只能通过订阅'单一币种'或'少数几个核心币种'方式来玩策略了....
        """
        # 1. 拆解symbol_lst
        lower_symbol_lst = [pair_name.split(".")[1].lower() for pair_name in pair_lst]
        upper_symbol_lst = [pair_name.split(".")[1].upper() for pair_name in pair_lst]
        # 2. 发起订阅 (subscribe_many也是自己写的, 已经实现在vnpy框架内了)
        self.Client.spot_market_ws_api.subscribe_many(lower_symbol_lst)
        self.Client.futures_market_ws_api.subscribe_many(upper_symbol_lst)
        # 3. 等待异步订阅完成
        logger.log(10, f"睡眠5秒, 等待所有币种异步订阅完成")
        time.sleep(5) #
        logger.log(20, f"当前已经订阅tick的pair:\n{list(self.oms.ticks.keys())}")

    def stop_subscribe(self):
        """
            function: 停止订阅所有ws的推送 (先stop 'gateway.market_ws_api')
        """
        if self.Client.spot_market_ws_api._active:
            self.Client.spot_market_ws_api.stop()
            self.Client.spot_market_ws_api.join()
        if self.Client.futures_market_ws_api._active:
            self.Client.futures_market_ws_api.stop()
            self.Client.futures_market_ws_api.join()
        self.oms.ticks = {}
        self.Data.pairs = {}

    def add_pairs(self, pair_lst=["BINANCE.LUNAUSDT", "BINANCE.ALPHAUSDT"]):
        """
            function: 同时添加多个pair_name, 同时订阅多个pair_name的 '现货and合约' 的tick数据
                        (完全改装于 add_pair函数)
            args:
                pair_lst: # ["BINANCE.LUNAUSDT", "BINANCE.ALPHAUSDT"]
                to_subscribe: True/False # 是否需要订阅tick数据(最优挂单信息)
        """
        # 1. 核对每个'pair_name'输入无误!!
        for pair_name in pair_lst:
            (pair_name, exchange_name, symbol, asset_name) = self.Data._split_pair_name(pair_name=pair_name)

            # 2. 初始化一些数据
            self.pairs.update(
                {
                    # [待删] 基本上弃用了.....
                    pair_name : {
                        "exchange_name" : exchange_name, # 'BINANCE' (是个字符串)
                        "symbol" : symbol, # LUNAUSDT; (用大写来作为symbol的一般通用形式) (pair_name是大小写不敏感的, 但是symbol最好还是大写)
                        "equal_volume" : False, # 用于判断某个pair_name的'期现数量是否相等'
                        "sum_volume" : np.nan, # 默认是个空数字
                    }
                }
            )
            self.record_dict.update({pair_name:[]})

        # 3. 订阅各个'pair'的tick'最优挂单'数据 (现货和合约)
            # [注意]: 订阅是'异步订阅', 所以这里没有阻塞直接就往下执行了, 所以如果后面的任务中需要用到这个请求中的数据, 则会访问失败... 后续需要一定的睡眠时间
        self.Data.subscribe_many(pair_lst=pair_lst) # 订阅该'套利对'的现货和期货的tick数据

    def get_my_pair_lst(self):
        """
            function: 获取当前持仓的所有币种的pair_name...
        """
        # 1. 获取当前持仓的所有币种
        pair_lst = []
        for position_name, position_data in self.oms.positions.items():
            # 只把市值大于30u的position加入 pair_lst (否则视为'小额资产', 暂不处理...)
            if abs(position_data.volume * position_data.price) >= 30:
                symbol, exchange_name, direction = position_name.split(".") # LUNAUSDT, BINANCE, '空'
                pair_name = f"{exchange_name}.{symbol.upper()}"
                pair_lst.append(pair_name)
        return pair_lst

    def add_my_pairs(self):
        """
            function: 订阅我自己持仓的这几个币种...
        """
        # 1. 获取当前持仓的所有币种
        pair_lst = self.Data.get_my_pair_lst()

        # 2. 开始订阅所有币种的tick数据
        self.Data.add_pairs(pair_lst=pair_lst)
        logger.log(10, f"延长睡眠8s, 确保我的所有持仓币种的tick都已经推送...")
        time.sleep(8) # 很容易没有tick数据而报错... (所以睡眠时间长点, 可以减少报错发生的概率)
        logger.log(20, f"当前已经订阅tick的pair:\n{list(self.oms.ticks)}")

        # 3. 核对所有pair的 '期现volume是否匹配'
        self.Show.show_my_pairs()

    def main_cal(self):
        """
            notes:
                - '主计算'函数 (0.1s计算一次)
                - Data系统下的主计算函数: 循环计算各种币对的价差率!!
                    [其他很多模块都需要调用这里计算的结果!!!]
        """
        def _recur_cal_spread_rate(pair_name):
            self.Data._check_tick(pair_lst=[pair_name])
            while True:
                if not self.alive:
                    break
                self._cal_spread_rate(pair_name=pair_name)
                time.sleep(0.1)

        # 如果发现alive已经为True, 说明子线程已经在运行, 此时先kill掉这些子线程!! (睡1s是确保所有子线程都已经停止了)
        if self.alive == True:
            self.alive = False
            time.sleep(1)
        self.alive = True # True表示: 可以开始循环计算'价差率'了

        # 利用多线程来执行'计算价差率' //用多进程可以吗?? //实测不可以....
        self.cal_thread_pool = []
        pair_name_lst = list(self.Data.pairs.keys())
        for pair_name in pair_name_lst:
            logger.log(10, "\n即将生成一个子线程...")
            t = threading.Thread(
                target=_recur_cal_spread_rate, # 不是该类下的直接子函数, 这里调用函数时不能在前面加self?
                kwargs=({'pair_name':pair_name})
                )
            t.start()
            self.cal_thread_pool.append(t)

    def stop_cal(self):
        # 把该main_cal函数杀死.. (其实就是让main_cal函数退出循环)
        # (要想main_cal继续运行, 可以执行 self.Data.main_cal()函数;)
        self.alive = False

    def active(self):
        self.Data.stop_cal()
        time.sleep(1) # 等待所有子线程死亡 (死透)
        self.Data.main_cal()
        time.sleep(3) # 等待所有子线程都开始计算

    def query_all_account(self):
        "调用vnpy框架的接口"
        self.Client.spot_rest_api.query_all_account()

    def query_positions(self):
        "调用vnpy框架的接口"
        self.Client.futures_rest_api.query_account()


class RiskModlue():
    def __init__(self, main_engine, client):
        """
            notes:
                - 风控模块
        """
        # 1. 初始化vnpy中的组件
        self.main_engine = main_engine
        self.oms = main_engine.engines["oms"]
        self.Client = client

        # 2. 初始化SC.Risk中所需变量
        self.risk_margin_rate = 0.10
        self.receiver_email = "15168201914@163.com" # 以后能不能提醒多个邮箱?? (把老爸老妈都加进去)
        self.to_send_email = True
        self.to_auto_close_position = True

    def _check_margin_rate(self):
        """
            function: 定时检测'保证金率'是否超过'risk_margin_rate', 一旦超过, 则发送邮件 (每60s执行一次)
        """
        margin_rate = self.Risk.get_margin_rate()

        # '维持保证金率'预警 (发送邮件...)
        if margin_rate >= self.risk_margin_rate:
            if self.to_send_email == True: # 可以手动将该对象的该属性设置成False, 从而禁止发送邮件...
                subject = f"【{self.Client.account_name}: 保证金率超过 {self.risk_margin_rate:.2%}】-> {margin_rate:.2%}" # 邮件标题
                content = self.Show.show_futures_index() # 获取'核心爆仓指标'的文本str输出
                receiver = self.receiver_email
                self.main_engine.send_email(subject, content, receiver)
            if self.to_auto_close_position == True: # 可以手动将该对象的该属性设置成False, 从而禁止'自动平仓'...
                self.Client.smart_close_position()

    def _repay_bnb(self):
        """
            每小时定期归还bnb的利息 (需要手动还利息..)
        """
        self.Client.spot_rest_api.repay(asset="BNB", amount=1, isIsolated="False")

    def get_margin_rate(self):
        """
            function: 获取'维持保证金率'

            todo:
                - 以后每隔10s检查一次保证金率, 如果超过70%, 则自动平掉部分仓位
                    (仓位选择: 选择价差率最低的币种, 小批量平仓, 死循环, 直到保证金率低于70%)
        """
        margin_rate = self.Data.futures_index.get("margin_rate")
        return margin_rate

    def check_match(self):
        """
            function: 检查全币种是否配平!!
        """
        def _round_num(doc):
            "作用: 四舍五入 (可视化呈现)"
            delta_volumn = round(doc.get("期现-数量差", 0), 4)
            delta_value = round(doc.get("期现-价值差", 0), 1)
            hedge_marketValue = round(doc.get("对冲市值", 0), 0)
            price = round(doc.get("价格", 0), 4)
            spot_volume = f"{doc.get('现货数量', 0):.4f}"
            futures_volume = round(doc.get("合约数量", 0), 4)
            doc.update({
                "期现-数量差":delta_volumn, "期现-价值差":delta_value, "对冲市值":hedge_marketValue,
                "价格":price, "现货数量":spot_volume, "合约数量":futures_volume,
            })
            return doc

        # 0. 获取合约的最新价格 (计算价值要用)
        self.Data._req_futures_last_price()
        futures_last_price_df = self.Data.futures_last_price_df

        # 1. 获取合约仓位数量
        futures_volume_lst = []
        positions = self.oms.positions
        for vt_positionid, position_obj in positions.items(): # vt_positionid: 'SUSHIUSDT.BINANCE.空'
            symbol = position_obj.symbol # symbol: 'SUSHIUSDT'
            futures_volume = position_obj.volume # volume: 20
            d = {
                "symbol" : symbol, "futures_volume" : futures_volume,
            }
            futures_volume_lst.append(d)
        futures_volume_df = pd.DataFrame(futures_volume_lst)
             # 作用: 双向持仓时候, 会把'正向'和'反向'的volume相互抵消
        if len(futures_volume_df):
            futures_volume_df = futures_volume_df.pivot_table(index="symbol", aggfunc={"futures_volume":"sum"})

        # 2. 获取现货/全仓/杠杆仓位数量
        spot_volume_lst = []
        for account_type, accounts in self.oms.accounts.items():
            if account_type == "futures":
                continue
            for vt_accountid, account_obj in accounts.items():  # vt_accountid: 'BINANCE.DODO'
                # _1, _2 = vt_accountid.split(".")
                # if _1 == "BINANCES": # BNB/USDT会出现在oms.accounts中 (这些是合约的余额, 需要剔除掉)
                #     continue
                asset_name = account_obj.accountid  # accountid: 'DODO'
                symbol = f"{asset_name}USDT"
                spot_volume = account_obj.balance # balance:总数量; frozen:被冻结的数量
                borrowed = account_obj.borrowed
                d = {
                    "symbol" : symbol, "spot_volume" : spot_volume, "borrowed":borrowed
                }
                spot_volume_lst.append(d)
        spot_volume_df = pd.DataFrame(spot_volume_lst)
        spot_volume_df = spot_volume_df.pivot_table(index="symbol", aggfunc={"spot_volume":"sum", "borrowed":"sum"})
        spot_volume_df = spot_volume_df.reset_index()

        # 3. 汇总
        if len(futures_volume_df):
            volume_df = pd.merge(futures_volume_df, spot_volume_df, on="symbol", how="left")
            volume_df = pd.merge(volume_df, futures_last_price_df, on="symbol", how="left")
            volume_df = volume_df.fillna(0) # 空值用0来填充
            volume_df["合约市值"] = volume_df["futures_volume"] * volume_df["price"]
            total_marketValue = abs(volume_df["合约市值"].sum())
            volume_df["持仓占比"] = abs(volume_df["合约市值"] / total_marketValue)
            volume_df["持仓占比"] = volume_df["持仓占比"].apply(lambda x: f"{x:.1%}")
            volume_df["期现-数量差"] = volume_df["futures_volume"] + volume_df["spot_volume"]
            volume_df["期现-价值差"] = volume_df["期现-数量差"] * volume_df["price"]

            # 4.可视化处理
            volume_df = volume_df.sort_values("合约市值", ascending=True)
            volume_df = volume_df.rename(columns={
                "symbol":"币种", "futures_volume":"合约数量", "spot_volume":"现货数量", "price":"价格", "funding_rate":"资金费率"
            })
            ordered_field_lst = [
                "币种", "期现-数量差", "期现-价值差", "合约市值", "持仓占比", "资金费率", "价格", "现货数量", "合约数量"
            ]
            volume_df  = sort_df(volume_df, ordered_field_lst)
            volume_df = volume_df.apply(_round_num, axis=1)
            volume_df = volume_df.reset_index(drop=True) # 重建自然索引: (sort_values会打乱自然索引)
            return volume_df
        else:
            print("合约貌似没有持仓...")
            l = [
                {"合约市值":0, "持仓占比":"0%", "资金费率":"0%"},
            ]
            volume_df = pd.DataFrame(l)
            return volume_df


class ShowModlue():
    def __init__(self, main_engine, client):
        """
            notes:
                - 展示模块
        """
        # 1. 初始化vnpy中的组件
        self.main_engine = main_engine
        self.oms = main_engine.engines["oms"]
        self.Client = client

        # 2. 初始化SC.Show中所需变量
            # 子线程控制的开关
        self.alive_main_print = False

    def show_futures_index(self):
        """
        function: 获取合约账户的 4个核心爆仓指标
            1. margin_rate (维持保证金率): 最真实反映'爆仓紧张程度' (达到100%就一定会爆仓的!!)
                    公式1: '维持保证金数' / '保证金余额'
            2. pnl_rate (实际浮盈率): 看合约账户的实际盈亏情况...  (币安显示的ROE没啥用...)
                    公式2: '未实现盈亏' / '钱包余额'
                            (注意: 实际浮盈率还没达到-100%就会爆仓,)
                            (因为有维持保证金的存在, 亏到只剩维持保证金就算爆仓了..)
            3. open_leverage (开仓杠杆倍数): 可以真实地感受当前的市值到底开了多少倍杠杆
                    公式3: '开仓名义市值的总和' / '钱包余额'
                            (多币种后, 对杠杆的概念比较模糊... 一定要强化! 因为风险一定要控制在自己能接受的范围... )
                            ('概念模糊'就是非常'不可控的', 对于实盘投资来说非常危险...)
            4. notional_pnl_rate (名义浮盈率): 从开仓开始, 了解币价整体的波动率情况
                    公式4: '未实现盈亏' / '开仓名义市值的总和'
                            (区别于'实际浮盈率'反映的是个人账面的财务状况, '名义浮盈率'反映的是开仓到现在币价的涨跌情况)

        notes:
            1. 合约账户里的usdt账户的balance, 是可以由 trade_ws_api 动态地在oms_engine中更新余额 (实时监听事件, 更新余额)
                - 只有usdt的钱包余额是会监听事件动态更新的, 其他相关数据都有可能存在误差...
                - 解决方案: 在监听到这个事件后的回调函数中, 调用 self.gateway.rest_api.query_account()访问最新的account数据...
                        (但是有个问题, 这样会导致频繁请求req, io密集阻塞?? 在套利策略中极度影响执行速度!!)
                        (算了, 还是先不请求吧, 这个数据的更新有点延迟也影响不大... 真的需要使用该数据的时候,重新用rest_api请求就可以了)
            2. 但是合约账户里的usdt的'维持保证金'和'保证金余额'并不会由 trade_ws_api监听, 这就意味着当前数据有可能旧数据, 需要用过rest_api再请求一遍

        todo:
            - 这么重要且宏观的数据, 以后可以每隔1分钟打印一次...
                (也能监控这个数据是否有变化...  防止数据不更新, 我还傻傻以为不会爆仓...)
        """
        self.Data._live_update_margin_rate()
        futures_index = self.Data.futures_index
        volume_df = self.Risk.check_match() # 各币种仓位'配平检查'的df
        hedge_marketValue = abs(sum(volume_df["合约市值"])) # 对冲市值

        marginBalance = futures_index.get("marginBalance") # 保证金余额 (usdt钱包余额+浮盈)
        maintMargin = futures_index.get("maintMargin") # 维持保证金
        margin_rate = futures_index.get("margin_rate") # 维持保证金率
        pnl = futures_index.get("pnl") # 未实现盈亏
        usdt_balance = futures_index.get("usdt_balance") # USDT钱包余额
        availableBalance = futures_index.get("availableBalance") # 可用划转余额
        if hedge_marketValue == 0:
            futures_lever = 0
            supported_max_increase = 0
        else:
            futures_lever = hedge_marketValue / marginBalance # 合约杠杆倍数
            supported_max_increase = ((marginBalance - maintMargin) / hedge_marketValue) # 合约爆仓涨幅
        txt =f"""
            < {self.Client.account_name} >
    ========================
    1.【维持保证金率---爆仓率】: 【{margin_rate:.2%}】
    2.【合约杠杆倍数】: {futures_lever:.2f}
    3.【合约爆仓涨幅】: {supported_max_increase:.2%}
    4.【对冲市值】: {hedge_marketValue:.2f}
    5.【总本金】: 【{0:.2%} 】 # 待完善 (需要获取杠杆账户中的各币种余额)
    6.【对冲杠杆】: 【{0:.2%} 】
    -----------------------
    保证金余额 : {marginBalance:.2f}
    维持保证金 : {maintMargin:.2f}
    未实现盈亏 : {pnl:.2f}
    USDT钱包余额 : {usdt_balance:.2f}
    可用划转余额 : {availableBalance:.2f}
    ========================
    时间戳: {datetime.now()}
        """
        logger.log(20, txt)
        return txt

    def _check_pair_pos(self, pair_name):
        """
            function: 核对pair的'对冲账户是否数量匹配'
            args:
                - pair_dict: self.pairs[pair_name] 得到的那个dict
            notes: - 一般用在 show_my_pairs 中, 不单独对外使用
        """
        # 初始核验
        (pair_name, exchange_name, symbol, asset_name) = self.Data._split_pair_name(pair_name=pair_name)
        # 核验余额
            # i. 该币种的现货余额
        symbol_account = self.oms.accounts.get("spot").get(f"{exchange_name}.{asset_name}") # 这里是ETH不是LUNAUSDT, 所以把后面4个字符删掉
        if symbol_account:
            spot_balance = symbol_account.balance
        else:
            spot_balance = 0 # 如果oms中没有该account, 则为0
            # ii. 该币种的合约持仓
        symbol_position = self.oms.positions.get(f"{symbol}.{exchange_name}.空")
        if symbol_position:
            futures_volume = symbol_position.volume
        else:
            futures_volume = 0 # 如果oms中没有该position, 则为0
            # iii. 现货和合约的volume总和  (做空的合约的volume为负数)
        spot_price = self.Data.get_last_price(pair_name=pair_name, type="spot")
        futures_price = self.Data.get_last_price(pair_name=pair_name, type="futures")
        spot_marketValue = spot_balance * spot_price # 现货市值
        futures_marketValue = futures_volume * futures_price # 合约市值 (空单为负)
        delta_amount = spot_balance + futures_volume # 期现净持仓量
        delta_marketValue = delta_amount * futures_price
        abs_sum_marketValue = spot_marketValue + abs(futures_marketValue) # 期现总市值
        d = {
            "spot_balance" : spot_balance,
            "futures_volume" : futures_volume,
            "spot_price" : spot_price,
            "futures_price" : futures_price,
            "spot_marketValue" : spot_marketValue,
            "futures_marketValue" : futures_marketValue,
            "delta_amount" : delta_amount, # # 期现净持仓量 (是否'期现双边配平', 就看这个值)
            "delta_marketValue" : delta_marketValue, # # 期现净持仓量 (是否'期现双边配平', 就看这个值)
            "abs_sum_marketValue" : abs_sum_marketValue,
        }
        return d

    def show_my_pairs(self, type="df"):
        """
            function: 打印self.pairs中的每个币种的'对冲账户是否数量匹配'
            args:
                type:
                    - "dict"
                    - "df"
            return: 每个pair的sum_volume相关信息
        """
        # 核对所有我的持仓的期现volume是否相等
        all_d = {}
        pair_lst = self.Data.get_my_pair_lst()
        total_futures_marketValue = 0
        for pair_name in pair_lst:
            d = self.Show._check_pair_pos(pair_name=pair_name)
            all_d.update({pair_name:d})
            total_futures_marketValue += abs(d.get("futures_marketValue")) # 累加每个币种的合约市值
        for pair_name, d in all_d.items():
            futures_marketValue = d.get("futures_marketValue")
            marketValue_percentage = abs(futures_marketValue) / total_futures_marketValue
            d.update({"marketValue_percentage" : marketValue_percentage}) # 每个合约持仓的市值占比
        if type == "dict":
            return all_d
        elif type == "df":
            df = pd.DataFrame(all_d)
            return df

    def show_pairs_df(self):
        "[弃用].. 没啥用了...用df的形式展示 pairs的信息"
        pairs_df = pd.DataFrame(self.Data.pairs)
        return pairs_df

    def req_mytrade(self, pair_name="BINANCE.LUNAUSDT", type="spot", df_type="1", start_time="today", end_time="now", direction=None):
        """
            function:
                - 请求历史成交记录, 复盘实际成交的价差率如何...
            args:
                - is_original: True/False  # 是否需要返回new_df, 还是过滤了不重要列的 _df
                - df_type: df的类型(根据df处理的顺序来决定):
                    - 1: 透视后的df
                    - 2: 透视表与原表联结的df (所有原字段)
                    - 3: 透视表与原表联结的df (挑选部分重要字段)
                - start_time/end_time: "today"/"2021-03-30"   # 选择一个时间段的数据生成df
                - direction: "BUY"/"SELL"/None    # 筛选不同买卖方向的df (None则不区分'买卖方向')

            usage:
                eg1:
                    symbol = "DENTUSDT"
                    s_df = sc.req_mytrade(symbol=symbol, type="spot", start_time="today", end_time="now", is_original=False, direction="BUY")
                    f_df = sc.req_mytrade(symbol=symbol, type="futures", start_time="today", end_time="now", is_original=False, direction="SELL")
                    sc.cal_avg_price(f_df) / sc.cal_avg_price(s_df)

        """

        # 1. 构造req对象, 并发送请求
        (pair_name, exchange_name, symbol, asset_name) = self.Data._split_pair_name(pair_name=pair_name)
        req = MyTradesRequest(symbol=symbol.lower(), exchange=Exchange[exchange_name])
        if type == "spot":
            mytrade_dict = self.Client.spot_rest_api.query_myTrades(req)
        elif type == "futures":
            mytrade_dict = self.Client.futures_rest_api.query_myTrades(req)
        else:
            return
        # 2. 处理response数据, 转变成'目标df'
        df = pd.DataFrame(mytrade_dict)
        if len(df) == 0:
            msg = f"没有 {symbol} 的相关交易记录... 请检查是否有发生过交易.."
            raise Exception(msg)
            # df默认的时区是'naive'(即:没有时区)
            # 这里需要先定义当前的时间戳是哪个时区, 然后需要转换成哪个时区...
            # 目前df整列换时区唯一的解决办法:
        # df["time"] = pd.to_datetime(df["time"], unit="ms") + pd.to_timedelta("8h") # utc改成北京时间
        df["time"] = pd.to_datetime(df['time'], unit="ms").dt.tz_localize('UTC').dt.tz_convert('hongkong') # 转化成东八区的时间
        # df = df[df["time"] >= get_timestamp(query_date)] # 应该改成'可选区间', 而不是'仅大于'... (写成query_set的方式可以实现)(设置起止日期)
        # query_df = s_df.query(f"time>'{get_timestamp(query_date)}'")
        # df = df.iloc[query_df.index]
        # query_df = df.query(f"'{get_timestamp('2021-04-16 7:00:00')}'<time<'{get_timestamp('2021-04-16 8:00:02')}'")
        df = df.query(f"'{get_timestamp(start_time)}'<=time<='{get_timestamp(end_time)}'")
        if type == "spot":
            df[['price', 'qty', 'quoteQty', 'commission']] = df[['price','qty', 'quoteQty', 'commission']].apply(pd.to_numeric)
            if direction == "BUY":
                df = df[df["isBuyer"]==True]
            elif direction == "SELL":
                df = df[df["isBuyer"]==False]
            # 如果direction不指定"BUY"or"SELL", 那么就不会进行筛选, 原df输出
        elif type == "futures":
            df[['price', 'qty', 'quoteQty', 'commission', 'realizedPnl']] = df[['price','qty', 'quoteQty', 'commission', 'realizedPnl']].apply(pd.to_numeric)
            if direction == "BUY":
                df = df[df["buyer"]==True]
            elif direction == "SELL":
                df = df[df["buyer"]==False]
            # 如果direction不指定"BUY"or"SELL", 那么就不会进行筛选, 原df输出
        else:
            raise Exception("没有此type...")

        if len(df) == 0:
            msg = f"日期筛选后的 mytrade_df 为空...检查交易时间或者direction..."
            raise Exception(msg)
        tmp_df = df.pivot_table(index="orderId", aggfunc={"qty":"sum", "quoteQty":"sum"})
        tmp_df["avg_price"] = tmp_df["quoteQty"] / tmp_df["qty"]
        tmp_df.rename(columns={"qty":"order_qty", "quoteQty":"order_quoteQty", "avg_price":"order_avg_price"}, inplace=True)
        tmp_df = tmp_df.reset_index() # 使用自然数作为索引, 把orderId右移变成'列'
        if type == "spot":
            time_df = df[["orderId", "time", "isBuyer", "isMaker"]].drop_duplicates("orderId") # 只有orderId列和time列的df
        elif type == "futures":
            time_df = df[["orderId", "time", "buyer", "maker", "positionSide"]].drop_duplicates("orderId") # 只有orderId列和time列的df
        tmp_df = pd.merge(tmp_df, time_df, how="left", on="orderId")
        if df_type == "1":
            return tmp_df
        elif df_type == "2":
            return df

    def _drop_useless_trades(self, s_df, f_df):
        """
            [方法二]
            functions: 将单腿下单的交易剔除 (这部分不能用于计算价差率...)
        """
        i = 0
        while True:
            s_order_qty = s_df["order_qty"].iloc[i]
            f_order_qty = f_df["order_qty"].iloc[i]
            print(f"当前的i:{i}; s:{s_order_qty}, f:{f_order_qty}")
            # 如果两个队列的第一顺位的值不相等
                # ([坑点]: python浮点精度问题, 导致不能直接判断是否相等...)
                # 解决方案:
                    # 1. decimal库: 计算效率很低, 比正常的python运算耗时多30倍.... 不建议用
                    # 2. 用相减的绝对值小于某个极小的数
            is_equal = abs(s_order_qty - f_order_qty) < 0.0000000001
            if not is_equal:
                print("111")
                if len(s_df) > len(f_df):
                    print("333")
                    s_df.drop(s_df.iloc[i].name, inplace=True)
                elif len(s_df) < len(f_df):
                    print("444")
                    f_df.drop(f_df.iloc[i].name, inplace=True)
                elif len(s_df) == len(f_df):
                    # 如果不是最后一个数字  (因为最后一个数字不能+1取索引)
                    print("555")
                    if i < (len(s_df) - 1):
                        if s_df["order_qty"].iloc[i] == f_df["order_qty"].iloc[i+1]:
                            f_df.drop(f_df.iloc[i].name, inplace=True)
                        elif s_df["order_qty"].iloc[i+1] == f_df["order_qty"].iloc[i]:
                            s_df.drop(s_df.iloc[i].name, inplace=True)
                        # 如果两个'交叉'都不匹配... 那就两个数字都删掉...
                        else:
                            f_df.drop(f_df.iloc[i].name, inplace=True)
                            s_df.drop(s_df.iloc[i].name, inplace=True)
                            i -= 1 # 两个都删掉, 此时不能再让i自增了
                    # 如果是最后一个数字  (两个都删掉...)
                    else:
                        f_df.drop(f_df.iloc[i].name, inplace=True)
                        s_df.drop(s_df.iloc[i].name, inplace=True)
            # 如果两个队列的第一顺位的值相等, 则i自增1
            elif is_equal:
                i += 1
                print("222")
            min_length = min(len(s_df), len(f_df))
            if i >= min_length:
                print("999")
                break
        # 前面drop会把某些索引删掉,造成自然数跳空问题.. (重置自然数索引)
        s_df = s_df.reset_index().drop(columns="index")
        f_df = f_df.reset_index().drop(columns="index")
        return (s_df[:min_length], f_df[:min_length])

    def show_trade(self, pair_name="BINANCE.LUNAUSDT", offset="OPEN", start_time="today", end_time="now"):
        # 1. 请求获得现货/合约的 trade_df (每笔交易数据)
        if offset == "OPEN":
                # i. 现货的'买入'trade
            s_df = self.Show.req_mytrade(pair_name=pair_name, type="spot", start_time=start_time, end_time=end_time, df_type="1", direction="BUY")
                # ii. 合约的'卖出'trade
            f_df = self.Show.req_mytrade(pair_name=pair_name, type="futures", start_time=start_time, end_time=end_time, df_type="1", direction="SELL")
        elif offset == "CLOSE":
                # i. 现货的'卖出'trade
            s_df = self.Show.req_mytrade(pair_name=pair_name, type="spot", start_time=start_time, end_time=end_time, df_type="1", direction="SELL")
                # ii. 合约的'买入'trade
            f_df = self.Show.req_mytrade(pair_name=pair_name, type="futures", start_time=start_time, end_time=end_time, df_type="1", direction="BUY")
        else:
            raise Exception("没有此offset...")

        # 2. 匹配df的行数 (现货合约的行数要保持一致!! 剔除非双腿开单的交易)
        s_df, f_df = self._drop_useless_trades(s_df=s_df, f_df=f_df)

        # 3. 计算每笔trade的价差率
        spread_rate_arr = (f_df["order_avg_price"] / s_df["order_avg_price"]) - 1
        spread_rate_arr = spread_rate_arr.apply(lambda x: f"{x:.4%}") # 用带有百分比的str表示
        qty_rate_arr = f_df["order_qty"].values / s_df["order_qty"].values # 用来验证这笔交易中'现货'和'合约'是否是配平的... (值为1表示正常)
        order_qty_arr = f_df["order_qty"].values
        futures_time_arr = f_df["time"].dt.strftime("%m-%d %X.%f")
        spot_time_arr = s_df["time"].dt.strftime("%m-%d %X.%f")
        s_minus_f = (s_df["time"] - f_df["time"]).dt.total_seconds()
        df = pd.DataFrame({
                "qty_rate":qty_rate_arr,
                "order_qty":order_qty_arr,
                "spread_rate":spread_rate_arr,
                "futures_time":futures_time_arr,
                "spot_time":spot_time_arr,
                "s_minus_f":s_minus_f,
            })
        return df

    def show_trades(self, pair_lst=["BINACE.LUNAUSDT"], offset="OPEN", start_time="today", end_time="now"):
        self.show_dict = {}
        for pair_name in pair_lst:
            df = self.Show.show_trade(pair_name=pair_name, offset=offset, start_time=start_time, end_time=end_time)
            spread_rate_arr = df["spread_rate"]
            spread_rate_arr = spread_rate_arr.apply(lambda x: float(x.strip("%"))/100) # 将百分比的str, 转成浮点数值
            avg_spread_rate = avg(spread_rate_arr, 5)
            self.show_dict.update({pair_name:(df, avg_spread_rate)})
        return self.show_dict

    def show_avg_price(self, df):
        "计算这个df中交易数据的平均价格"
        avg_price = df["quoteQty"].sum() / df["qty"].sum()
        return avg_price

    def main_print(self, sleep_time=1):
        """
            function: 打印所有订阅币种的 '资金费率', '开仓价差率', '平仓价差率' (已经排序) [子线程执行]
            args:
                sleep_time: 1/0.5  (可以选择打印的间隔时间...反正main_cal是每0.1s计算一次, 打印频次不超过它就可以了)
            note:
                - '主展示'函数 (1s打印一次)
                - 这是该类打印输出的最终形态, 所以采用最简洁的函数命名
                - 该函数实际上没有做任何计算, 只是用于打印...
                    (底层实际运算的是'print_spread_rate'函数, 打印的数据也是调用它计算的结果)
            todo:
                - '平仓价差率' 不应该是从小到大的简单排序... (应该考虑开仓时候的价差率)
        """
        def _recur_print(sleep_time):
            if self.alive_main_print == True:
                # 如果发现 self.alive_main_print 已经是True了, 说明可能之前的子线程还在运行中, 先将其关闭后再重新生成
                self.alive_main_print = False
                time.sleep(1)
            self.alive_main_print = True
            try:
                # 每秒打印 资金费率 and 开/平仓价差率
                while True:
                    if self.alive_main_print == False: # 可以用于杀死子线程
                        break
                    if len(self.Data.funding_rate_dict) > 1:
                        funding_rate_lst = sorted(self.Data.funding_rate_dict.items(), key=lambda x:x[1], reverse=True)
                        funding_rate_lst = [(pair[0], f"{pair[1]:.4%}") for pair in funding_rate_lst]
                    else:
                        funding_rate_lst = self.Data.funding_rate_dict
                    if len(self.Data.spread_rate_close_dict) > 1:
                        open_lst = sorted(self.Data.spread_rate_open_dict.items(), key=lambda x:x[1], reverse=True)
                        open_lst = [(pair[0], f"{pair[1]:.4%}") for pair in open_lst]
                        close_lst = sorted(self.Data.spread_rate_close_dict.items(), key=lambda x:x[1], reverse=False)
                        close_lst = [(pair[0], f"{pair[1]:.4%}") for pair in close_lst]
                    else:
                        open_lst = self.Data.spread_rate_open_dict
                        close_lst = self.Data.spread_rate_close_dict
                    print(f"资金费率: {funding_rate_lst}")
                    print(f"开仓价差率: {open_lst}")
                    print(f"平仓价差率: {close_lst}", "\n")
                    time.sleep(sleep_time)
                self.alive_main_print = False
            except Exception as e:
                self.alive_main_print = False
                raise Exception(e)

        t = threading.Thread(target=_recur_print, kwargs=({'sleep_time':sleep_time}))
        t.start()

    def stop_print(self):
        # 把该main_print函数杀死.. (其实就是让main_print函数退出循环)
        # (要想main_print继续运行, 可以执行 self.Show.main_print()函数;)
        self.alive_main_print = False

    def active(self):
        self.Show.main_print()

    def robot_print(self, robot):
        """
            functions: 打印robot上运行的币对的价差率信息... (简洁打印...)
        """

        def _recur_robot_print(robot):
            # 初始化
            (pair_name, exchange_name, symbol, asset_name) = self.Data._split_pair_name(pair_name=robot._pair_name)
            offset = robot._offset
            spot_lock = None # 初始化一个spot_lock.(当作'锁'?)
            futures_lock = None # 初始化一个spot_lock.(当作'锁'?)

            try:
                while True:
                    # robot的 'alive'和'to_print'变量都决定该子线程的生死
                    if (robot.alive == False) or (robot.to_print == False):
                        break

                    if offset == "OPEN":
                        # 通过main_cal计算的结果, 直接取数
                        spread_rate_open = self.Data.spread_rate_open_dict.get(asset_name)
                        # 分流打印
                        if spread_rate_open < 0.0023:
                            if spot_lock != '0':
                                logger.log(20, f'[{symbol} - 开仓]: 价差率在一个无聊的区间...')
                                spot_lock = '0'
                        elif 0.0023 <= spread_rate_open < 0.003:
                            if spot_lock != '1':
                                logger.log(20, f'[{symbol} - 开仓]: 价差率区间: [0.23% 至 0.30%]   ({round(spread_rate_open*100, 4)}%)')
                                spot_lock = '1'
                        elif 0.0030 <= spread_rate_open < 0.0035:
                            if spot_lock != '2':
                                logger.log(20, f'[{symbol} - 开仓]: 价差率区间: [0.30% 至 0.35%]   ({round(spread_rate_open*100, 4)}%)')
                                spot_lock = '2'
                        elif 0.0035 <= spread_rate_open < 0.0040:
                            if spot_lock != '3':
                                logger.log(20, f'[{symbol} - 开仓]: 价差率区间: [0.35% 至 0.40%]   ({round(spread_rate_open*100, 4)}%)')
                                spot_lock = '3'
                        elif 0.0040 <= spread_rate_open < 0.0045:
                            if spot_lock != '4':
                                logger.log(20, f'[{symbol} - 开仓]: 价差率区间: [0.40% 至 0.45%]   ({round(spread_rate_open*100, 4)}%)')
                                spot_lock = '4'
                        elif 0.0045 <= spread_rate_open < 0.0050:
                            if spot_lock != '5':
                                logger.log(20, f'[{symbol} - 开仓]: 价差率区间: [0.45% 至 0.50%]   ({round(spread_rate_open*100, 4)}%)')
                                spot_lock = '5'
                        else:
                            if spot_lock != '6':
                                logger.log(20, f'[{symbol} - 开仓]: 价差率区间: [ >= 0.50% ]   ({round(spread_rate_open*100, 4)}%)')
                                spot_lock = '6'

                    elif offset == "CLOSE":
                        # 通过main_cal计算的结果, 直接取数
                        spread_rate_close = self.Data.spread_rate_close_dict.get(asset_name)
                        # 分流打印
                        if 0.0030 <= spread_rate_close:
                            if futures_lock != '0':
                                logger.log(20, f'[{symbol} - 平仓]: 价差率在一个无聊的区间...')
                                futures_lock = '0'
                        elif 0.0020 <= spread_rate_close < 0.003:
                            if futures_lock != '1':
                                logger.log(20, f'[{symbol} - 平仓]: 价差率区间: [0.20% 至 0.30%]   ({round(spread_rate_close*100, 4)}%)')
                                futures_lock = '1'
                        elif 0.0010 <= spread_rate_close < 0.0020:
                            if futures_lock != '2':
                                logger.log(20, f'[{symbol} - 平仓]: 价差率区间: [0.10% 至 0.20%]   ({round(spread_rate_close*100, 4)}%)')
                                futures_lock = '2'
                        elif 0.0005 <= spread_rate_close < 0.0010:
                            if futures_lock != '3':
                                logger.log(20, f'[{symbol} - 平仓]: 价差率区间: [0.05% 至 0.10%]   ({round(spread_rate_close*100, 4)}%)')
                                futures_lock = '3'
                        elif 0.0000 <= spread_rate_close < 0.0005:
                            if futures_lock != '4':
                                logger.log(20, f'[{symbol} - 平仓]: 价差率区间: [0.00% 至 0.05%]   ({round(spread_rate_close*100, 4)}%)')
                                futures_lock = '4'
                        elif -0.0005 <= spread_rate_close < 0.0000:
                            if futures_lock != '5':
                                logger.log(20, f'[{symbol} - 平仓]: 价差率区间: [-0.05% 至 0.00%]   ({round(spread_rate_close*100, 4)}%)')
                                futures_lock = '5'
                        elif -0.0010 <= spread_rate_close < 0.0005:
                            if futures_lock != '5':
                                logger.log(20, f'[{symbol} - 平仓]: 价差率区间: [-0.10% 至 -0.05%]   ({round(spread_rate_close*100, 4)}%)')
                                futures_lock = '5'
                        else:
                            if futures_lock != '6':
                                logger.log(20, f'[{symbol} - 平仓]: 价差率区间: [ < -0.10% ]   ({round(spread_rate_close*100, 4)}%)')
                                futures_lock = '6'
                    # 休眠1秒 (所以robot_print的打印频次最快是1s) (因为lock的原因, 实际打印频次更低)
                    time.sleep(1)
                # 若退出循环后, 这个属性也要改为False
                self.to_print = False

            except Exception as e:
                self.to_print = False
                raise Exception(e)

        t = threading.Thread(target=_recur_robot_print, kwargs=({'robot':robot}))
        t.start()

    def show_income(self, income_type="FUNDING_FEE", start_time=None, end_time=None):
        """
            function: 获取合约账户资金流水的记录
            args:
                income_type:  "TRANSFER"，"WELCOME_BONUS", "REALIZED_PNL"，"FUNDING_FEE", "COMMISSION", and "INSURANCE_CLEAR"
                start_date/end_time: 币安接口中的startTime必须是 'ms'为单位的int型 (eg: 1234567890123)
        """
        def on_show_income(data, request):
            """
                function: 展示资金费用收入
                args:
                    last: True/False  (设置为True, 则展示最近8小时的资金费用收入...)
                    start_date/end_time: 字符串表示的时间  ("2021-03-12 08:03:33")
            """
            df = pd.DataFrame(data)
            df["time"] = pd.to_datetime(df['time'], unit="ms").dt.tz_localize('UTC').dt.tz_convert('hongkong') # 转化成东八区的时间
            start_time = get_timestamp("now") - get_timedelta("8h") # 也就是开始时间是8小时前
            # query_df = df.query(f"'{get_timestamp('2021-04-16 7:00:00')}'<time<'{get_timestamp('2021-04-16 8:00:02')}'")
            query_df = df.query(f"'{get_timestamp(start_time)}'<=time<='{get_timestamp('now')}'")
            query_df[['income']] = query_df[['income']].apply(pd.to_numeric)
            print(query_df)
            print(query_df['income'].sum())

        # 构造需要发送的参数
            # 1. 是否需要签名
        from vnpy.gateway.binances.binances_gateway import Security
        data = {"security": Security.SIGNED} # 需要发送数字签名
            # 2. 该API必须传入的参数
        params = {
            "incomeType" : income_type,
            "limit" : 1000,
        }
        #     # 币安接口中的startTime必须是 'ms'为单位的int型 (eg: 1234567890123)
        # start_time = start_time if start_time else int(get_timestamp("today").timestamp()*1000)  # 如果没有传入start_time, 则用今天0点的时间戳传入
        # end_time = end_time if end_time else int(get_timestamp("now").timestamp()*1000)  # 如果没有传入end_time, 则用当前的时间戳传入
        if start_time:
            params.update({"startTime":start_time})
        if end_time:
            params.update({"endTime":end_time})
            # 3. 构造req并发送 (通过add_request()函数发送请求)
        self.Client.futures_rest_api.add_request(
            method="GET",
            path="/fapi/v1/income",
            callback=on_show_income,
            data=data,
            params=params,
        )

    def show_funding_rate(self):
        "获取所有币种平均的资金费率 (对'跨期套利'问题做简单处理)"
        volume_df = self.Risk.check_match()
        print(volume_df)
        volume_df["持仓占比"] = volume_df["持仓占比"].apply(lambda x: float(x[:-1])/100)
        volume_df["资金费率"] = volume_df["资金费率"].apply(lambda x: float(x[:-1])/100)
            # 当合约账户中存在跨期套利, 就需要用到这种妥协的解决办法...
        if round(volume_df["持仓占比"].sum(), 2) != 1:
            volume_df["持仓占比"] = volume_df["持仓占比"] / volume_df["持仓占比"].sum()
        avg_funding_rate = sum(volume_df["持仓占比"] * volume_df["资金费率"])
        print(f"全币种的平均资金费率为: {avg_funding_rate: .3%}")


class TradeModule():
    """
        notes:
            - 针对'期现是否配平'问题, 使用了两层检测, 确保开仓正确无误!! (不会在'未平'情况下仍然疯狂开仓)
                1. 开仓前: 调用 _recur_check_is_matched() 函数, 来确保当前期现的'市值差'是小于50u的
                2. 开仓后: 如果 现货/合约 的order状态没有更新成 "完全成交", 则表示网络出现延迟, 下单可能被拒绝, 则停止继续下单
                            (避免'期现-数量差'进一步拉大)
    """

    def __init__(self, main_engine, client):
        """
            notes:
                - 交易模块
        """
        # 1. 初始化vnpy中的组件
        self.main_engine = main_engine
        self.oms = main_engine.engines["oms"]
        self.Client = client

        # 2. 初始化SC.Trade中所需变量
        pass

    def _check_balance(self, pair_name, volume, offset):
        """

            function: 核对本账户是否有足够的仓位.. (但是...合适的价差率转瞬即逝...你确定要在每次下单前还在先req一下position嘛....)
                    解决: 本地来管理这个pos, 这样不会浪费太多时间...
                    解决2: 压根不需要重新req呀.....我的trade_ws_api实时更新这个pos状态, 直接去oms.position取值就好了....
                    为了防止一边开仓, 另一边余额不够开不了仓的情况发生, 最好还是取值判断一下...

            args:
                - volume: 准备去交易的币种数量.. (本函数就是用于核对是否有足够的usdt来购买这些volume)
                - offset: "OPEN"/"CLOSE"  (开仓或者平仓的check方式不太一样, 所以一定要有这个参数...)
            notes:
                - **(volume是指币种数量, qty是指usdt数量)
                - 用volume形容合约的持仓, 用balance形容现货的余额
                - 用于'双边下单'时候的余额核验.. (当其中一边余额不足时, 另一边也禁止下单)
                    (而对于'单边下单'场景, 不需要通过该函数核验)
        """
        # 0. 初始校验
        (pair_name, exchange_name, symbol, asset_name) = self.Data._split_pair_name(pair_name=pair_name)

        # 1. 查询当前币种的最新价格
        last_price_spot = self.Data.get_last_price(pair_name=pair_name, type="spot")
        last_price_futures = self.Data.get_last_price(pair_name=pair_name, type="futures")

        # 2. 计算当前待开仓的qty **(volume是指币种数量, qty是指usdt数量)
            # 过滤器-最小名义市值
        self.Trade._filter_min_notional(pair_name=pair_name, volume=volume)


        # 3. 核验是否满足'下单条件'
        if offset == "OPEN":
            # 1. 查询当前余额
                # i. 现货USDT可用余额
                    # // 这里的取值不能取balance!!! 必须是非冻结的余额!! [坑点]: 已存在的委托挂单会让可用余额变少!!! (导致不能顺利开仓)
            _ = self.oms.accounts.get("spot")[f"{exchange_name}.USDT"] # 目前只有在现货下单, 所以这里暂时只有现货 (以后如果实现在全仓下单, 就还需要优化)
            usdt_available_balance_spot = _.balance - _.frozen # 相减后才是实际的USDT'可用余额'
                # ii. 合约USDT可用余额 (即: 钱包余额) (即: 最真实的保证金, 不考虑合约的浮盈浮亏!!)
            usdt_available_balance_futures = self.Data.futures_index.get("availableBalance")

            # 2. 计算最大支持的交易volume
            supported_volume_spot = usdt_available_balance_spot // (last_price_spot * 1.03) # 预留3%的余量..确保价格剧烈波动中也一定能买入!
            supported_volume_futures = usdt_available_balance_futures // (last_price_futures * 1.03) # 预留3%的余量..确保价格剧烈波动中也一定能买入!
            msg = f"现货-USDT余额: {usdt_available_balance_spot:.1f};  合约-可用划转USDT余额: {usdt_available_balance_futures:.1f}"
            logger.log(30, msg)
            msg = f"现货最大交易量:{supported_volume_spot}个币;  合约最大交易量:{supported_volume_futures}个币; (当前开仓volume:{volume}, 最新价:{last_price_futures})"
            logger.log(30, msg)

            # 3. 判断是否能够买入
            if supported_volume_spot < volume:
                msg = f"############## 现货USDT: {usdt_available_balance_spot}USDT, 不足买入 {volume}个 {asset_name}现货!!!  [无法交易]\n"
                raise Exception(msg)
            if supported_volume_futures < volume:
                msg = f"############## 合约可用余额: {supported_volume_futures}USDT, 不足开仓 {volume}个 {asset_name}合约!!!  [无法交易]\n"
                raise Exception(msg)
            msg = f"============== 余额检测通过!!  [允许交易]\n"
            logger.log(30, msg)
            return volume

        elif offset == "CLOSE":
            # 1. 查询当前余额
            try:
                # i. 该币种的现货余额
                    # // 这里的取值不能取balance!!! 必须是非冻结的余额!! [坑点]: 已存在的委托挂单会让可用余额变少!!! (导致不能顺利开仓)
                _ = self.oms.accounts.get("spot")[f"{exchange_name}.{asset_name}"] # 目前只有在现货下单, 所以这里暂时只有现货 (以后如果实现在全仓下单, 就还需要优化)
                symbol_spot_balance = _.balance - _.frozen
            except:
                raise Exception(f"没有{asset_name}的现货'可用余额'...")
                # ii. 该币种的合约持仓数量
            try:
                if self.oms.positionSide == "DOUBLE":
                    symbol_futures_volume = self.oms.positions[f"{symbol}.{exchange_name}.空"].volume # volume用负数来表示正负的仓位
                elif self.oms.positionSide == "SINGLE":
                    symbol_futures_volume = self.oms.positions[f"{symbol}.{exchange_name}.单向模式"].volume # volume用负数来表示正负的仓位
            except:
                raise Exception(f"没有{asset_name}的空单持仓...")
            # 最大支持的可平的volume
            max_supported_volume = min(symbol_spot_balance, abs(symbol_futures_volume))
            if volume > max_supported_volume:
                print(f"现货'可用余额'数量: {symbol_spot_balance}")
                print(f"合约'可用余额'数量: {symbol_futures_volume}")
                # 这里修改为'最大支持的volume'的目的: 让少于1单位 multiplier的仓位能够全部平仓...
                logger.log(30, f"现货或合约的'可用余额'已经小于'此次交易命令的交易数量': {volume}, 将实际交易volume改为最大支持的volume: {max_supported_volume}")
                volume = max_supported_volume

                # 过滤器-订单数量精度
                volume = self.Trade._filter_lot_size(pair_name=pair_name, volume=volume)
                # 过滤器-最小名义市值
                self.Trade._filter_min_notional(pair_name=pair_name, volume=volume)

                # # 1.保留有效数字: 在最高位向后保留3位数 (即: 123456.123保留成 123000; 0.00123456保留成0.00123)
                # volume = round(volume, -math.floor(math.log10(volume))+2) # 前面是负号, 并在最高位数基础上保留2位数
                #
                # # 2. 最小精度问题: 查询self.oms.contracts中的最小volume精度, 避免volume精度过高超过官方支持而报错...
                #     # 一般来说现货支持更高的精度, 而合约的最小支持精度比现货低一级 (即: 现货可以交易1.23个币, 而合约只能交易1.2个币)
                # spot_precision = self.oms.contracts.get(f"{symbol.lower()}.{exchange_name}", {}).min_volume
                # futures_precision = self.oms.contracts.get(f"{symbol.upper()}.{exchange_name}", {}).min_volume
                # min_volume = max(spot_precision, futures_precision) # 取更大(更粗略)的那一个精度
                # supported_deal_count = round(volume / min_volume) * min_volume
                # supported_deal_count = round(supported_deal_count, 10) # 上面的计算中可能出现'python浮点精度问题', 所以这里必须再做一次round
                # if (volume != 0) and (supported_deal_count == 0):
                #     raise Exception("######## 最小精度问题, 导致计算出来的volume为0!!!")
                # else:
                #     volume = supported_deal_count
                #
                # # 3. 最小交易额问题: 修改volume后, 再核对下是否满足平台最小交易额 10u
                # qty_spot = last_price_spot * volume
                # qty_futures = last_price_futures * volume
                # if (qty_spot <= 10) or (qty_futures <= 10):
                #     msg = f"[{symbol}-不满足最低交易额] 待交易现货qty : {qty_spot}; 待交易合约qty : {qty_futures}"
                #     raise Exception(msg)

            # 2. 计算最大支持的交易volume
            msg = f"现货-{asset_name}余额: {symbol_spot_balance};  合约-{asset_name}空单持仓量: {symbol_futures_volume}"
            logger.log(30, msg)
            msg = f"现货最大交易量: {symbol_spot_balance}个币; 合约最大交易量: {abs(symbol_futures_volume)}个币; (当前平仓volume: {volume}, 合约最新价:{last_price_futures})"
            logger.log(30, msg)

            # 3. 判断是否能够卖出
            if (symbol_spot_balance < volume) or (volume == 0):
                msg = f"############## 现货-{asset_name}: {symbol_spot_balance}个币, 不足卖出 {volume}个 {asset_name}现货!!!  [无法交易]\n"
                raise Exception(msg)
            if (abs(symbol_futures_volume) < volume) or (volume == 0):
                msg = f"############## 合约-{asset_name}: {symbol_futures_volume}个持仓量, 不足平仓 {volume}个 {asset_name}空头合约!!!  [无法交易]\n"
                raise Exception(msg)
            msg = f"============== 余额检测通过!!  [允许交易]\n"
            logger.log(30, msg)
            return volume

    def _filter_min_notional(self, pair_name, volume):
        "过滤器-最小名义市值: 防止计算出的volume不符合交易的精度"
        _, symbol = pair_name.split(".")

        # 1. 查询当前币种的最新价格
        last_price_spot = self.Data.get_last_price(pair_name=pair_name, type="spot")
        last_price_futures = self.Data.get_last_price(pair_name=pair_name, type="futures")

        # 2. 最小交易额问题: 修改volume后, 再核对下是否满足平台最小交易额 10u
        qty_spot = last_price_spot * volume
        qty_futures = last_price_futures * volume
        if (qty_spot <= 10) or (qty_futures <= 10):
            msg = f"[{symbol}-不满足最低交易额] 现货的交易金额: {qty_spot};  合约的交易金额: {qty_futures}"
            raise Exception(msg)

    def _filter_lot_size(self, pair_name, volume, order_type="both"):
        """
        function: 过滤器-订单尺寸过滤器: 防止计算出的volume不符合交易的精度
        args:
            order_type: "both"/"spot"/"futures" ("both"代表'现货和合约'都需要检查 lot_size)
        """
        (pair_name, exchange_name, symbol, asset_name) = self.Data._split_pair_name(pair_name=pair_name)

        # 1. volume不能为0
        if volume == 0:
            msg = f"[{symbol}-交易量为0] 终止下单  (检查是否已经没有仓位..)"
            raise Exception(msg)

        # 2.保留有效数字: 在最高位向后保留3位数 (即: 123456.123保留成 123000; 0.00123456保留成0.00123)
            # // 不需要这个保留有效数字的过程, 多此一举... (因为下面就会做精度调整)
        # volume = round(volume, -math.floor(math.log10(volume))+2) # 前面是负号, 并在最高位数基础上保留2位数

        # 3. 最小精度问题: 查询self.oms.contracts中的最小volume精度, 避免volume精度过高超过官方支持而报错...
            # 一般来说现货支持更高的精度, 而合约的最小支持精度比现货低一级 (即: 现货可以交易1.23个币, 而合约只能交易1.2个币)
        if order_type == "both":
            spot_precision = self.oms.contracts.get(f"{symbol.lower()}.{exchange_name}", {}).min_volume
            futures_precision = self.oms.contracts.get(f"{symbol.upper()}.{exchange_name}", {}).min_volume
            min_volume = max(spot_precision, futures_precision) # 取更大(更粗略)的那一个精度
            supported_deal_count = math.floor(volume / min_volume) * min_volume
            supported_deal_count = round(supported_deal_count, 10) # 上面的计算中可能出现'python浮点精度问题', 所以这里必须再做一次round
        elif order_type == "spot":
            min_volume = self.oms.contracts.get(f"{symbol.lower()}.{exchange_name}", {}).min_volume
            supported_deal_count = math.floor(volume / min_volume) * min_volume
            supported_deal_count = round(supported_deal_count, 10) # 上面的计算中可能出现'python浮点精度问题', 所以这里必须再做一次round
        elif order_type == "futures":
            min_volume = self.oms.contracts.get(f"{symbol.upper()}.{exchange_name}", {}).min_volume
            supported_deal_count = math.floor(volume / min_volume) * min_volume
            supported_deal_count = round(supported_deal_count, 10) # 上面的计算中可能出现'python浮点精度问题', 所以这里必须再做一次round
        if (volume != 0) and (supported_deal_count == 0):
            raise Exception("######## 最小精度问题, 导致计算出来的volume为0!!!")
        else:
            volume = supported_deal_count
            return volume

    def _cal_volume(self, pair_name, multiplier, insurance_usdt=800):
        """
            function: 通过'交易乘数', 来计算实际开仓需要的volume
            args:
                multiplier: 乘数就是 1:1  (100代表100u) [即: 开仓金额的意思]
                insurance_usdt: 保险开仓金额  (eg:最大只能开200, 参数可调)
        """
        _, symbol = pair_name.split(".")

        # 1. 在oms.ticks中获取该币种最新的成交价格
        last_price = self.Data.get_last_price(pair_name=pair_name, type="futures") # 使用'合约最新价格'来计算

        # 2. 通过'交易乘数', 计算出实际开仓所需的volume
        if multiplier > insurance_usdt:
            multiplier = insurance_usdt
            logger.log(40, f"!!!!!!!!! [{symbol}] 开仓金额大于最高上限, 调整至最高上限:{insurance_usdt}usdt [检查是否手误!!]\n\n")

        volume = (1 / last_price) * multiplier
        # 过滤器-订单数量精度
        volume = self.Trade._filter_lot_size(pair_name=pair_name, volume=volume)
        return volume

    def _recur_check_is_matched(self, pair_name):
        """
            function: 开仓前, 检查币对是否已经配平 (没配平就不开单)
        """
        # 0. 初始校验
        (pair_name, exchange_name, symbol, asset_name) = self.Data._split_pair_name(pair_name=pair_name)
        # 防止网络延迟导致单边余额增加而另一边没增加: 循环5秒检查是否已经配平...
        for i in range(5):
            is_matched = self.Trade.judge_match(pair_name=pair_name)
            if is_matched:
                return True
            time.sleep(2) # 循环5次

        # 如果循环5次检测都没有配平, 则抛出异常
        # msg = f"####### [未平警告]: {asset_name}-现货数量: {spot_amount};  {symbol}-合约数量: {futures_volume};   数量差: {delta_amount}\n"
        # msg += f"####### [未平警告]: {asset_name}-现货市值: {spot_marketValue};  {symbol}-合约市值: {futures_marketValue};   市值差: {delta_marketValue}\n\n\n"
        self.Trade.redeem_delta_amount(pair_name=pair_name) # 开始补救配平
        msg = f"[未平报错] 币种: {symbol}"
        print("尝试启动补救配平...")
        raise Exception(msg)

    def judge_match(self, pair_name):
        """
            function: 判断'期现是否配平' (不配平, 禁止下单)
            notes: 这里的检查是'下单前的检查' (与'Risk.check_match'不一样, 那个是全币种检查)
        """
        # 0. 初始校验
        (pair_name, exchange_name, symbol, asset_name) = self.Data._split_pair_name(pair_name=pair_name)

        # 1. 检查现货和合约的量
            # i. 合约持仓量
        if self.oms.positionSide == "DOUBLE":
            position_obj = self.oms.positions.get(f"{symbol}.BINANCE.空")
        elif self.oms.positionSide == "SINGLE":
            position_obj = self.oms.positions.get(f"{symbol}.BINANCE.单向模式")
        if position_obj:
            futures_volume = position_obj.volume
            # futures_price = position_obj.price # [巨坑]: 这个仓位对象的price是指 '开仓价格'
            futures_price = self.Data.get_last_price(pair_name=pair_name, type="futures")
            futures_marketValue = futures_volume * futures_price
        else:
            futures_volume = 0
            futures_marketValue = 0
            futures_price = self.Data.get_last_price(pair_name=pair_name, type="futures")
            # futures_marketValue = futures_volume * futures_price

            # ii. 现货数量
        spot_account_obj = self.oms.accounts.get("spot").get(f"BINANCE.{asset_name}")
        fullMargin_account_obj = self.oms.accounts.get("fullMargin").get(f"BINANCE.{asset_name}")
        isoMargin_account_obj = self.oms.accounts.get("isoMargin").get(f"BINANCE.{asset_name}")
        if spot_account_obj or fullMargin_account_obj or isoMargin_account_obj:
            spot_price = self.Data.get_last_price(pair_name=pair_name, type="spot")
            # 1. 现货
            spot_amount = spot_account_obj.balance if spot_account_obj else 0
            spot_marketValue = spot_amount * spot_price
            # 2. 全仓
            fullMargin_amount = fullMargin_account_obj.balance if fullMargin_account_obj else 0
            fullMargin_marketValue = fullMargin_amount * spot_price
            # 3. 逐仓
            isoMargin_amount = isoMargin_account_obj.balance if isoMargin_account_obj else 0
            isoMargin_marketValue = isoMargin_amount * spot_price
            # 汇总
            spot_amount = spot_amount + fullMargin_amount + isoMargin_amount
            spot_marketValue = spot_marketValue + fullMargin_marketValue + isoMargin_marketValue
        else:
            spot_amount = 0
            spot_marketValue = 0

        delta_amount = spot_amount + futures_volume
        # delta_marketValue = spot_marketValue + futures_marketValue # 这样整体的'市值差'呈现好像意义不大...
        delta_marketValue = delta_amount * futures_price # 只计算多余数量下的'价值差'
        msg = f"####### [{self.Client.user}-配平检测]: {asset_name}-现货数量: {spot_amount};  {symbol}-合约数量: {futures_volume};   数量差: {delta_amount}\n"
        msg += f"####### [{self.Client.user}-配平检测]: {asset_name}-现货市值: {spot_marketValue};  {symbol}-合约市值: {futures_marketValue};   市值差: {delta_marketValue}\n\n\n"
        print(msg)
        if abs(delta_marketValue) < 80:
            return True
        else:
            return False

    def get_pair_volume(self, pair_name="BINANCE.LUNAUSDT"):
        """
            function: 获取某个币种的最大平仓持仓量.
                (当币种余额小于100u时, 我不想精准地计算数量, 直接全仓交易, 所以需要获取这个精准的持仓量)
        """
        (pair_name, exchange_name, symbol, asset_name) = self.Data._split_pair_name(pair_name=pair_name)
        # 该币种的现货余额
        spot_balance = self.oms.accounts.get("spot")[f"{exchange_name}.{asset_name}"].balance
        # 该币种的合约持仓量
        futures_volume = self.oms.positions[f"{symbol}.{exchange_name}.空"].volume
        max_available_volume = min(spot_balance, abs(futures_volume))
        return max_available_volume

    def two_sides_send_order(self, pair_name, offset, volume):
        """
            function:
                - 检查: 现货和期货的剩余资金是否足够下单 (双边下单)
                - 下单:
                    1.先合约下单
                    2.后现货下单

            usage:
                eg1:
                    # 双边下单
                    sc.two_sides_send_order(pair_name="BINANCE.LUNAUSDT", offset="OPEN", volume=1)
                    (鉴于套利策略特性的双边下单, 不需要有type/direction/order_type这些参数)
        """

        # 0. 初始校验
        (pair_name, exchange_name, symbol, asset_name) = self.Data._split_pair_name(pair_name=pair_name)

        # 1. 开仓前检测: 当前是否配平 (如果发现未配平, 则抛出异常不执行后序任务)
        self._recur_check_is_matched(pair_name=pair_name)

        # 1. 下单
            # i. 开仓: 做空卖出合约, 买入现货;
        if offset == "OPEN":
                # 1. 核对仓位余额
            volume = self.Trade._check_balance(pair_name=pair_name, volume=volume, offset=offset)
                # 2. 做空卖出合约
            req_futures = OrderRequest(
                exchange=Exchange[exchange_name], symbol=symbol, offset=Offset.OPEN, direction=Direction.SHORT,
                type=OrderType.MARKET, price=None, volume=volume
            )
            vt_orderid_futures = self.main_engine.send_order(req_futures, gateway_name=exchange_name+"S")
                # 3. 买入现货
            print(f"实际开仓volume:{volume}")
            req_spot = OrderRequest(
                exchange=Exchange[exchange_name], symbol=symbol, offset=Offset.OPEN, direction=Direction.LONG,
                type=OrderType.MARKET, price=None, volume=volume
            )
            vt_orderid_spot = self.main_engine.send_order(req_spot, gateway_name=exchange_name)

            # ii. 平仓: 平空买入合约, 卖出现货;
        elif offset == "CLOSE":
                # 1. 核对仓位余额
            volume = self.Trade._check_balance(pair_name=pair_name, volume=volume, offset=offset)
                # 2. 平空买入合约
            req_futures = OrderRequest(
                exchange=Exchange[exchange_name], symbol=symbol, offset=Offset.CLOSE, direction=Direction.LONG,
                type=OrderType.MARKET, price=None, volume=volume
            )
            # print(f"req_futures:{req_futures}")
            vt_orderid_futures = self.main_engine.send_order(req_futures, gateway_name=exchange_name+"S")
                # 3. 卖出现货
            req_spot = OrderRequest(
                exchange=Exchange[exchange_name], symbol=symbol, offset=Offset.CLOSE, direction=Direction.SHORT,
                type=OrderType.MARKET, price=None, volume=volume
            )
            # print(f"req_spot:{req_spot}")
            vt_orderid_spot = self.main_engine.send_order(req_spot, gateway_name=exchange_name)

        # todo: 需要通过 'vt_orderid' 来判断, 该请求是否已经交易成功, 如果没有成功, 则循环等待
            # (10s还没有成功, 则报错退出, 或者打印大篇幅'#'来提示出错!)
        time.sleep(1) # 也可以作为降低下单频次的功能
        spot_success = False
        futures_success = False
        for i in range(10):
            spot_order = self.oms.orders.get(vt_orderid_spot)
            futures_order = self.oms.orders.get(vt_orderid_futures)
            if spot_order and spot_order.status.value == "全部成交":
                spot_success = True
            if futures_order and futures_order.status.value == "全部成交":
                futures_success = True
            if spot_success and futures_success:
                break
            print("循环睡眠...")
            time.sleep(1) # 也可以作为降低下单频次的功能
        return spot_success, futures_success

    def redeem_delta_amount(self, pair_name="BINANCE.LUNAUSDT", offset="CLOSE"):
        """
        function: 自动检测期现的数量差, 如果没有对齐, 则自动单边下单补齐
        args:
            offset: "OPEN"/"CLOSE" (开仓和平仓的处理逻辑是不一样的...)
        notes:
        usage:
            lsh.Trade.redeem_delta_amount(pair_name="BINANCE.aliceUSDT")
            zl.Trade.redeem_delta_amount(pair_name="BINANCE.ZENUSDT")

        """
        # 0. 初始校验
        (pair_name, exchange_name, symbol, asset_name) = self.Data._split_pair_name(pair_name=pair_name)

        volume_df = self.Risk.check_match()
        print(volume_df)
        query_df = volume_df.query(f"币种=='{symbol}'")
        delta_amount = query_df["期现-数量差"].iloc[0]
        delta_value = query_df["期现-价值差"].iloc[0]
        if (delta_value > 200) or (delta_value < -200): # 机动修改!!!  平常设置为1000
            msg = f"### 币种{symbol}:  期现价值差差异过大, 抛出异常, 终止弥补redeem   (期现-数量差:{delta_amount};  期现-价值差:{delta_value})"
            raise Exception(msg)
        if delta_amount > 0:
            self.Trade.one_side_send_order(
                pair_name=pair_name, type="spot", offset="CLOSE", direction="SELL", volume=abs(delta_amount), order_type="MARKET"
            )
        elif delta_amount < 0:
            self.Trade.one_side_send_order(
                pair_name=pair_name, type="spot", offset="OPEN", direction="BUY", volume=abs(delta_amount), order_type="MARKET"
            )
        elif delta_amount == 0:
            pass

    def one_side_send_order(
            self, pair_name="BINANCE.LUNAUSDT", type="spot", offset="OPEN", direction="BUY",
            order_type="MARKET", price=10, volume=1, insurance_usdt=800,
        ):
        """
            function: 封装后的send_order (单边下单)
            args:
                pair_name:
                    "BINANCE.LUNAUSDT"
                type:
                    现货: 'spot'
                    合约: 'futures'
                offset:
                    开仓: "OPEN"   # 对应vnpy的 Offset.OPEN
                    平仓: "CLOSE"   # 对应vnpy的 Offset.CLOSE
                direction:
                    买入: "BUY"   # 对应vnpy的 Direction.LONG
                    卖出: "SELL"   # 对应vnpy的 Direction.SHORT
                order_type:
                    (使用kw618的命名方式作为参数传入, 在函数内部转化成vnpy的命名方式)
                    市价单: "MARKET"
                    限价单: "LIMIT"
                insurance_usdt:
                    (保险值: 单次最多支持多少usdt的交易金额)
            return:
                返回 该函数生成的req生成的order 下的 order.vt_orderid
                    # vt_orderid: "BINANCE.mUvoqJxFIILMdfAW5iGSOW"
            notes:
                - 单边下单不需要验证账户余额, 如果没有余额交易所会返回错误, 不需要自己验证...

            usage:
                eg1:
                    # 单边下单
                sc.one_side_send_order(pair_name="BINANCE.LUNAUSDT", type="futures", offset="OPEN", direction="BUY", volume=1, order_type="MARKET")

        """
        # 0. 初始校验
        (pair_name, exchange_name, symbol, asset_name) = self.Data._split_pair_name(pair_name=pair_name)
        # 0. 单次交易的最大限额
        # last_price_spot = self.Data.get_last_price(pair_name=pair_name, type="spot")
        last_price_futures = self.Data.get_last_price(pair_name=pair_name, type="futures")
        value = volume * last_price_futures
        if value > insurance_usdt:
            volume = insurance_usdt / last_price_futures
            volume = self.Trade._filter_lot_size(pair_name=pair_name, volume=volume, order_type=type)
            logger.log(40, f"!!!!!!!!! [{symbol}] 开仓金额大于最高上限, 调整至最高上限:{insurance_usdt}usdt (即: {volume}个{symbol}) [检查是否手误!!]\n\n")

        # 过滤器1-订单数量精度
        volume = self.Trade._filter_lot_size(pair_name=pair_name, volume=volume, order_type=type)
        # 过滤器2-最低交易额
        self.Trade._filter_min_notional(pair_name=pair_name, volume=volume)

        # 1. 构造vnpy中的请求req对象
        if type == "spot":
            symbol = symbol.lower()
            gateway_name = exchange_name
        elif type == "futures":
            symbol = symbol.upper()
            gateway_name = exchange_name + "S"
        req = OrderRequest(
            exchange=Exchange[exchange_name], symbol=symbol, offset=OFFSET_KW2VT[offset], direction=DIRECTION_KW2VT[direction],
            type=ORDERTYPE_KW2VT[order_type], price=price, volume=volume
        )

        # 2. 下单
        vt_orderid = self.main_engine.send_order(req, gateway_name=gateway_name)
        # logger.log(30, f"下单成功!!!\n") # 不能说'交易成功', 因为有些req是委托限价单, 这里也会返回orderid相关信息
        return vt_orderid

    def fast_buy_sell(self, pair_name="BINANCE.LUNAUSDT", multiplier=100, time_sleep=10, sell_first=True):
        """
            # '秒抢费率'
            function: 合约单边, 快速的买入卖出 (冲进去吃一波资金费率就退场)
                (会有亏损的情况, 所以这么操作的前提: 要能接受10秒内价格剧烈波动的亏损and单边0.1%的手续费成本)
            args:
                - sell_first:
                    True: 先开空卖出, 后平空买入
                    False: 先开多买入, 后平多卖出

            notes:
                - 最佳执行条件:
                        - 资金费率巨高 (至少0.5%以上)
                        - 交割节点前2秒执行
                        (单边交易不需要考虑'价差率'的问题...)
                - '单边抢费率'的成本:
                        1. 0.12%的手续费 (实际还有bnb优惠和推荐费优惠)
                        2. 假设0.08%的滑点成本
                        3. 假设 0.1% 的盘口价差 (即使当前纳秒买,当前纳秒卖, 也会存在盘口价差, 是必亏的!) [这个一定也要注意...]
                        3. 所以如果资金费率高达0.5%, 除去手续费和滑点, 还有0.2%的升水补贴!!
                            (用这0.2%的补贴去抗衡可能的损失, 也是值得搏一搏的!! 这比滚ic的补贴多多了...)
                            # ***(要有100次, 共计34天, 就可以达到20%的补贴, 这比ic一年的12%高多了...)
                            (也是个不错的策略, 可以作为套利策略的替补策略...)
            # TODO:
                - 1. 做成多线程的形式去跑: 以后可以在交割节点前开10个币种去单边抢费率...
                        (前提是10个币的资金费率都很高!!)
                        同时买10个币种可以做到风险分摊: 在价格上10个币种不一定都跌...
                            i. 10s内的平均跌幅应该不会很大, 还可能赚钱呢...
                            ii. 滑点成本也会因为多币种分摊下来?
        """
        # 1. 校验pair_name
        (pair_name, exchange_name, symbol, asset_name) = self.Data._split_pair_name(pair_name=pair_name)
        if (f"{symbol.lower()}.{exchange_name}" not in list(self.oms.ticks)) or \
            (f"{symbol.upper()}.{exchange_name}" not in list(self.oms.ticks)):
            print(f"######## 未订阅 {symbol} 的tick数据, 开始订阅中....")
            self.Data.subscribe_many(pair_lst=[pair_name])

        # 根据乘数, 计算出volume
        volume = self.Trade._cal_volume(pair_name=pair_name, multiplier=multiplier)

        # i. 如果是'先卖后买'
        if sell_first:
            # 1. 开空卖出
            self.Trade.send_order(pair_name=pair_name, type="futures", offset="OPEN", direction="SELL", volume=volume)
            # 2. 睡眠
            time.sleep(time_sleep)
            # 3. 平空买入
            self.Trade.send_order(pair_name=pair_name, type="futures", offset="CLOSE", direction="BUY", volume=volume)
        # ii. 如果是'先买后卖'
        else:
            # 1. 开多买入
            self.Trade.send_order(pair_name=pair_name, type="futures", offset="OPEN", direction="BUY", volume=volume)
            # 2. 睡眠
            time.sleep(time_sleep)
            # 3. 平多卖出
            self.Trade.send_order(pair_name=pair_name, type="futures", offset="CLOSE", direction="SELL", volume=volume)

    def divide(self, spot_ratio=0.49):
        """
            function: 按 spot_ratio 均分 '现货账户'和'合约账户'的usdt余额
                    (为了更方便地套利)
            usage:
                sc.Trade.divide(spot_ratio=0.5)
        """
        # 1. 查询当前余额
            # i. 现货USDT可用余额
        usdt_account = self.oms.accounts.get("spot").get("BINANCE.USDT")
        if usdt_account:
            usdt_available_balance_spot = usdt_account.balance - usdt_account.frozen
        else:
            usdt_available_balance_spot = 0
            # ii. 合约USDT可用余额 (即: 钱包余额) (即: 最真实的保证金, 不考虑合约的浮盈浮亏!!)
        usdt_available_balance_futures = self.Data.futures_index.get("availableBalance")
            # iii. 双边的usdt总和
        sum_usdt = usdt_available_balance_spot + usdt_available_balance_futures
            # iv. 现货中需要有这么多的usdt (按照spot_ratio计算)
        spot_usdt = round(spot_ratio * sum_usdt)

        # 2. 开始划转
            # i. 如果现货usdt已经大于本应该配的量 (usdt从现货划转至合约账户)
        if usdt_available_balance_spot > spot_usdt:
            delta = abs(round(usdt_available_balance_spot - spot_usdt))
            self.Client.spot_rest_api.transfer(t_type="MAIN_UMFUTURE", amount=delta, asset="USDT")
            # i. 如果现货usdt小于本应该配的量 (usdt从合约账户划转至现货账户)
        elif usdt_available_balance_spot < spot_usdt:
            delta = abs(round(spot_usdt - usdt_available_balance_spot))
            self.Client.spot_rest_api.transfer(t_type="UMFUTURE_MAIN", amount=delta, asset="USDT")

    def queue_price_send_order(self, pair_name, offset, volume, hang_type="futures"):
        """
            function: 使用排队价下单, 当一腿成交后, 另一腿马上市价吃掉!! (逻辑同'AIcoin')
            args:
                hang_type: 挂单用的是什么账户 ('futures'/'spot')
        # 0. 初始校验
        (pair_name, exchange_name, symbol, asset_name) = self.Data._split_pair_name(pair_name=pair_name)

        # 1. 下单
            # i. 开仓: 做空卖出合约, 买入现货;
        if offset == "OPEN":
                # 1. 核对仓位余额
            self.Trade._check_balance(pair_name=pair_name, volume=volume, offset=offset)
                # 2. 做空卖出合约
            req_futures = OrderRequest(
                exchange=Exchange[exchange_name], symbol=symbol, offset=Offset.OPEN, direction=Direction.SHORT,
                type=OrderType.MARKET, price=None, volume=volume
            )
            vt_orderid_futures = self.main_engine.send_order(req_futures, gateway_name=exchange_name+"S")
                # 3. 买入现货
            req_spot = OrderRequest(
                exchange=Exchange[exchange_name], symbol=symbol, offset=Offset.OPEN, direction=Direction.LONG,
                type=OrderType.MARKET, price=None, volume=volume
            )
            vt_orderid_spot = self.main_engine.send_order(req_spot, gateway_name=exchange_name)

            # ii. 平仓: 平空买入合约, 卖出现货;
        elif offset == "CLOSE":
                # 1. 核对仓位余额
            self.Trade._check_balance(pair_name=pair_name, volume=volume, offset=offset)
                # 2. 平空买入合约
            req_futures = OrderRequest(
                exchange=Exchange[exchange_name], symbol=symbol, offset=Offset.CLOSE, direction=Direction.LONG,
                type=OrderType.MARKET, price=None, volume=volume
            )
            vt_orderid_futures = self.main_engine.send_order(req_futures, gateway_name=exchange_name+"S")
                # 3. 卖出现货
            req_spot = OrderRequest(
                exchange=Exchange[exchange_name], symbol=symbol, offset=Offset.CLOSE, direction=Direction.SHORT,
                type=OrderType.MARKET, price=None, volume=volume
            )
            vt_orderid_spot = self.main_engine.send_order(req_spot, gateway_name=exchange_name)

        # 如果执行到这一步都没有报错, 则表示下单成功, 返回True..
        success = True
        return success
    """


class AccountManager():
    """
        notes:
            需要能同时实例化100个User对象. (使用多进程??)
            - 实例化的过程使用多进程, 实例化最后的结果可以append到这个manager的列表中..
    """

    def __init__(self, main_account_name="LSH"):
        # self.main_account_name = main_account_name
        # self.main_account = ''
        self.accounts = {}

    def add_accounts(self, gateway_setting_lst):
        """
            function:
                添加网关的设置信息, 以此来新建一群'账户对象'
            notes:
                - 可以指定某个account_name为'主账户'
        """

        def _init_account(gateway_setting):
            account = SpreadClient(gateway_setting=gateway_setting)
            # 挂载
            account.am = self
            self.accounts.update({gateway_setting.get("account_name"):account})
            account_name = gateway_setting.get("account_name")
            # 指定某个account对象为'主账户' (用于计算价差率, 供其他子账户使用...)
            if account_name == self.main_account_name:
                self.main_account = account

        # self.thread_pool = []
        for gateway_setting in gateway_setting_lst:
            logger.log(10, "\n通过子线程新建一个'账户对象'...")
            t = threading.Thread(
                target=_init_account, # 不是该类下的直接子函数, 这里调用函数时不能在前面加self?
                kwargs=({'gateway_setting':gateway_setting})
                )
            t.start()
            time.sleep(1)
            # self.thread_pool.append(t)

    def __repr__(self):
        txt = f"< AM对象 | {self.accounts}> "
        return txt

    def _check(self):
        # 等待add_accounts函数100s, 看能否成功添加main_account (100s都没添加好, 就报错)
        for i in range(100):
            if self.main_account:
                return True
            time.sleep(1)
        raise Exception("'main_account'添加失败, 请重试am.add_accounts函数...")

    def get(self, account_name):
        "通过'账户名称'获取账户对象"
        return self.accounts.get(account_name)

    def add_pairs(self, pair_lst):
        self.main_account.Data.add_pairs(pair_lst=pair_lst)
        self.main_account.Data.active()

    def cal(self):
        """
            function: 计算am对象下挂载的所有sc对象的所有持仓的position
                # am.add_pairs自带有main_cal的执行
        """
        # 1. 核对是否存在main_account (不用管它)
        self._check()

        # 2. 获取am下所有sc的所有持仓的 pair_name
        pair_name_lst = []
        for account_name, sc in self.accounts.items():
            l = sc.Data.get_my_pair_lst() # 获取该sc的所有持仓的 pair_name
            pair_name_lst.extend(l)

        # 3. 订阅所有账户下的所有持仓币对的tick数据
        pair_name_lst = list(set(pair_name_lst)) # 去重
        logger.log(20, f"该am对象下的所有持仓币对:\n{pair_name_lst}")
        self.main_account.Data.add_pairs(pair_lst=pair_name_lst)

        # 4. 同时计算所有币种的价差率 (使用多线程)
        self.main_account.Data.active() # active函数中包含了 main_cal函数

    def stop_cal(self):
        self._check()
        self.main_account.Data.stop_cal()

    def print(self):
        self._check()
        self.main_account.Show.main_print()

    def stop_print(self):
        self._check()
        self.main_account.Show.stop_print()

    def open_robot(
            self, pair_lst, multiplier=1, volume=None, target_spread_rate=0.005,
            trading_count=3, to_print=False
        ):
        """
            function: 批量新建'开仓robot'
                - 现有持仓中, 只要找到合适的价差率, 就可以提前平仓... (比如0.5%)
            args:
                pair_lst: ["BINANCE.LUNAUSDT", "BINANCE.ALPHAUSDT"]
            usage:
                # 把所有持仓合约都开启'开仓robot'
                pair_lst = self.Data.get_my_pair_lst()
                sc.batch_create_open_robot(pair_lst=pair_lst)
        """
        # 遍历am中的sc对象
        for account_name, account in self.accounts.items():
            logger.log(10, f"<{account_name}> 正在批量生成 '开仓'robot...")
            # 批量生成开仓robot
            account.batch_create_open_robot(
                pair_lst=pair_lst, multiplier=multiplier, volume=volume,
                target_spread_rate=target_spread_rate, trading_count=trading_count, to_print=to_print
            )

    def close_robot(
            self, pair_lst, multiplier=1, volume=None, target_spread_rate=0.001,
            trading_count=3, to_print=False
        ):
        """
            function: 批量新建'平仓robot'
                - 现有持仓中, 只要找到合适的价差率, 就可以提前平仓... (比如0.1%)
            args:
                pair_lst: ["BINANCE.LUNAUSDT", "BINANCE.ALPHAUSDT"]
            usage:
                # 把所有持仓合约都开启'平仓robot'
                pair_lst = sc.Data.get_my_pair_lst()
                sc.batch_create_close_robot(pair_lst=pair_lst)
        """
        # 遍历am中的sc对象
        for account_name, account in self.accounts.items():
            logger.log(10, f"<{account_name}> 正在批量生成 '平仓'robot...")
            # 批量生成平仓robot
            account.batch_create_close_robot(
                pair_lst=pair_lst, multiplier=multiplier, volume=volume,
                target_spread_rate=target_spread_rate, trading_count=trading_count, to_print=to_print
            )

    def active(self, offset="BOTH", trading_count=None):
        # 遍历am中的sc对象
        for account_name, account in self.accounts.items():
            account.active_all_robots(offset=offset, trading_count=trading_count)

    def pause(self, offset="BOTH", trading_count=None):
        "pause只是停止每个sc对象的robot对象的run函数运行(clear是清空所有robot)"
        # 遍历am中的sc对象
        for account_name, account in self.accounts.items():
            account.pause_all_robots(offset=offset, trading_count=trading_count)

    def clear(self, offset="BOTH"):
        "pause只是停止每个sc对象的robot对象的run函数运行(clear是清空所有robot)"
        # 遍历am中的sc对象
        for account_name, account in self.accounts.items():
            account.clear(offset=offset)

    def show(self, type=1):
        # 遍历am中的sc对象
        for account_name, account in self.accounts.items():
            df = account.get_df(type=type)
            print(df)

    def get_real(self):
        "获取每个账户的实际成交的价差率"
        pass


class Account():
    """
        spread_client框架解析:
            调度模块: [核心!!] [其实就是'量化策略'or'程序化策略'] (SC本身self就是负责这个模块的)
                1. 创造各种类型的robot [开仓]/[平仓]
                2. 调度robot [调仓]
                3. 销毁robot [停止操作]
                (如果开仓/平仓, 开/平多少, 什么时候调, 调成什么币种?? 一系列都是问题, 这才是整个策略最核心的部分!!) [研究策略和算法]
                (多线程执行, 所以在线程管理和线程安全问题上也要重视)
            数据模块:
                (指: 将盘口挂单数据计算成盘口价差率, 方便robot执行)
                (使用统一的数据来源!! 这样各个robot之间没有数据误差, 后期若发现价差率计算有bug也方便修改)
                // 0528更新: 盘口数据的获取, 价差率的计算, 都挪到别的脚本去了, 这里只做和账户相关的数据获取
                    (这样vnpy的网关中就不需要订阅盘口的实时推送了, 减少开销)
                1. 数据获取
                2. 数据计算
                3. 数据打印
                4. 数据调用
            风控模块:
                1. 保证金率风控 (邮件发送)
            展示模块:
                1. 展示每笔交易的'实际价差率'
                2. 展示'爆仓率'
                3. 循环展示'当前所有币对的价差率'
                4. 呈现每日的资金费用收入
            交易模块:
                1. 单边下单
                2. 双边下单
                3. 余额核验
            可视化模块:
                1. 将各种重要指标数据呈现在web端??
                (收益曲线?)

            思考: 这几个系统要分别写成'类'的形式吗? (还是全部塞在SpreadClient类中?? 优劣??)

        usage:
            lsh = SpreadClient(LSH_BINANCE_SETTING)

        todo:
            - 该Account对象, 最好是能够兼容所有交易所的api?
            - 实时更新: u/币本位的保证金率; 全仓/逐仓杠杆的风险率!  [做好足够的风险控制]
            - 逐仓杠杆的每小时还款! (没钱自动转账??)

    """
    def __init__(self, gateway_setting=LSH_BINANCE_SETTING, engines=[]):
        """
            notes:
                - SC类本身的职责: 各种子模块的'调度' (包括各种robot的调度)
        """
        # 1. 初始化vnpy中的组件
        main_engine = init_main_engine(gateway_setting=gateway_setting, engines=engines) # 启动vnpy框架的'主引擎'对象
        self.account_name = main_engine.account_name
        self.user = self.account_name # 助记
        self.am = "" # 初始为空 (account_manager对象) (通过am对象add_accounts函数才会有此挂载)
        self.main_engine = main_engine
        self.oms = main_engine.engines["oms"]
        self.log_engine = main_engine.engines["log"]
        self.logger = self.log_engine.logger
        self.logger.setLevel(30)  # 可以通过这种方式控制logger打印内容
        self.email_engine = main_engine.engines["email"]
        self.spot_rest_api = main_engine.gateways.get("BINANCE").rest_api
        self.futures_rest_api = main_engine.gateways.get("BINANCES").rest_api
        self.spot_trade_ws_api = main_engine.gateways.get("BINANCE").trade_ws_api
        self.futures_trade_ws_api = main_engine.gateways.get("BINANCES").trade_ws_api
        self.spot_market_ws_api = main_engine.gateways.get("BINANCE").market_ws_api
        self.futures_market_ws_api = main_engine.gateways.get("BINANCES").market_ws_api

        # 2. 挂载SC的各个子模块
        self.Data = DataModule(main_engine=main_engine, client=self) # 把sc自身这个对象作为client参数传入
        self.Trade = TradeModule(main_engine=main_engine, client=self)
        self.Risk = RiskModlue(main_engine=main_engine, client=self)
        self.Show = ShowModlue(main_engine=main_engine, client=self)
        self._mount_submodule() # 方便各个子模块函数的相互调用

        # 3. 初始化SC中所需变量
        self.timer = 0
        self.open_d = {} # 存放所有'开仓机器人'
        self.close_d = {} # 存放所有'平仓机器人'
        self.open_df = '' # 用df的形式呈现robot数据
        self.close_df = ''
        self.delta_serverTime = get_timedelta(0)

        # 4. 注册事件的监听handler
            # 1. Timer定时器的监听 (这个事件每隔1s被执行一次)
        self.main_engine.event_engine.register(EVENT_TIMER, self.process_timer_event)
            # 2. TickData推送的事件监听
        self.main_engine.event_engine.register(EVENT_TICK, self.process_tick_event)

        # 5. 执行一些初始启动函数
            # i. 计算合约账户的'爆仓率'
        self.Data._live_update_margin_rate()
            # ii. 展示一些'关键爆仓指标'
        self.Show.show_futures_index()

        # 6. 设置更多'个性化/可控'的参数 (便于程序执行中控制走向) [以后可以通过不同'参数表'来启动实例]
        self.pause_on_rugularTime = False # (每天3个节点后10秒, 关闭所有'开仓robot')

    def __repr__(self):
        txt = f"<账户{self.account_name}>"
        return txt

    def _mount_submodule(self):
        """
            function: 方便各个子模块函数的相互调用
        """
        self.Data.Data = self.Data
        self.Data.Trade = self.Trade
        self.Data.Risk = self.Risk
        self.Data.Show = self.Show

        self.Trade.Data = self.Data
        self.Trade.Trade = self.Trade
        self.Trade.Risk = self.Risk
        self.Trade.Show = self.Show

        self.Risk.Data = self.Data
        self.Risk.Trade = self.Trade
        self.Risk.Risk = self.Risk
        self.Risk.Show = self.Show

        self.Show.Data = self.Data
        self.Show.Trade = self.Trade
        self.Show.Risk = self.Risk
        self.Show.Show = self.Show

    def process_timer_event(self, event: Event) -> None:
        """
            functions: 处理'定时器事件' (该事件没有具体data, 只用于跟'时间'相关的任务)
            notes: 每秒执行一次
        """
        # 每到3600s归零 (每隔1个小时归零)
        self.timer += 1
        if self.timer == 3600:
            self.timer = 0
        # 一. 需要每1秒执行的函数
        if self.timer % 1 == 0:
                # 实时更新每个币对的'资金费率'
            self.Data._live_update_funding_rate()
                # 定时闹钟
            self.process_clock()
        # 二. 需要每5秒执行的函数
        if self.timer % 5 == 0:
            pass
        # 三. 需要每10秒执行的函数
        if self.timer % 10 == 0:
                # 1. 实时更新本账户的'u本位-维持保证金率'
            self.Data._live_update_margin_rate()
                # 2. todo: 实时更新本账户的'币本位-维持保证金率'
            # self.Data._live_update_margin_rate()
                # 3. todo: 实时更新本账户的'全仓杠杆-风险率'
            # self.Data._live_update_margin_rate()
                # 4. todo: 实时更新本账户的'逐仓杠杆-风险率'
            # self.Data._live_update_margin_rate()
                # 5. 实时更新最新价格 (价值不大, 暂时取消)
            # self.Data._live_update_last_price()
        # 四. 需要每30秒执行的函数
        if self.timer % 30 == 0:
            pass
        # 五. 需要每60秒执行的函数
        if self.timer % 60 == 0:
                # 1. 检测'u本位-维持保证金率'是否过高 (过高就会发送邮件预警)
            self.Risk._check_margin_rate()
                # 2. 检测'币本位-维持保证金率'是否过高 (过高就会发送邮件预警)
            # self.Risk._check_margin_rate()
                # 3. 检测'全仓杠杆-风险率'是否过高 (过高就会发送邮件预警)
            # self.Risk._check_margin_rate()
                # 4. 检测'逐仓杠杆-风险率'是否过高 (过高就会发送邮件预警)
            # self.Risk._check_margin_rate()
        # 六. 需要每1小时执行的函数
        if self.timer == 20: # 当计时器过去20秒就开始执行 (每小时一次)
                # 检测'维持保证金率'是否过高 (过高就会发送邮件预警)
            # 1. 每小时定期还款:
                # i. 全仓杠杆的还款
            self.Risk._repay_bnb()
                # ii. 逐仓杠杆的还款
            # self.Risk._repay_bnb()

    def process_tick_event(self, event: Event) -> None:
        """
        用于处理tick事件的函数 (可以获取到所有实时推送的tick数据)
        """
        # tick = event.data
        # self.ticks[tick.vt_symbol] = tick
        # 暂时没想到要怎么利用起来...
        pass

    def process_clock(self):
        """
            function: 整时/分/秒的闹钟 (指定时间执行某些任务)
        """
        t = get_time()
        # print(t)
        # (hour, minute, second) = t.split(":")
        # if second == '00' and minute == '00':
        #     pass
        if (t == "00:00:10") or (t == "08:00:10") or (t == "16:00:10"):
            if self.pause_on_rugularTime:
                self.pause_all_robots(offset="OPEN") # 指定时间, 杀死open_robot

    def set_logger_level(self, level=10):
        self.logger.setLevel(level)  # 可以通过这种方式控制logger打印内容

    def create_sendOrderRobot(
            self, pair_name, offset, multiplier, target_spread_rate, trading_count, to_print=False, volume=None
        ):
        # 1. 创建一个robot对象
        robot = Robot(
            main_engine=self.main_engine, client=self,
            pair_name=pair_name, offset=offset,
            multiplier=multiplier, volume=volume,
            target_spread_rate=target_spread_rate, trading_count=trading_count, to_print=to_print
        )
        # 2. 将每个生成的robot对象都append进sc的字典中, 便于管理/调度
        if robot._offset == "OPEN":
            if self.open_d.get(robot._pair_name):
                self.open_d[robot._pair_name].update({robot.target_spread_rate : robot})
            else:
                self.open_d[robot._pair_name] = {}
                self.open_d[robot._pair_name].update({robot.target_spread_rate : robot})
        elif robot._offset == "CLOSE":
            if self.close_d.get(robot._pair_name):
                self.close_d[robot._pair_name].update({robot.target_spread_rate : robot})
            else:
                self.close_d[robot._pair_name] = {}
                self.close_d[robot._pair_name].update({robot.target_spread_rate : robot})
        return robot

    def get_df(self, type=1):
        # 通过df的形式, 方便查阅和管理各个robot
        if type == "open" or type == 1: # 简便表示
            self.open_df = pd.DataFrame(self.open_d).T
            return self.open_df
        elif type == "close" or type == 2:
            self.close_df = pd.DataFrame(self.close_d).T
            return self.close_df

    def batch_create_open_robot(
            self, pair_lst, multiplier=1, volume=None, target_spread_rate=0.005,
            trading_count=3, to_print=False
        ):
        """
            function: 批量新建'开仓robot'
                - 现有持仓中, 只要找到合适的价差率, 就可以提前平仓... (比如0.5%)
            args:
                pair_lst: ["BINANCE.LUNAUSDT", "BINANCE.ALPHAUSDT"]
            usage:
                # 把所有持仓合约都开启'开仓robot'
                pair_lst = self.Data.get_my_pair_lst()
                sc.batch_create_open_robot(pair_lst=pair_lst)
        """
        # 批量生成开仓robot
        for pair_name in pair_lst:
            self.create_robot(
                pair_name=pair_name, offset="OPEN", multiplier=multiplier, volume=volume,
                target_spread_rate=target_spread_rate, trading_count=trading_count, to_print=to_print
            )

    def batch_create_close_robot(
            self, pair_lst, multiplier=1, volume=None, target_spread_rate=0.001,
            trading_count=3, to_print=False
        ):
        """
            function: 批量新建'平仓robot'
                - 现有持仓中, 只要找到合适的价差率, 就可以提前平仓... (比如0.1%)
            args:
                pair_lst: ["BINANCE.LUNAUSDT", "BINANCE.ALPHAUSDT"]
            usage:
                # 把所有持仓合约都开启'平仓robot'
                pair_lst = sc.Data.get_my_pair_lst()
                sc.batch_create_close_robot(pair_lst=pair_lst)
        """
        # 批量生成平仓robot
        for pair_name in pair_lst:
            self.create_robot(
                pair_name=pair_name, offset="CLOSE", multiplier=multiplier, volume=volume,
                target_spread_rate=target_spread_rate, trading_count=trading_count, to_print=to_print
            )

    def active_all_robots(self, offset="BOTH", trading_count=None):
        """
            function: 激活当前所有的robot.. (比如8点刚过)
                offset:
                    "OPEN":   只激活'开仓robot'
                    "CLOSE":  只激活'平仓robot'
                    "BOTH":   同时激活'开/平仓robot'
                trading_count:
                    None:  不修改次数
                    1/2/3: 修改成相对应的次数
        """
        if offset == "OPEN" or offset == "BOTH":
            # 这里的 'd', 是指 {0.001:robot, 0.002:robot, 0.006:robot} (key是目标价差率)
            for pair_name, d in self.open_d.items():
                for target_spread_rate, robot in d.items():
                    logger.log(20, f"启动robot: {robot}")
                    robot.active(trading_count=trading_count)
        if offset == "CLOSE" or offset == "BOTH":
            for pair_name, d in self.close_d.items():
                for target_spread_rate, robot in d.items():
                    logger.log(20, f"启动robot: {robot}")
                    robot.active(trading_count=trading_count)

    def pause_all_robots(self, offset="BOTH", trading_count=None):
        """
            function: 停止当前所有的robot.. (比如8点刚过)
                offset:
                    "OPEN":   只停止'开仓robot'
                    "CLOSE":  只停止'平仓robot'
                    "BOTH":   同时停止'开/平仓robot'
                trading_count:
                    None:  不修改次数
                    1/2/3: 修改成相对应的次数
        """
        if offset == "OPEN" or offset == "BOTH":
            # 这里的 'd', 是指 {0.001:robot, 0.002:robot, 0.006:robot} (key是目标价差率)
            for pair_name, d in self.open_d.items():
                for target_spread_rate, robot in d.items():
                    logger.log(20, f"关闭robot: {robot}")
                    robot.pause(trading_count=trading_count)
        if offset == "CLOSE" or offset == "BOTH":
            for pair_name, d in self.close_d.items():
                for target_spread_rate, robot in d.items():
                    logger.log(20, f"关闭robot: {robot}")
                    robot.pause(trading_count=trading_count)

    def clear(self, offset="BOTH"):
        """
            function: 清空该SC内含的所有robot对象
                    (其实就是解决绑定关系, 让python内部的垃圾回收机制清除这部分对象的缓存)
        """
        if offset == "BOTH":
            self.pause_all_robots(offset="BOTH")
            self.open_d = {}
            self.close_d = {}
            self.open_df = ""
            self.close_df = ""
        elif offset == "OPEN":
            self.pause_all_robots(offset="OPEN")
            self.open_d = {}
            # self.close_d = {}
            self.open_df = ""
            # self.close_df = ""
        elif offset == "CLOSE":
            self.pause_all_robots(offset="CLOSE")
            # self.open_d = {}
            self.close_d = {}
            # self.open_df = ""
            self.close_df = ""


    def smart_close_position(self):
        """
            functions:
                - 当保证金率达到某个值时, 会自动平掉部分仓位. (选择价差率最小的币种平仓)
                - 可以自动选择币种, 自动小步调平仓

            notes:
                - 这个函数最好还是放到 SpreadClient 中实现.. (因为这操作和网关实际上没啥太大关系.... 或者放到oms中实现也行..)

        """
        pass







class SignalRobot():
    "产生信号机器人"
    pass


class SendOrderRobot():
    "下单机器人"
    def __init__(
        self, main_engine, client,
        base_qty=None, quote_qty=20, total_quote_qty=100, trading_count=None,

        pair_name="BINANCE.LUNAUSDT", offset="OPEN",
        target_spread_rate=0.005,
    ):
        """
            function: 把run函数包装成一个对象, 而不是函数形式, 这样方便管理...
            args:
                client: sc实例对象
                account_manager: 账户管理对象 (如果不使用 AccountManager 生成的sc对象, 就不会有这个属性)
                base_qty: 开仓的标的币数量 [特殊情况才会用到]:
                        因为每个币种价格差异过大, 每次都要计算数量很麻烦... (推荐: 改用'金额'来下单)
                        (如果在"CLOSE"平仓的时候传入'all', 则表示全部卖出!)
                quote_qty: 每次下单的金额(usdt) (计价币数量)
                total_quote_qty: 下单的总金额(usdt)
                trading_count: int型 0/1/2/3/4/5  (表示可以连续自动交易的次数...) (当被递减为0的时候, 不允许被交易)


                pair_name: # "BINANCE.LUNAUSDT"
                    以下变量由pair在self.pairs中获取:
                        exchange: # Exchange.BINANCE (是个对象! 不是字符串)
                        symbol: # ethusdt
                offset:
                    'OPEN': '开仓'套利币对
                    'CLOSE': '平仓'套利币对
        """
        # 1. 初始化vnpy中的组件
        self.main_engine = main_engine
        self.oms = main_engine.engines["oms"]
        self.Client = client
        self.am = self.Client.am # account_manager: 账户管理对象 (如果不使用 AccountManager 生成的sc对象, 就不会有这个属性)

        # 2. Robot中所需的初始变量
            # i. 不可变属性
        self._pair_name = pair_name.upper() # 每个robot的pair_name在创建时就定死了, 后续不允许修改!!
        self._offset = offset
            # ii. 可变属性 (外部可控制)
        self.multiplier = multiplier
        self.volume = volume # 一般不用volume, 但特殊情况还是需要精准的输入volume.. (此时volume优先)
        self.target_spread_rate = target_spread_rate
        self.trading_count = trading_count # 初始值为0 (代表禁止实盘交易)
        self.alive = False # 该robot对象通过一个alive变量决定它的生死... (而不是通过self.sc.pairs中的变量)
        self.to_print = to_print # 控制 self.Show.robot_print 是否继续打印...

        # 3. 挂载
        self.mount()

        # 4. 核验信息 (pair_name的3步走验证: 确保已经开始计算该币种的价差率了)
        self.Data._ensure_pairs(pair_lst=[pair_name]) # [注意]: 一定要再mount()挂载后, 才能执行这个函数


    def mount(self):
        "将am或者sc中的方法, 移植到本robot对象中"
        # 1. 如果am对象中存在main_account:
        if self.Client.am and self.Client.am.main_account:
            self.Data = self.Client.am.main_account.Data
            self.Trade = self.Client.am.main_account.Trade
            self.Risk = self.Client.am.main_account.Risk
            self.Show = self.Client.am.main_account.Show
        # 2. 不存在则用sc对象的方法来挂载:
        else:
            self.Data = self.Client.Data
            self.Trade = self.Client.Trade
            self.Risk = self.Client.Risk
            self.Show = self.Client.Show

    def __repr__(self):
        (pair_name, exchange_name, symbol, asset_name) = self.Data._split_pair_name(pair_name=self._pair_name)
        offset = self._offset
        m = self.multiplier
        r = self.target_spread_rate
        c = self.trading_count
        a = self.alive
        t = self.to_print
        txt = f"[{asset_name}] 乘数:{m}, 差率:{r}, 次数:{c}, alive:{a}"
        return txt

    def show(self):
        (pair_name, exchange_name, symbol, asset_name) = self.Data._split_pair_name(pair_name=self._pair_name)
        offset = self._offset
        m = self.multiplier
        r = self.target_spread_rate
        c = self.trading_count
        a = self.alive
        t = self.to_print
        txt = "-----------------------------------------------------\n"
        txt += f"[{offset} - {asset_name}]  交易乘数:{m}, 目标价差率:{r}, 剩余交易次数:{c}, alive:{a}, 打印:{t}\n"
        logger.log(30, txt)

    def run(self):
        """
            function:
                - 计算该实例中币种的'价差率', 并在'捕捉到某个指定的价差率'时, 立即用'市价单'下单 (指定是开仓or平仓)
                        (现货/合约双向下单)
                - 每次执行run(), 只能跑一个pair (所以现货和合约的gateway_name是固定的)
                - 使用'异步的方式'来执行run.. (这样可以在用一个ipython交互终端中, 执行多个run函数)
                    (两个选择: '子线程'or'子进程')

            todo: (优化方向)
                1. 当达到目标价差率之后, 等待3次0.1秒后, 再正式下单...否则容易被忽悠...
                    (观察到一些现象, 就是在毫秒级别的挂撤单, 严重影响盘口价差的真实性.. 而它速度太快导致我一般捕捉不到那种'变态的挂撤单')
                2. 函数自己计算每次的开仓数量... 不要每次都要我去计算100u大概是几个币... 函数自己捕获最新价去计算
                3. 可以设置一些开仓金额/开仓次数, 当达到目标价差率后, 自动多次开仓.. 不要变成一次性的run.. 频繁复制粘贴也比较麻烦..没有必要..明明它自己能重新开的..
                    # 其实可以不用打印吧... 它自己跑就行了?
                    # 或者开个多进程让它去跑... (这样我可以在同一个终端中开多个run()函数)
                4. 最好是多进程执行多个run函数...
                    1. 或者手动开启?:
                        手动的话可控一些, 想pause哪个就pause那个
                        (但其实有进程id, 我也可以控制多进程啊...也可以随意杀死某个进程)
                    2. 多进程跑的好处:
                        可以设置不同的交易量:
                            低价差率(0.3%): 交易金额在 50-100u左右 (成交快)
                            中价差率(0.35%): 交易金额在 300u左右
                            高价差率(0.4%): 交易金额在 500u左右 (赚的多)
                            # 如果是刚交割完, 还有8小时时间, 那就更多地设置在高价差率, 如果是接近交割了, 就需要更多挂在低价差率
                            # 前期: 这些倾向性的控制可以是手动控制;   后期: 这些细微的调整也可以由函数自发性的来完成
        """

        def _recur_run():
            # 启动该robot
            if self.alive == True:
                self.alive = False
                self.to_print = False
                time.sleep(1)
            self.alive = True
            # 开始打印该robot执行过程中的价差率
            if self.to_print:
                self.Show.robot_print(robot=self) # 通过子线程, 异步打印...
            # 初始化
            (pair_name, exchange_name, symbol, asset_name) = self.Data._split_pair_name(pair_name=self._pair_name)
            offset = self._offset
            record_lst = self.Data.record_dict[pair_name]

            try:
                # 循环获取最新的盘口数据, 并捕捉合适的'价差率'
                while True:
                    if (self.alive == False) or (self.trading_count == 0):
                        break

                    if offset == "OPEN":
                        # 通过main_cal计算的结果, 直接取数
                        spread_rate_open = self.Data.spread_rate_open_dict.get(asset_name)
                        # 1. 开仓: 做空卖出合约, 买入现货;
                        if (spread_rate_open >= self.target_spread_rate) and (self.trading_count >= 1):
                            # d的内容作为日志记录下来 (之后还要记录下ws推送中计算价差率所有的时间戳)
                            d = {
                                "offset" : offset, "time": datetime.now(),
                                "target_spread_rate" : self.target_spread_rate, "capture_spread_rate": f"{spread_rate_open:.2%}",
                                }
                            if self.volume:
                                volume = self.volume
                            else:
                                volume = self.Trade._cal_volume(pair_name=pair_name, multiplier=self.multiplier)
                                # if volume == 0:
                                #     raise Exception("计算得到的volume为0, 检查: 1.币价是否过高 2.是否有该币种的tick数据")
                            print(f"{symbol}-开仓数量: {volume}")
                            spot_success, futures_success = self.Client.Trade.two_sides_send_order(pair_name=pair_name, offset="OPEN", volume=volume) # 双边下单
                            if spot_success and futures_success:
                                msg = f"\n--------> 发出开仓请求!!! (币种:{symbol}, 开仓数量:{volume})\n"
                                logger.log(30, msg)
                                # d = {
                                #     "offset" : offset, "time": datetime.now(),
                                #     "target_spread_rate" : self.target_spread_rate, "capture_spread_rate": f"{spread_rate_open:.2%}",
                                #     }
                                self.Data.record_dict[pair_name].append(d)
                                self.trading_count -= 1 # 成功交易一笔后, 就把trading_count递减1, 减为0的时候停止交易.. (可以自行在控制台开启)
                                time.sleep(1) # 拉开两笔交易的间隔时间, 避免0.1s的时间太短而重复发送下单信号, 导致滑点过大...
                            else:
                                msg = ""
                                if not spot_success:
                                    msg += f"[报错]: 现货-{asset_name}: 下单失败...(非'全部成交')\n"
                                if not futures_success:
                                    msg += f"[报错]: 合约-{symbol}: 下单失败...(非'全部成交')"
                                raise Exception(msg)

                    elif offset == "CLOSE":
                        # 通过main_cal计算的结果, 直接取数
                        spread_rate_close = self.Data.spread_rate_close_dict.get(asset_name)
                        # 2. 平仓: 平空买入合约, 卖出现货;
                        if (spread_rate_close <= self.target_spread_rate) and (self.trading_count >= 1):
                            # d的内容作为日志记录下来 (之后还要记录下ws推送中计算价差率所有的时间戳)
                            d = {
                                "offset" : offset, "time": datetime.now(),
                                "target_spread_rate" : self.target_spread_rate, "capture_spread_rate": f"{spread_rate_close:.2%}",
                                }
                            if self.volume:
                                # 只有'平仓'的时候, 才有'all in', 开仓时候是没有的....
                                if self.volume == "all":
                                    volume = self.Trade.get_pair_volume(pair_name=pair_name)
                                else:
                                    volume = self.volume
                            else:
                                volume = self.Trade._cal_volume(pair_name=pair_name, multiplier=self.multiplier)
                            print(f"{symbol}-平仓数量: {volume}")
                            spot_success, futures_success = self.Client.Trade.two_sides_send_order(pair_name=pair_name, offset="CLOSE", volume=volume) # 双边下单
                            if spot_success and futures_success:
                                msg = f"\n--------> 发出平仓请求!!! (币种:{symbol}, 平仓数量:{volume})\n"
                                logger.log(30, msg)
                                # d = {
                                #     "offset" : offset, "time": datetime.now(),
                                #     "target_spread_rate" : self.target_spread_rate, "capture_spread_rate": f"{spread_rate_close:.2%}",
                                #     }
                                self.Data.record_dict[pair_name].append(d)
                                self.trading_count -= 1 # 成功交易一笔后, 就把trading_count递减1, 减为0的时候停止交易.. (可以自行在控制台开启)
                                time.sleep(1) # 拉开两笔交易的间隔时间, 避免0.1s的时间太短而重复发送下单信号, 导致滑点过大...
                            else:
                                msg = ""
                                if not spot_success:
                                    msg += f"[报错]: 现货-{asset_name}: 下单失败...(非'全部成交')\n"
                                if not futures_success:
                                    msg += f"[报错]: 合约-{symbol}: 下单失败...(非'全部成交')"
                                raise Exception(msg)

                    # 休眠0.1秒 (所以robot的捕捉频次是0.1s)
                    time.sleep(1)
                # 若退出循环后, 这两个属性都要改为False
                self.alive = False
                self.to_print = False

            except Exception as e:
                self.alive = False
                self.to_print = False
                raise Exception(e)
        t = threading.Thread(target=_recur_run) # 生成一个子线程去跑, 所以不影响主进程的运行
        t.start()

    def pause(self, trading_count=None):
        """
            function: 杀死该robot, 并按需给予一定的trading_count
            args:
                trading_count:
                    None:  不修改次数
                    0/1/2/3: 修改成相对应的次数
        """
        if trading_count:
            self.trading_count = trading_count
        # 把该robot杀死.. (其实就是让run函数退出循环)
        # (要想robot继续运行, 可以执行robot.run()函数;)
        # (但要注意的是, trading_count用完后, 必须重新装弹, 才能在run()中下单交易)
        self.alive = False

    def active(self, trading_count=None):
        """
            function: 激活该robot, 并按需给予一定的trading_count
            args:
                trading_count:
                    None:  不修改次数
                    1/2/3: 修改成相对应的次数
        """
        if trading_count:
            self.trading_count = trading_count
        self.run()



def __name__ == "__main__":

    am = AccountManager(main_account_name="LSH")
    gateway_setting_lst = [LSH_BINANCE_SETTING, ZL_BINANCE_SETTING]
    am.add_accounts(gateway_setting_lst=gateway_setting_lst)

    # am = AccountManager(main_account_name="LB")
    # gateway_setting_lst = [LB_BINANCE_SETTING]
    # am.add_accounts(gateway_setting_lst=gateway_setting_lst)
















#
