from logging import INFO
import threading
import multiprocessing
import sys
from datetime import datetime

# 这里的vnpy直接是导入site-packages里的python包. (而不是在我'量化'目录下的项目!!) (所以要修改的话, 去到源文件去改!!)
from vnpy.trader.setting import SETTINGS
from vnpy.event import EventEngine, Event
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

from kw618.k_finance.const import * # 导入币安api-key




class Robot():
    def __init__(self, spread_client):
        """
            function: 把run函数包装成一个对象, 而不是函数形式, 这样方便管理...
            args:
                spread_client: sc实例对象
        """
        self.sc = spread_client
        self.alive = False # 该robot对象通过一个alive变量决定它的生死... (而不是通过self.sc.pairs中的变量)
        self.trading_count = 0 # 初始值为0 (代表禁止实盘交易)

    def run(
            self, pair="BINANCE.ETHUSDT", trading_count=1,
            offset="OPEN", multiplier=1, alert_spread_rate=0.005,
            cycle_count=1000, sleep_time=0.1, to_check_balance=True, to_print=True
        ):
        """
            function:
                - 计算该实例中币种的'价差率', 并在'捕捉到某个指定的价差率'时, 立即用'市价单'下单 (指定是开仓or平仓)
                        (现货/合约双向下单)
                - 每次执行run(), 只能跑一个pair (所以现货和合约的gateway_name是固定的)
            args:
                pair: # "BINANCE.ETHUSDT"
                    以下变量由pair在self.pairs中获取:
                        exchange: # Exchange.BINANCE (是个对象! 不是字符串)
                        symbol: # ethusdt
                offset:
                    'OPEN': '开仓'套利币对
                    'CLOSE': '平仓'套利币对
                volume: 开仓数量 [被弃用]: 因为每个币种价格差异过大, 每次都要计算数量很麻烦... (改用'乘数'来表示)
                multiplier: 交易乘数
                    默认: 100u为基础单位.
                    交易乘积: 表示是基础单位的多少倍 (即: 0.1表示10u市值, 100表示10000u市值)
                            (通过交易乘数, 最终会计算出一个合理的'deal_count', 即: 实际用来开仓的volume)
                trading_count: int型 0/1/2/3/4/5  (表示可以连续自动交易的次数...) (当被递减为0的时候, 不允许被交易)
                cycle_count: 1000 (默认: 循环跑1000次, 就跳出循环)
                to_check_balance: True/False
                        (因为check一次需要浪费1ms的时间, 而套利的机会是毫秒级别的!! 当资金量足够的时候, 其实完全没有必要去check啊...)
                        (或者在run之前就测算好最多能交易多少volume, 并把这个volume记录在某个变量中, run执行中只要满足这个volume, 就可以执行交易..)
                            - 但问题是, 如果同时执行多个run(), 每个run又是不同币种, 上面的方法就不适用了...
                                (我们未来一定是要实现多币种同时在run的..)

            usage:
                eg1:
                    # 开始套利
                    symbol = "dentusdt"
                    sc.run(
                        pair=f"BINANCE.{symbol}", trading_count=1, offset="OPEN", volume=10,
                        alert_spread_rate=0.002, cycle_count=1000000, sleep_time=0.1
                    )

            todo: (优化方向)
                1. 当达到目标价差率之后, 等待3次0.1秒后, 再正式下单...否则容易被忽悠...
                    (观察到一些现象, 就是在毫秒级别的挂撤单, 严重影响盘口价差的真实性.. 而它速度太快导致我一般捕捉不到那种'变态的挂撤单')
                2. 函数自己计算每次的开仓数量... 不要每次都要我去计算100u大概是几个币... 函数自己捕获最新价去计算
                3. 可以设置一些开仓金额/开仓次数, 当达到目标价差率后, 自动多次开仓.. 不要变成一次性的run.. 频繁复制粘贴也比较麻烦..没有必要..明明它自己能重新开的..
                    # 其实可以不用打印吧... 它自己跑就行了?
                    # 或者开个多进程让它去跑... (这样我可以在同一个终端中开多个run()函数)
                4. 最好是多进程执行多个run函数...
                    1. 或者手动开启?:
                        手动的话可控一些, 想kill哪个就kill那个
                        (但其实有进程id, 我也可以控制多进程啊...也可以随意杀死某个进程)
                    2. 多进程跑的好处:
                        可以设置不同的交易量:
                            低价差率(0.3%): 交易金额在 50-100u左右 (成交快)
                            中价差率(0.35%): 交易金额在 300u左右
                            高价差率(0.4%): 交易金额在 500u左右 (赚的多)
                            # 如果是刚交割完, 还有8小时时间, 那就更多地设置在高价差率, 如果是接近交割了, 就需要更多挂在低价差率
                            # 前期: 这些倾向性的控制可以是手动控制;   后期: 这些细微的调整也可以由函数自发性的来完成
                5. 测试一下 check_balance() 函数的执行时间.... 我的交易都是毫秒级别的, 万一它浪费了我0.1秒, 我都血亏啊....
                        目前实测是 1ms, 看看怎么能优化它, 达到微秒级别?
                            (想想怎么优化这个函数的性能)

        """

        # 1. 初始化
        spot_lock = None # 初始化一个spot_lock.(当作'锁'?)
        futures_lock = None # 初始化一个spot_lock.(当作'锁'?)
        pair = pair.upper()
        pair_dict = self.sc.pairs.get(pair)
        if not pair_dict:
            self.sc.add_pair(pair=pair, to_subscribe=True)
            pair_dict = self.sc.pairs.get(pair)
        record_lst = self.sc.record_dict[pair]
        exchange = pair_dict.get("exchange") # Exchange.BINANCE
        self.trading_count = trading_count
        symbol = pair_dict.get("symbol").upper() # ethusdt
        exchange_name = pair_dict.get("exchange_name")
        if (f"{symbol.lower()}.{exchange_name}" not in list(self.sc.oms.ticks)) or \
            (f"{symbol.upper()}.{exchange_name}" not in list(self.sc.oms.ticks)):
            msg = f"tick数据还没订阅成功, 请通过add_pair函数订阅pair后, 再重试...."
            raise Exception(msg)
        volume = self.sc._cal_volume(pair=pair, multiplier=multiplier)
        asset_name = symbol[:-4] # "BTC", "ETH" 这种形式
        self.alive = True

        # 2. 循环获取最新的盘口数据, 并捕捉合适的'价差率'
        try:
            for count in range(cycle_count):
                # 3. 通过pair, 计算价差率
                spread_open, spread_rate_open, spread_close, spread_rate_close = self.sc.cal_spread_rate(pair=pair)

                # 4. 打印'价差率'
                if to_print:
                    # i. 开仓价差率-分阶段打印
                    if offset == 'OPEN':
                        if spread_rate_open < 0.0023:
                            if spot_lock != '0':
                                msg = f'[{symbol} - 开仓]: 价差率在一个无聊的区间...'
                                logger.log(20, msg)
                                spot_lock = '0'
                        elif 0.0023 <= spread_rate_open < 0.003:
                            if spot_lock != '1':
                                msg = f'[{symbol} - 开仓]: 价差率区间: [0.23% 至 0.30%]   ({round(spread_rate_open*100, 4)}%)'
                                logger.log(20, msg)
                                spot_lock = '1'
                        elif 0.0030 <= spread_rate_open < 0.0035:
                            if spot_lock != '2':
                                msg = f'[{symbol} - 开仓]: 价差率区间: [0.30% 至 0.35%]   ({round(spread_rate_open*100, 4)}%)'
                                logger.log(20, msg)
                                spot_lock = '2'
                        elif 0.0035 <= spread_rate_open < 0.0040:
                            if spot_lock != '3':
                                msg = f'[{symbol} - 开仓]: 价差率区间: [0.35% 至 0.40%]   ({round(spread_rate_open*100, 4)}%)'
                                logger.log(20, msg)
                                spot_lock = '3'
                        elif 0.0040 <= spread_rate_open < 0.0045:
                            if spot_lock != '4':
                                msg = f'[{symbol} - 开仓]: 价差率区间: [0.40% 至 0.45%]   ({round(spread_rate_open*100, 4)}%)'
                                logger.log(20, msg)
                                spot_lock = '4'
                        elif 0.0045 <= spread_rate_open < 0.0050:
                            if spot_lock != '5':
                                msg = f'[{symbol} - 开仓]: 价差率区间: [0.45% 至 0.50%]   ({round(spread_rate_open*100, 4)}%)'
                                logger.log(20, msg)
                                spot_lock = '5'
                        else:
                            if spot_lock != '6':
                                msg = f'[{symbol} - 开仓]: 价差率区间: [ >= 0.50% ]   ({round(spread_rate_open*100, 4)}%)'
                                logger.log(20, msg)
                                spot_lock = '6'

                    # ii. 平仓价差率-分阶段打印
                    if offset == 'CLOSE':
                        if 0.0030 <= spread_rate_close:
                            if futures_lock != '0':
                                msg = f'[{symbol} - 平仓]: 价差率在一个无聊的区间...'
                                logger.log(20, msg)
                                futures_lock = '0'
                        elif 0.0020 <= spread_rate_close < 0.003:
                            if futures_lock != '1':
                                msg = f'[{symbol} - 平仓]: 价差率区间: [0.20% 至 0.30%]   ({round(spread_rate_close*100, 4)}%)'
                                logger.log(20, msg)
                                futures_lock = '1'
                        elif 0.0010 <= spread_rate_close < 0.0020:
                            if futures_lock != '2':
                                msg = f'[{symbol} - 平仓]: 价差率区间: [0.10% 至 0.20%]   ({round(spread_rate_close*100, 4)}%)'
                                logger.log(20, msg)
                                futures_lock = '2'
                        elif 0.0005 <= spread_rate_close < 0.0010:
                            if futures_lock != '3':
                                msg = f'[{symbol} - 平仓]: 价差率区间: [0.05% 至 0.10%]   ({round(spread_rate_close*100, 4)}%)'
                                logger.log(20, msg)
                                futures_lock = '3'
                        elif 0.0000 <= spread_rate_close < 0.0005:
                            if futures_lock != '4':
                                msg = f'[{symbol} - 平仓]: 价差率区间: [0.00% 至 0.05%]   ({round(spread_rate_close*100, 4)}%)'
                                logger.log(20, msg)
                                futures_lock = '4'
                        elif -0.0005 <= spread_rate_close < 0.0000:
                            if futures_lock != '5':
                                msg = f'[{symbol} - 平仓]: 价差率区间: [-0.05% 至 0.00%]   ({round(spread_rate_close*100, 4)}%)'
                                logger.log(20, msg)
                                futures_lock = '5'
                        elif -0.0010 <= spread_rate_close < 0.0005:
                            if futures_lock != '5':
                                msg = f'[{symbol} - 平仓]: 价差率区间: [-0.10% 至 -0.05%]   ({round(spread_rate_close*100, 4)}%)'
                                logger.log(20, msg)
                                futures_lock = '5'
                        else:
                            if futures_lock != '6':
                                msg = f'[{symbol} - 平仓]: 价差率区间: [ < -0.10% ]   ({round(spread_rate_close*100, 4)}%)'
                                logger.log(20, msg)
                                futures_lock = '6'

                # 5. 下单: (达到目标价差率)
                if self.trading_count:
                    if (offset == 'OPEN') and (spread_rate_open >= alert_spread_rate):
                        # 1. 开仓: 做空卖出合约, 买入现货;
                        # alert_msg = f"[提醒] =====>  当前'开仓'价差率: {round(spread_rate_open*100, 4)}, 大于{alert_spread_rate*100}%, 适合执行'开仓'操作....\n\n"
                        # logger.log(30, alert_msg)
                        self.sc.two_sides_send_order(pair=pair, offset="OPEN", volume=volume, to_check_balance=to_check_balance) # 双边下单
                        msg = f"\n--------> 开仓成功!!! (币种:{symbol}, 开仓数量:{volume})\n"
                        logger.log(30, msg)
                        d = {
                            "spread_open" : spread_open, "spread_close" : spread_close,
                            "spread_rate_open" : spread_rate_open, "spread_rate_close" : spread_rate_close,
                            "offset" : offset, "alert_spread_rate" : alert_spread_rate,
                            }
                        record_lst.append(d)
                        self.trading_count -= 1 # 成功交易一笔后, 就把trading_count递减1, 减为0的时候停止交易.. (可以自行在控制台开启)
                        time.sleep(1) # 拉开两笔交易的间隔时间, 避免0.1s的时间太短而重复发送下单信号, 导致滑点过大...

                    elif (offset == 'CLOSE') and (spread_rate_close <= alert_spread_rate):
                        # 2. 平仓: 平空买入合约, 卖出现货;
                        # alert_msg = f"[提醒] =====>  当前'平仓'价差率: {round(spread_rate_close*100, 4)}, 小于{alert_spread_rate*100}%, 适合执行'平仓'操作....\n\n"
                        # logger.log(30, alert_msg)
                        self.sc.two_sides_send_order(pair=pair, offset="CLOSE", volume=volume, to_check_balance=to_check_balance) # 双边下单
                        msg = f"\n--------> 平仓成功!!! (币种:{symbol}, 平仓数量:{volume})\n"
                        logger.log(30, msg)
                        d = {
                            "spread_open" : spread_open, "spread_close" : spread_close,
                            "spread_rate_open" : spread_rate_open, "spread_rate_close" : spread_rate_close,
                            "offset" : offset, "alert_spread_rate" : alert_spread_rate,
                            }
                        record_lst.append(d)
                        self.trading_count -= 1 # 成功交易一笔后, 就把trading_count递减1, 减为0的时候停止交易.. (可以自行在控制台开启)
                        # 拉开两笔交易的间隔时间, 避免0.1s的时间太短而重复发送下单信号, 导致滑点过大...
                        # (且: 连下两笔的速度过快, 余额还没更新, 容易出现check_balance误以为有钱... 导致交易出错...可能只成交了一腿...)
                        time.sleep(1) # 为啥这个睡眠没起到作用的感觉....????
                # 休眠
                time.sleep(sleep_time)
                if not self.alive: # 当alive为False时, 逻辑上杀死该函数...
                    break
        except Exception as e:
            # 若同时有很多个该pair的run函数在执行, 这几个线程都会同时被杀死...
            # (即: 一旦一个线程报错, 其他同pair的线程也会死掉)
            self.alive = False
            raise Exception(e)

    def async_run(
            self, async_type="process", pair="BINANCE.ETHUSDT", trading_count=1,
            offset="OPEN", multiplier=1, alert_spread_rate=0.005,
            cycle_count=1000, sleep_time=0.1, to_check_balance=True, to_print=True
        ):
        """
            function: 使用'异步的方式'来执行run.. (这样可以在用一个ipython交互终端中, 执行多个run函数)
                    (两个选择: '子线程'or'子进程')
            args:
                - async_type: "process" or "thread"
        """
        # 通过子线程在执行run (可在终端控制trading变量来决定run是否被允许交易...)
        if async_type == "thread":
            t = threading.Thread(
                target=self.sc.run,
                kwargs=({
                    'pair' : pair,
                    'offset' : offset,
                    'alert_spread_rate' : alert_spread_rate,
                    'multiplier' : multiplier,
                    'trading_count' : trading_count,
                    'to_check_balance' : to_check_balance,
                    'cycle_count' : cycle_count,
                    'sleep_time' : sleep_time,
                    'to_print' : to_print,
                    })
                )
            t.start()

        elif async_type == "process":
            t = multiprocessing.Process(
                target=self.sc.run,
                kwargs=({
                    'pair' : pair,
                    'offset' : offset,
                    'alert_spread_rate' : alert_spread_rate,
                    'multiplier' : multiplier,
                    'trading_count' : trading_count,
                    'to_check_balance' : to_check_balance,
                    'cycle_count' : cycle_count,
                    'sleep_time' : sleep_time,
                    'to_print' : to_print,
                    })
                )
            t.start()



class DataSystem():
    def __init__(self, main_engine):
        """
            notes:
                - 1. 数据系统
        """
        # 1. 初始化vnpy中的组件
        self.main_engine = main_engine
        self.oms = main_engine.engines["oms"]
        self.spot_rest_api = main_engine.gateways.get("BINANCE").rest_api
        self.futures_rest_api = main_engine.gateways.get("BINANCES").rest_api
        self.spot_trade_ws_api = main_engine.gateways.get("BINANCE").trade_ws_api
        self.futures_trade_ws_api = main_engine.gateways.get("BINANCES").trade_ws_api
        self.spot_market_ws_api = main_engine.gateways.get("BINANCE").market_ws_api
        self.futures_market_ws_api = main_engine.gateways.get("BINANCES").market_ws_api

        # 2. 初始化SC所需用到的变量
        self.record_dict = {} # 用于记录价差率相关数据
        self.pairs = {} # 套利币对 (允许有多个币对)
        self.oms.futures_account = {} # 存放合约账户相关的重要信息 (关键是"维持保证金率"!!)
        self.spread_rate_open_dict = {}
        self.spread_rate_close_dict = {}
        self.funding_rate_dict = {}

    def split_pair(self, pair_name):
        """
            note: 拆分'交易所名称'和'币对名称', 返回的都是大写
        """
        # 1. 拆分pair名称
        exchange_name, symbol = pair_name.split(".")
        exchange_name = exchange_name.upper()
        symbol = symbol.upper()
        return exchange_name, symbol

    def check_pair_name(self, pair_name):
        """
            function: 鉴于我经常把这个symbol/exchange拼错, 导致的各种bug... 提前先在oms.contract中检查...
            return: ("BINANCE", "ETHUSDT", Exchange.BINANCE) # 返回一个元组
        """
        # 1. 拆分: 得到'交易所'和'币对'
        exchange_name, symbol = self.split_pair(pair_name=pair_name)

        # 2. '交易所名称'检查
        for ex in Exchange:
            if exchange_name == ex.name:
                exchange = ex
        if not exchange:
            msg = f"没有该交易所, 请检查..."
            raise Exception(msg)

        # 2. '币对名称'检查
        contracts_lst = list(self.oms.contracts)
        success = False
        for contract in contracts_lst:
            _sy, _ex = contract.split(".") # contract: 'wbtceth.BINANCE'
            if symbol == _sy:
                success = True
        if not success:
            msg = f"oms.contract中不存在该symbol: {symbol}"
            raise Exception(msg)
        return (exchange_name, symbol, exchange) # ("BINANCE", "ETHUSDT", Exchange.BINANCE) 返回一个元组


    def get_last_price(self, pair_name, type="spot"):
        """
            note: 默认获取的是现货的价格
        """
        (exchange_name, symbol, exchange) = self.check_pair_name(pair_name=pair_name)
        if type == "spot":
            return self.oms.ticks[f"{symbol.lower()}.{exchange_name}"].last_price
        elif type == "futures":
            return self.oms.ticks[f"{symbol.upper()}.{exchange_name}"].last_price





class TradeSystem():
    pass

class RiskControlSystem():
    pass

class DispatchSystem():
    pass

class FinanceSystem():
    pass

class VisualSystem():
    pass




class SpreadClient():
    """
        sc框架解析:
            数据系统:
                (指: 将盘口挂单数据计算成盘口价差率, 方便robot执行)
                (使用统一的数据来源!! 这样各个robot之间没有数据误差, 后期若发现价差率计算有bug也方便修改)
                1. 数据获取
                2. 数据计算
                3. 数据打印
                4. 数据调用
            交易系统:
                1. 单边下单
                2. 双边下单
                3. 余额核验
            风控系统:
                1. 保证金率风控
                2. 邮件模块
            调度系统: [核心!!] [其实就是'量化策略'or'程序化策略']
                1. 创造各种类型的robot [开仓]/[平仓]
                2. 调度robot [调仓]
                3. 销毁robot [停止操作]
                (如果开仓/平仓, 开/平多少, 什么时候调, 调成什么币种?? 一系列都是问题, 这才是整个策略最核心的部分!!) [研究策略和算法]
                (多线程执行, 所以在线程管理和线程安全问题上也要重视)
            财务系统:
                1. 计算开/平仓价差率的盈亏
                2. 呈现每日的资金费用收入
            可视化系统:
                1. 将各种重要指标数据呈现在web端??
                (收益曲线?)

            思考: 这几个系统要分别写成'类'的形式吗? (还是全部塞在SpreadClient类中?? 优劣??)

    """

    def __init__(self, main_engine):
        """
            args:
                symbol: 应该做到'大小写不敏感', 需要在函数内部实现'大小写逻辑控制' (一般传入小写的货币对即可)
        """
        self.main_engine = main_engine
        self.oms = main_engine.engines["oms"]
        self.spot_rest_api = main_engine.gateways.get("BINANCE").rest_api
        self.futures_rest_api = main_engine.gateways.get("BINANCES").rest_api
        self.spot_trade_ws_api = main_engine.gateways.get("BINANCE").trade_ws_api
        self.futures_trade_ws_api = main_engine.gateways.get("BINANCES").trade_ws_api
        self.spot_market_ws_api = main_engine.gateways.get("BINANCE").market_ws_api
        self.futures_market_ws_api = main_engine.gateways.get("BINANCES").market_ws_api


        self.record_dict = {} # 用于记录价差率相关数据
        self.pairs = {} # 套利币对 (允许有多个币对)
        self.oms.futures_account = {} # 存放合约账户相关的重要信息 (关键是"维持保证金率"!!)
        self.spread_rate_open_dict = {}
        self.spread_rate_close_dict = {}
        self.funding_rate_dict = {}


        # 用于停止子线程的开关
        # self.stop_threads = False # 用于杀死所有正在跑的子线程...  (相比于其他kill的方法都要优雅...)
        self.kill_live_update_funding_rate = False # 子线程功能: 每隔5s更新币种的资金费率
        self.kill_print_spread_rate = False # 子线程功能: 计算币种的价差率, 并打印输出
        self.kill_print = False # 子线程功能: 打印各个币种的 资金费率and开平仓价差率
        self.show_futures_index()
        self.subscribe_myPosition()


        self.Data = DataSystem(main_engine)
        self.Trade = TradeSystem()
        self.Risk = RiskControlSystem()
        self.Dispatch = DispatchSystem()
        self.Finance = FinanceSystem()
        self.Visual = VisualSystem()



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

        [提示]: 该函数的功能已经移植到 vnpy里的binance_gateway模块内
                futures_rest_api.keep_margin_rate(wait=False)
                futures_rest_api.get_futures_index_text()


        """
        "[该函数已经转移]"
        # self.futures_rest_api.query_account()
        # # 因为上面的请求是异步的, 而后面的处理都是基于上面的req返回的数据的, 所以必须要等待它请求完成才能继续
        # print("睡眠2秒, 等待请求最新的合约账户数据...")
        # time.sleep(2)
        # # 我放弃了...: 下面这些值赋值回给oms有两个问题: 1.显得鸡肋  2.数据更新不及时(oms.accounts的数据是ws实时更新的...)
        # # usdt_account = self.oms.accounts["BINANCES.USDT"]
        # # self.oms.futures_account["usdt_balance"] = usdt_account.balance # 钱包余额
        # # self.oms.futures_account["pnl"] = usdt_account.pnl # 未实现浮动盈亏
        # # self.oms.futures_account["marginBalance"] = usdt_account.marginBalance # 保证金余额
        # # self.oms.futures_account["maintMargin"] = usdt_account.maintMargin # 维持保证金
        # # self.oms.futures_account["availableBalance"] = usdt_account.availableBalance # 可用划转余额
        # # self.oms.futures_account["margin_rate"] = self.oms.futures_account["maintMargin"] / self.oms.futures_account["marginBalance"]
        #
        # # 1. 获取基础数据
        # usdt_account = self.oms.accounts["BINANCES.USDT"] # 如果取不出数, 可能是网络问题导致上面的req请求还没得到resp (异步就有这种问题...)
        # usdt_balance = usdt_account.balance # 钱包余额
        # pnl = usdt_account.pnl # 未实现浮动盈亏
        # marginBalance = usdt_account.marginBalance # 保证金余额
        # maintMargin = usdt_account.maintMargin # 维持保证金
        # availableBalance = usdt_account.availableBalance # 可用划转余额
        # sum_open_notional = self.cal_sum_open_notional() # 开仓名义市值的总和
        #
        # # 2. 计算4个核心爆仓指标
        #     # i. 维持保证金率
        # margin_rate = maintMargin / marginBalance
        #     # ii. 名义浮盈率
        # notional_pnl_rate = pnl / sum_open_notional
        #     # iii. 开仓杠杆倍数
        # open_leverage = sum_open_notional / usdt_balance
        #     # iv. 实际浮盈率
        # pnl_rate = pnl / usdt_balance
        #
        # # 3. 输出
        # txt =f"""
        # ===============================================
        # 1.【维持保证金率---爆仓率】: {margin_rate:.3%}
        # 2.【名义浮盈率】: {notional_pnl_rate:.3%}
        # 3.【开仓杠杆倍数】: {open_leverage:.2f}
        # 4.【实际浮盈率】: {pnl_rate:.3%}
        # -----------------------------------------------
        # USDT钱包余额 : {usdt_balance:.2f}
        # 开仓名义市值总和 : {sum_open_notional:.2f}
        # 未实现盈亏 : {pnl:.2f}
        # 保证金余额 : {marginBalance:.2f}
        # 维持保证金 : {maintMargin:.2f}
        # 可用划转余额 : {availableBalance:.2f}
        # ===============================================
        # """
        # print(txt)

        self.futures_rest_api.keep_margin_rate(wait=False)
        self.futures_rest_api.get_futures_index_text()

    def subscribe_myPosition(self):
        """
            function: 订阅我自己持仓的这几个币种...
        """
        # 1. 获取当前持仓的所有币种
        position_name_lst = list(self.oms.positions.keys())
        pair_lst = []
        for position_name in position_name_lst:
            symbol, exchange_name, direction = position_name.split(".") # ETHUSDT, BINANCE, '空'
            pair_name = f"{exchange_name}.{symbol.upper()}"
            pair_lst.append(pair_name)

        # 2. 开始订阅所有币种的tick数据
        self.add_pairs(pair_lst=pair_lst, to_subscribe=True)
        print("延迟睡眠15s, 确保所有币种的tick都已经推送...")
        time.sleep(10)
        msg = f"当前已经订阅tick的pair:\n{list(self.oms.ticks)}"
        logger.log(10, msg)
        msg = f"准备开始获取tick数据, 计算价差率..."
        logger.log(10, msg)

        # 3. 同时计算所有币种的价差率 (使用多线程)
        self.print_all_pair_spread_rate(to_print=False, cycle_count=1000000000)

    def show_pairs(self):
        "用df的形式展示 pairs的信息"
        self.pairs_df = pd.DataFrame(self.pairs)
        return self.pairs_df

    def cal_sum_open_notional(self):
        "[该函数已经转移]"
        "计算: 开仓名义市值的总和"
        sum_open_notional = 0
        for k, v in self.oms.positions.items():
            sum_open_notional += abs(v.volume * v.price)
        return round(sum_open_notional, 6)

    def get_margin_rate(self):
        """
            function: 获取'维持保证金率'

            todo:
                - 以后每隔1分钟检查一次保证金率, 如果超过70%, 则自动平掉部分仓位
                    (仓位选择: 选择价差率最低的币种, 小批量平仓, 死循环, 直到保证金率低于70%)
        """
        "[该函数已经转移]"
        # self.futures_rest_api.query_account()
        # # 因为上面的请求是异步的, 而后面的处理都是基于上面的req返回的数据的, 所以必须要等待它请求完成才能继续
        # print("睡眠2秒, 等待请求最新的合约账户数据...")
        # time.sleep(2)
        # margin_rate = self.oms.accounts["BINANCES.USDT"].maintMargin / self.oms.accounts["BINANCES.USDT"].marginBalance

        self.futures_rest_api.keep_margin_rate(wait=False)
        margin_rate = self.oms.futures_index.get("margin_rate")
        return margin_rate

    def check_pair_name(self, pair):
        """
            function: 鉴于我经常把这个symbol/exchange拼错, 导致的各种bug... 提前先在oms.contract中检查...
            return: "BINANCE", "ETHUSDT"
        """

        # 1. '交易所'检查
        pair = pair.upper()
        exchange_name, symbol = pair.split(".")
        for ex in Exchange:
            if exchange_name == ex.name:
                exchange = ex
        if not exchange:
            msg = f"没有该交易所, 请检查..."
            raise Exception(msg)

        # 2. '币种'检查
        contracts_lst = list(self.oms.contracts)
        success = False
        for contract in contracts_lst:
            _sy, _ex = contract.split(".") # contract: 'wbtceth.BINANCE'
            if symbol == _sy:
                success = True
        if not success:
            msg = f"oms.contract中不存在该symbol: {symbol}"
            raise Exception(msg)
        return exchange_name, symbol, exchange

    def check_pair_pos(self, pair_dict):
        """
            function: 核对pair的'对冲账户是否数量匹配'
            args:
                - pair_dict: self.pairs[pair] 得到的那个dict
            notes: - 一般用在add_pair中, 不单独对外使用
        """
        symbol = pair_dict.get("symbol") # "ethusdt"
        gateway_name_spot = pair_dict.get("gateway_name_spot") # "BINANCE"
        gateway_name_futures = pair_dict.get("gateway_name_futures") # "BINANCES"
        exchange_name = pair_dict.get("exchange_name") # "BINANCE"
            # i. 该币种的现货余额
        symbol_account = self.oms.accounts.get(f"{gateway_name_spot}.{symbol.upper()[:-4]}") # 这里是ETH不是ETHUSDT, 所以把后面4个字符删掉
        if symbol_account:
            spot_balance = symbol_account.balance
        else:
            spot_balance = 0 # 如果oms中没有该account, 则为0
            # ii. 该币种的合约持仓
        symbol_position = self.oms.positions.get(f"{symbol.upper()}.{exchange_name}.空")
        if symbol_position:
            futures_volume = symbol_position.volume
        else:
            futures_volume = 0 # 如果oms中没有该position, 则为0
            # iii. 现货和合约的volume总和  (做空的合约的volume为负数)
        sum_volume = spot_balance + futures_volume
        pair_dict["sum_volume"] = sum_volume
        pair_dict["spot_balance"] = spot_balance
        pair_dict["futures_volume"] = futures_volume
        if sum_volume == 0:
            pair_dict["equal_volume"] = True
        else:
            pair_dict["equal_volume"] = False

    def check_all_pair_pos(self):
        """
            function: 核对self.pairs中的每个币种的'对冲账户是否数量匹配'
            return: 每个pair的sum_volume
                eg:
                    {'BINANCE.CHZUSDT/sum_volume': -10.0,
                     'BINANCE.aliceUSDT/sum_volume': 5.3865379000000075}
        """
        # 遍历self.pairs, 核对这些pair的期现volume是否相等
        for pair_name, pair_dict in self.pairs.items():
            self.check_pair_pos(pair_dict=pair_dict)
        d = {}
        for pair_name, pair_dict in self.pairs.items():
            d.update({f"{pair_name}/sum_volume" : pair_dict.get("sum_volume")})
        return d

    def subscribe(self, pair):
        """
            function: 同时订阅'现货'和'期货'的tick数据 (都包含了'最优挂单信息')
                (前提: 要先add_pair(), 不能单独执行)
            args:
                symbol: 大小写不敏感 (一般小写即可)   # "ethusdt"

        """

        # 1. 初始化
        main_engine = self.main_engine
        pair_dict = self.pairs.get(pair)
        gateway_name_spot = pair_dict.get("gateway_name_spot") # BINANCE
        gateway_name_futures = pair_dict.get("gateway_name_futures") # BINANCES
        symbol = pair_dict.get("symbol") # ethusdt
        exchange = pair_dict.get("exchange") # Exchange.BINANCE (对象)
        exchange_name = pair_dict.get("exchange_name") # "BINANCE"

        # 2. 发起tick订阅
        while True:
            # i. 如果oms.ticks中有该tick数据, 则不重复subscribe
                # 当oms.ticks中同时存在 '现货'和'合约'的tick数据后, 才证明该函数订阅成功!
            msg = f"当前已经订阅tick的pair:\n{list(self.oms.ticks)}"
            logger.log(10, msg)
            if f"{symbol.lower()}.{exchange_name}" in list(self.oms.ticks) and f"{symbol.upper()}.{exchange_name}" in list(self.oms.ticks):
                time.sleep(4) # tick数据有了, 但是可能没有'最优挂单'数据??? 所以睡眠久一些, 让请求有时间去完成整个订阅过程
                # 3. 实时更新资金费率
                self.live_update_funding_rate()
                return
            # ii. 如果oms.ticks中没有该tick数据, 则开始执行subscribe
            else:
                print(f"等待订阅 pair : {pair} 的tick数据... (直到订阅成功才会睡醒...)")
                    # i. 订阅'现货'的tick数据
                req = SubscribeRequest(symbol=symbol.lower(), exchange=exchange)
                main_engine.subscribe(req, gateway_name=gateway_name_spot)
                    # ii. 订阅'合约'的tick数据
                time.sleep(2) # 多个请求不要同时发送, 否则会出现各种莫名其妙的bug.... 多个请求之间一般都要睡眠一段时间比较好...
                req = SubscribeRequest(symbol=symbol.upper(), exchange=exchange)
                main_engine.subscribe(req, gateway_name=gateway_name_futures)
                time.sleep(4)
        return

    def subscribe_many(self, pair_lst=["BINANCE.BTCUSDT", "BINANCE.ETHUSDT"]):
        """
            notes:
                - 使用 futures_market_ws_api, spot_market_ws_api 中改写的 subscribe_many 很方便就可以同时订阅多币种
                - 这里不检验 pair的书写正确性, 是因为在 add_pairs中已经检测过了...

            问题:
                - 发现同时订阅多个币种的时候, 会存在一个问题: 很多币种的tick数据更新很慢...延迟有好几秒的...
                    可能的原因: 1.网络延迟问题...(难以改善) 2.币安服务器问题(没办法解决,别人也一样) 3.订阅数量过多的问题(那只能减少同时订阅币种数)
                    解决方案: 可以在阿里云上试试网速, 如果延迟还是很久则只能通过订阅'单一币种'或'少数几个核心币种'方式来玩策略了....
        """

        lower_symbol_lst = [pair_name.split(".")[1].lower() for pair_name in pair_lst]
        upper_symbol_lst = [pair_name.split(".")[1].upper() for pair_name in pair_lst]
        # 2. 发起订阅
        self.spot_market_ws_api.subscribe_many(lower_symbol_lst)
        self.futures_market_ws_api.subscribe_many(upper_symbol_lst)
        # 3. 等待异步订阅完成
        print("睡眠6秒, 等待所有币种异步订阅完成")
        time.sleep(6) #
        msg = f"当前已经订阅tick的pair:\n{list(self.oms.ticks)}"
        logger.log(10, msg)
        # 4. 实时更新资金费率
        self.live_update_funding_rate()

    def live_update_funding_rate(self, interval=5):
        """
            function: 实时更新各个币种的'资金费率'到 self.pairs中 (使用子线程在默默不断的更新)
            args:
                interval: 间隔多少秒更新一次 (以'秒'为单位) # type: int
        """
        def foo(interval):
            self.kill_live_update_funding_rate = False
            while True:
                ticks = self.oms.ticks
                for k, v in ticks.items():
                    symbol, exchange_name = k.split(".")
                    asset = symbol[:-4]
                    pair_name = f"{exchange_name}.{symbol}" # BINANCE.ethusdt是现货; BINANCE.ETHUSDT是合约; (只有大写的合约才有'资金费率')
                    if pair_name in self.pairs:
                        self.pairs[pair_name]["funding_rate"] = v.funding_rate # 将oms.ticks中'funding_rate', 更新到 self.pairs中
                        self.funding_rate_dict.update({asset:v.funding_rate})
                # print('live更新资金费率, 睡眠5s....')
                time.sleep(interval) # 每隔一段时间更新一下资金费率
                if self.kill_live_update_funding_rate: # 可以用于杀死子线程
                    break
        t = threading.Thread(target=foo, kwargs=({'interval':interval}))
        t.start()

    def add_pair(self, pair="BINANCE.ETHUSDT", to_subscribe=False):
        """
            function: 添加pair, 同时订阅该pair的 '现货and合约' 的tick数据
            args:
                pair: # BINANCE.ETHUSDT
                to_subscribe: True/False # 是否需要订阅tick数据(最优挂单信息)
            notes:
                - # exchange_name一定是大写的. (而symbol可能大写, 可能小写)
        """
        # 1. 核对该'pair'输入无误!!
        exchange_name, symbol, exchange = self.check_pair_name(pair=pair)

        # 2. 初始化一些数据
        gateway_name_spot = exchange_name
        gateway_name_futures = exchange_name + "S"
        vt_symbol_spot = f"{symbol.lower()}.{exchange_name}"
        vt_symbol_futures = f"{symbol.upper()}.{exchange_name}"
        symbol_spot = symbol.lower()
        symbol_futures = symbol.upper()
        symbol = symbol.lower()
        self.pairs.update(
            {
                pair : {
                    "gateway_name_spot" : gateway_name_spot, # BINANCE
                    "gateway_name_futures" : gateway_name_futures, # BINANCES
                    "vt_symbol_spot" : vt_symbol_spot, # ethusdt.BINANCE
                    "vt_symbol_futures" : vt_symbol_futures, # ETHUSDT.BINANCE
                    "symbol_spot" : symbol_spot, # ethusdt; (同vt_symbol_spot前半段)
                    "symbol_futures" : symbol_futures, # ETHUSDT; (同vt_symbol_futures前半段)
                    "symbol" : symbol, # ethusdt; (用小写来作为symbol的一般通用形式)
                    "exchange" : exchange, # Exchange.BINANCE (是个对象)
                    "exchange_name" : exchange_name, # 'BINANCE' (是个字符串)
                    # "trading" : False, # 用于判断是否需要开启实盘交易...
                    "trading_count" : 0, # 用于判断是否需要开启实盘交易... (用数字表示剩余可以交易的次数..)
                    # 控制执行该pair的run函数的开关! (设为True, 则立马停止run函数) (不是真的直接杀死, 而是逻辑上的控制, 停止它循环执行)
                    # "kill" : False,
                    "alive" : False, # 表示run函数是否还在'异步执行中'...
                    "equal_volume" : False, # 用于判断某个pair的'期现数量是否相等'
                    "sum_volume" : -999,
                    "funding_rate" : 0,
                }
            }
        )
        self.record_dict.update({pair:[]})

        # 3. 核对pair的 '期现volume是否匹配'
        self.check_pair_pos(pair_dict=self.pairs[pair])

        # 4. 订阅该'pair'的tick'最优挂单'数据 (现货和合约)
        if to_subscribe:
            self.subscribe(pair=pair) # 订阅该'套利对'的现货和期货的tick数据

    def add_pairs(self, pair_lst=["BINANCE.BTCUSDT", "BINANCE.ETHUSDT"], to_subscribe=False):
        """
            function: 同时添加多个pair, 同时订阅多个pair的 '现货and合约' 的tick数据
                        (完全改装于 add_pair函数)
            args:
                pair_lst: # ["BINANCE.ETHUSDT", "BINANCE.BTCUSDT"]
                to_subscribe: True/False # 是否需要订阅tick数据(最优挂单信息)
        """
        # 1. 核对每个'pair'输入无误!!
        for pair in pair_lst:
            exchange_name, symbol, exchange = self.check_pair_name(pair=pair)

            # 2. 初始化一些数据
            gateway_name_spot = exchange_name
            gateway_name_futures = exchange_name + "S"
            vt_symbol_spot = f"{symbol.lower()}.{exchange_name}"
            vt_symbol_futures = f"{symbol.upper()}.{exchange_name}"
            symbol_spot = symbol.lower()
            symbol_futures = symbol.upper()
            symbol = symbol.lower()
            self.pairs.update(
                {
                    pair : {
                        "gateway_name_spot" : gateway_name_spot, # BINANCE
                        "gateway_name_futures" : gateway_name_futures, # BINANCES
                        "vt_symbol_spot" : vt_symbol_spot, # ethusdt.BINANCE
                        "vt_symbol_futures" : vt_symbol_futures, # ETHUSDT.BINANCE
                        "symbol_spot" : symbol_spot, # ethusdt; (同vt_symbol_spot前半段)
                        "symbol_futures" : symbol_futures, # ETHUSDT; (同vt_symbol_futures前半段)
                        "symbol" : symbol, # ethusdt; (用小写来作为symbol的一般通用形式)
                        "exchange" : exchange, # Exchange.BINANCE (是个对象)
                        "exchange_name" : exchange_name, # 'BINANCE' (是个字符串)
                        # "trading" : False, # 用于判断是否需要开启实盘交易...
                        "trading_count" : 0, # 用于判断是否需要开启实盘交易... (用数字表示剩余可以交易的次数..)
                        # 控制执行该pair的run函数的开关! (设为True, 则立马停止run函数) (不是真的直接杀死, 而是逻辑上的控制, 停止它循环执行)
                        # "kill" : False,
                        "alive" : False, # 表示run函数是否还在'异步执行中'...
                        "equal_volume" : False, # 用于判断某个pair的'期现数量是否相等'
                        "sum_volume" : -999,
                        "funding_rate" : 0,
                    }
                }
            )
            self.record_dict.update({pair:[]})

            # 3. 核对pair的 '期现volume是否匹配'
            self.check_pair_pos(pair_dict=self.pairs[pair])

        # 4. 订阅各个'pair'的tick'最优挂单'数据 (现货和合约)
            # [注意]: 订阅是'异步订阅', 所以这里没有阻塞直接就往下执行了, 所以如果后面的任务中需要用到这个请求中的数据, 则会访问失败... 后续需要一定的睡眠时间
        if to_subscribe:
            self.subscribe_many(pair_lst=pair_lst) # 订阅该'套利对'的现货和期货的tick数据
        # self.show_pairs()

    def print_spread_rate(
            self, pair="BINANCE.ETHUSDT", cycle_count=1000, sleep_time=0.1, to_print=True
        ):
        """
            function: 传入一个pair, 打印该symbol现货和合约的'开仓价差'和'平仓价差率'
            args:
                pair: # BINANCE.ETHUSDT
        """
        # 1. 初始化
        pair = pair.upper()
        pair_dict = self.pairs.get(pair)
        if not pair_dict: # 这只是用于'重新add_pair', 其实已经没啥用了... 待删...
            self.add_pair(pair=pair, to_subscribe=True)
            pair_dict = self.pairs.get(pair)
        symbol = pair_dict.get("symbol")
        exchange_name = pair_dict.get("exchange_name")
        if (f"{symbol.lower()}.{exchange_name}" not in list(self.oms.ticks)) or \
            (f"{symbol.upper()}.{exchange_name}" not in list(self.oms.ticks)):
            msg = f"tick数据还没订阅成功, 请通过add_pair函数订阅pair后, 再重试...."
            raise Exception(msg)
        exchange_name, symbol = pair.split(".")
        asset_name = symbol[:-4] # "BTC", "ETH" 这种形式
        self.to_print = to_print # (把to_print变量放入self中, 便于外部控制)

        # 2. 循环获取最新的盘口数据, 并捕捉合适的'价差率'
        for count in range(cycle_count):
            # 3. 通过pair, 计算价差率
            spread_open, spread_rate_open, spread_close, spread_rate_close = self.cal_spread_rate(pair=pair)
                # 将计算好的价差率存储到self.pairs对象中 (便于外部访问)
            pair_dict["spread_rate_open"] = spread_rate_open
            pair_dict["spread_rate_close"] = spread_rate_close
            pair_dict["time"] = get_time_us()
            self.spread_rate_open_dict[asset_name] = spread_rate_open
            self.spread_rate_close_dict[asset_name] = spread_rate_close
            self.funding_rate_dict[asset_name] = pair_dict.get("funding_rate")

            # 4. 打印
            if self.to_print:
                msg = f"[{asset_name}]  '开仓价差率' : {spread_rate_open:6.4%};    '平仓价差率' : {spread_rate_close:6.4%};"
                logger.log(20, msg)
            time.sleep(sleep_time)

            # 是对象的属性, 可以被所有子线程访问到.. 一旦这个属性被外部控制成False, 则所有子线程都退出死循环 (即: 全部被杀死了...)
            if self.kill_print_spread_rate:
                # 注意: 该函数名虽然是'打印函数', 但实际承担'计算价差率'的功能. 把该函数杀死, 循环计算价差率的程序就不再存在了..
                break

    def print_all_pair_spread_rate(self, to_print=True, sleep_time=1, cycle_count=100000):
        """
            function: 同时显示多个币种的价差率 (使用多进程方式计算价差率??)
        """

        self.t_pool = []
        pair_name_lst = list(self.pairs.keys())
        for pair_name in pair_name_lst:
            print("\n即将生成一个子线程...")
            t = threading.Thread(
                target=self.print_spread_rate,
                kwargs=({'pair':pair_name, 'sleep_time':sleep_time, 'to_print':to_print, 'cycle_count':cycle_count})
                )
            t.start()
            self.t_pool.append(t)
        # for t in self.t_pool:
        #     t.join() # 主线程需要阻塞等待每一个子线程

    def cal_spread_rate(self, pair):
        """
            function: 传入一个pair, 得到该symbol现货和合约的'最优挂单信息', 返回'价差率'相关信息
            args:
                pair: # BINANCE.ETHUSDT
            return: '开仓价差', '开仓价差率', '平仓价差', '平仓价差率'
        """
        # 1. 初始化
        oms = self.oms
        pair_dict = self.pairs.get(pair)
        vt_symbol_spot = pair_dict.get("vt_symbol_spot") # ethusdt.BINANCE
        vt_symbol_futures = pair_dict.get("vt_symbol_futures") # ETHUSDT.BINANCE

        # 2. 获取两个实时'挂单信息' (得到现货/合约的买一/卖一价, 总共4个价格)
        spot_live = oms.ticks[vt_symbol_spot].live # 获取到实时推送的'现货-最优挂单信息'
        futures_live = oms.ticks[vt_symbol_futures].live # 获取到实时推送的'合约-最优挂单信息'
        spot_buy1_price = spot_live.get("bid_price_1") # 现货买一价
        spot_sell1_price = spot_live.get("ask_price_1") # 现货卖一价
        futures_buy1_price = futures_live.get("bid_price_1") # 合约买一价
        futures_sell1_price = futures_live.get("ask_price_1") # 合约卖一价

        # 3. 计算'价差率'
            # i. 开仓的价差率
        spread_open = futures_buy1_price - spot_sell1_price
        spread_rate_open = spread_open / spot_sell1_price
            # ii. 平仓的价差率
        spread_close = futures_sell1_price - spot_buy1_price
        spread_rate_close = spread_close / spot_buy1_price
        return spread_open, spread_rate_open, spread_close, spread_rate_close

    def _cal_volume(self, pair, multiplier):
        "通过'交易乘数', 来计算实际开仓需要的volume"

        # 1. 在oms.ticks中获取该币种最新的成交价格
        exchange_name, symbol = pair.split(".")
        last_price = self.oms.ticks[f"{symbol.upper()}.{exchange_name}"].last_price

        # 2. 通过'交易乘数', 计算出实际开仓所需的volume
        count = 100 / last_price * multiplier
        # 在最高位向后保留3位数 (即: 123456.123保留成 123000; 0.00123456保留成0.00123)
        deal_count = round(count, -math.floor(math.log10(count))+2) # 前面是负号, 并在最高位数基础上保留2位数

        # 3. 查询self.oms.contracts中的最小volume精度, 避免volume精度过高超过官方支持而报错...
            # 一般来说现货支持更高的精度, 而合约的最小支持精度比现货低一级 (即: 现货可以交易1.23个币, 而合约只能交易1.2个币)
        spot_precision = self.oms.contracts.get(f"{symbol.lower()}.{exchange_name}", {}).min_volume
        futures_precision = self.oms.contracts.get(f"{symbol.upper()}.{exchange_name}", {}).min_volume
        min_volume = max(spot_precision, futures_precision) # 取更大的那一个精度
        deal_count = round(deal_count / min_volume) * min_volume
        return deal_count

    def print(self, cycle_count=1000000):
        """
            function: 打印所有订阅币种的 '资金费率', '开仓价差率', '平仓价差率' (已经排序) [子线程执行]
            note:
                - 这是该类打印输出的最终形态, 所以采用最简洁的函数命名
                - 该函数实际上没有做任何计算, 只是用于打印...
                    (底层实际运算的是'print_spread_rate'函数, 打印的数据也是调用它计算的结果)
                    (所以一旦 self.kill_print_spread_rate=True, 这里的数据也不再更新...)
            todo:
                - '平仓价差率' 不应该是从小到大的简单排序... (应该考虑开仓时候的价差率)
        """
        def foo(cycle_count):
            self.kill_print = False
            # 每秒打印 资金费率 and 开/平仓价差率
            for count in range(cycle_count):
                if len(self.funding_rate_dict) > 1:
                    funding_rate_lst = sorted(self.funding_rate_dict.items(), key=lambda x:x[1], reverse=True)
                    funding_rate_lst = [(pair[0], f"{pair[1]:.4%}") for pair in funding_rate_lst]
                else:
                    funding_rate_lst = self.funding_rate_dict
                if len(self.spread_rate_close_dict) > 1:
                    open_lst = sorted(self.spread_rate_open_dict.items(), key=lambda x:x[1], reverse=True)
                    open_lst = [(pair[0], f"{pair[1]:.4%}") for pair in open_lst]
                    close_lst = sorted(self.spread_rate_close_dict.items(), key=lambda x:x[1], reverse=False)
                    close_lst = [(pair[0], f"{pair[1]:.4%}") for pair in close_lst]
                else:
                    open_lst = self.spread_rate_open_dict
                    close_lst = self.spread_rate_close_dict
                print(f"资金费率: {funding_rate_lst}")
                print(f"开仓价差率: {open_lst}")
                print(f"平仓价差率: {close_lst}", "\n")
                time.sleep(1)
                if self.kill_print: # 可以用于杀死子线程
                    break
        t = threading.Thread(target=foo, kwargs=({'cycle_count':cycle_count}))
        t.start()

    def run(
            self, pair="BINANCE.ETHUSDT", trading_count=1,
            offset="OPEN", multiplier=1, alert_spread_rate=0.005,
            cycle_count=1000, sleep_time=0.1, to_check_balance=True, to_print=True
        ):
        """
            function:
                - 计算该实例中币种的'价差率', 并在'捕捉到某个指定的价差率'时, 立即用'市价单'下单 (指定是开仓or平仓)
                        (现货/合约双向下单)
                - 每次执行run(), 只能跑一个pair (所以现货和合约的gateway_name是固定的)
            args:
                pair: # "BINANCE.ETHUSDT"
                    以下变量由pair在self.pairs中获取:
                        exchange: # Exchange.BINANCE (是个对象! 不是字符串)
                        symbol: # ethusdt
                offset:
                    'OPEN': '开仓'套利币对
                    'CLOSE': '平仓'套利币对
                volume: 开仓数量 [被弃用]: 因为每个币种价格差异过大, 每次都要计算数量很麻烦... (改用'乘数'来表示)
                multiplier: 交易乘数
                    默认: 100u为基础单位.
                    交易乘积: 表示是基础单位的多少倍 (即: 0.1表示10u市值, 100表示10000u市值)
                            (通过交易乘数, 最终会计算出一个合理的'deal_count', 即: 实际用来开仓的volume)
                trading_count: int型 0/1/2/3/4/5  (表示可以连续自动交易的次数...) (当被递减为0的时候, 不允许被交易)
                cycle_count: 1000 (默认: 循环跑1000次, 就跳出循环)
                to_check_balance: True/False
                        (因为check一次需要浪费1ms的时间, 而套利的机会是毫秒级别的!! 当资金量足够的时候, 其实完全没有必要去check啊...)
                        (或者在run之前就测算好最多能交易多少volume, 并把这个volume记录在某个变量中, run执行中只要满足这个volume, 就可以执行交易..)
                            - 但问题是, 如果同时执行多个run(), 每个run又是不同币种, 上面的方法就不适用了...
                                (我们未来一定是要实现多币种同时在run的..)

            usage:
                eg1:
                    # 开始套利
                    symbol = "dentusdt"
                    sc.run(
                        pair=f"BINANCE.{symbol}", trading_count=1, offset="OPEN", volume=10,
                        alert_spread_rate=0.002, cycle_count=1000000, sleep_time=0.1
                    )

            todo: (优化方向)
                1. 当达到目标价差率之后, 等待3次0.1秒后, 再正式下单...否则容易被忽悠...
                    (观察到一些现象, 就是在毫秒级别的挂撤单, 严重影响盘口价差的真实性.. 而它速度太快导致我一般捕捉不到那种'变态的挂撤单')
                2. 函数自己计算每次的开仓数量... 不要每次都要我去计算100u大概是几个币... 函数自己捕获最新价去计算
                3. 可以设置一些开仓金额/开仓次数, 当达到目标价差率后, 自动多次开仓.. 不要变成一次性的run.. 频繁复制粘贴也比较麻烦..没有必要..明明它自己能重新开的..
                    # 其实可以不用打印吧... 它自己跑就行了?
                    # 或者开个多进程让它去跑... (这样我可以在同一个终端中开多个run()函数)
                4. 最好是多进程执行多个run函数...
                    1. 或者手动开启?:
                        手动的话可控一些, 想kill哪个就kill那个
                        (但其实有进程id, 我也可以控制多进程啊...也可以随意杀死某个进程)
                    2. 多进程跑的好处:
                        可以设置不同的交易量:
                            低价差率(0.3%): 交易金额在 50-100u左右 (成交快)
                            中价差率(0.35%): 交易金额在 300u左右
                            高价差率(0.4%): 交易金额在 500u左右 (赚的多)
                            # 如果是刚交割完, 还有8小时时间, 那就更多地设置在高价差率, 如果是接近交割了, 就需要更多挂在低价差率
                            # 前期: 这些倾向性的控制可以是手动控制;   后期: 这些细微的调整也可以由函数自发性的来完成
                5. 测试一下 check_balance() 函数的执行时间.... 我的交易都是毫秒级别的, 万一它浪费了我0.1秒, 我都血亏啊....
                        目前实测是 1ms, 看看怎么能优化它, 达到微秒级别?
                            (想想怎么优化这个函数的性能)

        """

        # 1. 初始化
        spot_lock = None # 初始化一个spot_lock.(当作'锁'?)
        futures_lock = None # 初始化一个spot_lock.(当作'锁'?)
        pair = pair.upper()
        pair_dict = self.pairs.get(pair)
        if not pair_dict:
            self.add_pair(pair=pair, to_subscribe=True)
            pair_dict = self.pairs.get(pair)
        record_lst = self.record_dict[pair]
        exchange = pair_dict.get("exchange") # Exchange.BINANCE
        pair_dict.update({"trading_count":trading_count})
        symbol = pair_dict.get("symbol").upper() # ethusdt
        exchange_name = pair_dict.get("exchange_name")
        if (f"{symbol.lower()}.{exchange_name}" not in list(self.oms.ticks)) or \
            (f"{symbol.upper()}.{exchange_name}" not in list(self.oms.ticks)):
            msg = f"tick数据还没订阅成功, 请通过add_pair函数订阅pair后, 再重试...."
            raise Exception(msg)
        volume = self._cal_volume(pair=pair, multiplier=multiplier)
        asset_name = symbol[:-4] # "BTC", "ETH" 这种形式
        pair_dict["alive"] = True

        # 2. 循环获取最新的盘口数据, 并捕捉合适的'价差率'
        try:
            for count in range(cycle_count):
                # 3. 通过pair, 计算价差率
                spread_open, spread_rate_open, spread_close, spread_rate_close = self.cal_spread_rate(pair=pair)

                # 4. 打印'价差率'
                if to_print:
                    # i. 开仓价差率-分阶段打印
                    if offset == 'OPEN':
                        if spread_rate_open < 0.0023:
                            if spot_lock != '0':
                                msg = f'[{symbol} - 开仓]: 价差率在一个无聊的区间...'
                                logger.log(20, msg)
                                spot_lock = '0'
                        elif 0.0023 <= spread_rate_open < 0.003:
                            if spot_lock != '1':
                                msg = f'[{symbol} - 开仓]: 价差率区间: [0.23% 至 0.30%]   ({round(spread_rate_open*100, 4)}%)'
                                logger.log(20, msg)
                                spot_lock = '1'
                        elif 0.0030 <= spread_rate_open < 0.0035:
                            if spot_lock != '2':
                                msg = f'[{symbol} - 开仓]: 价差率区间: [0.30% 至 0.35%]   ({round(spread_rate_open*100, 4)}%)'
                                logger.log(20, msg)
                                spot_lock = '2'
                        elif 0.0035 <= spread_rate_open < 0.0040:
                            if spot_lock != '3':
                                msg = f'[{symbol} - 开仓]: 价差率区间: [0.35% 至 0.40%]   ({round(spread_rate_open*100, 4)}%)'
                                logger.log(20, msg)
                                spot_lock = '3'
                        elif 0.0040 <= spread_rate_open < 0.0045:
                            if spot_lock != '4':
                                msg = f'[{symbol} - 开仓]: 价差率区间: [0.40% 至 0.45%]   ({round(spread_rate_open*100, 4)}%)'
                                logger.log(20, msg)
                                spot_lock = '4'
                        elif 0.0045 <= spread_rate_open < 0.0050:
                            if spot_lock != '5':
                                msg = f'[{symbol} - 开仓]: 价差率区间: [0.45% 至 0.50%]   ({round(spread_rate_open*100, 4)}%)'
                                logger.log(20, msg)
                                spot_lock = '5'
                        else:
                            if spot_lock != '6':
                                msg = f'[{symbol} - 开仓]: 价差率区间: [ >= 0.50% ]   ({round(spread_rate_open*100, 4)}%)'
                                logger.log(20, msg)
                                spot_lock = '6'

                    # ii. 平仓价差率-分阶段打印
                    if offset == 'CLOSE':
                        if 0.0030 <= spread_rate_close:
                            if futures_lock != '0':
                                msg = f'[{symbol} - 平仓]: 价差率在一个无聊的区间...'
                                logger.log(20, msg)
                                futures_lock = '0'
                        elif 0.0020 <= spread_rate_close < 0.003:
                            if futures_lock != '1':
                                msg = f'[{symbol} - 平仓]: 价差率区间: [0.20% 至 0.30%]   ({round(spread_rate_close*100, 4)}%)'
                                logger.log(20, msg)
                                futures_lock = '1'
                        elif 0.0010 <= spread_rate_close < 0.0020:
                            if futures_lock != '2':
                                msg = f'[{symbol} - 平仓]: 价差率区间: [0.10% 至 0.20%]   ({round(spread_rate_close*100, 4)}%)'
                                logger.log(20, msg)
                                futures_lock = '2'
                        elif 0.0005 <= spread_rate_close < 0.0010:
                            if futures_lock != '3':
                                msg = f'[{symbol} - 平仓]: 价差率区间: [0.05% 至 0.10%]   ({round(spread_rate_close*100, 4)}%)'
                                logger.log(20, msg)
                                futures_lock = '3'
                        elif 0.0000 <= spread_rate_close < 0.0005:
                            if futures_lock != '4':
                                msg = f'[{symbol} - 平仓]: 价差率区间: [0.00% 至 0.05%]   ({round(spread_rate_close*100, 4)}%)'
                                logger.log(20, msg)
                                futures_lock = '4'
                        elif -0.0005 <= spread_rate_close < 0.0000:
                            if futures_lock != '5':
                                msg = f'[{symbol} - 平仓]: 价差率区间: [-0.05% 至 0.00%]   ({round(spread_rate_close*100, 4)}%)'
                                logger.log(20, msg)
                                futures_lock = '5'
                        elif -0.0010 <= spread_rate_close < 0.0005:
                            if futures_lock != '5':
                                msg = f'[{symbol} - 平仓]: 价差率区间: [-0.10% 至 -0.05%]   ({round(spread_rate_close*100, 4)}%)'
                                logger.log(20, msg)
                                futures_lock = '5'
                        else:
                            if futures_lock != '6':
                                msg = f'[{symbol} - 平仓]: 价差率区间: [ < -0.10% ]   ({round(spread_rate_close*100, 4)}%)'
                                logger.log(20, msg)
                                futures_lock = '6'

                # 5. 下单: (达到目标价差率)
                if pair_dict.get("trading_count"):
                    if (offset == 'OPEN') and (spread_rate_open >= alert_spread_rate):
                        # 1. 开仓: 做空卖出合约, 买入现货;
                        # alert_msg = f"[提醒] =====>  当前'开仓'价差率: {round(spread_rate_open*100, 4)}, 大于{alert_spread_rate*100}%, 适合执行'开仓'操作....\n\n"
                        # logger.log(30, alert_msg)
                        self.two_sides_send_order(pair=pair, offset="OPEN", volume=volume, to_check_balance=to_check_balance) # 双边下单
                        msg = f"\n--------> 开仓成功!!! (币种:{symbol}, 开仓数量:{volume})\n"
                        logger.log(30, msg)
                        d = {
                            "spread_open" : spread_open, "spread_close" : spread_close,
                            "spread_rate_open" : spread_rate_open, "spread_rate_close" : spread_rate_close,
                            "offset" : offset, "alert_spread_rate" : alert_spread_rate,
                            }
                        record_lst.append(d)
                        pair_dict["trading_count"] -= 1 # 成功交易一笔后, 就把trading_count递减1, 减为0的时候停止交易.. (可以自行在控制台开启)
                        time.sleep(1) # 拉开两笔交易的间隔时间, 避免0.1s的时间太短而重复发送下单信号, 导致滑点过大...

                    elif (offset == 'CLOSE') and (spread_rate_close <= alert_spread_rate):
                        # 2. 平仓: 平空买入合约, 卖出现货;
                        # alert_msg = f"[提醒] =====>  当前'平仓'价差率: {round(spread_rate_close*100, 4)}, 小于{alert_spread_rate*100}%, 适合执行'平仓'操作....\n\n"
                        # logger.log(30, alert_msg)
                        self.two_sides_send_order(pair=pair, offset="CLOSE", volume=volume, to_check_balance=to_check_balance) # 双边下单
                        msg = f"\n--------> 平仓成功!!! (币种:{symbol}, 平仓数量:{volume})\n"
                        logger.log(30, msg)
                        d = {
                            "spread_open" : spread_open, "spread_close" : spread_close,
                            "spread_rate_open" : spread_rate_open, "spread_rate_close" : spread_rate_close,
                            "offset" : offset, "alert_spread_rate" : alert_spread_rate,
                            }
                        record_lst.append(d)
                        pair_dict["trading_count"] -= 1 # 成功交易一笔后, 就把trading_count递减1, 减为0的时候停止交易.. (可以自行在控制台开启)
                        # 拉开两笔交易的间隔时间, 避免0.1s的时间太短而重复发送下单信号, 导致滑点过大...
                        # (且: 连下两笔的速度过快, 余额还没更新, 容易出现check_balance误以为有钱... 导致交易出错...可能只成交了一腿...)
                        time.sleep(1) # 为啥这个睡眠没起到作用的感觉....????
                # 休眠
                time.sleep(sleep_time)
                if not pair_dict.get("alive"): # 当alive为False时, 逻辑上杀死该函数...
                    break
        except Exception as e:
            # 若同时有很多个该pair的run函数在执行, 这几个线程都会同时被杀死...
            # (即: 一旦一个线程报错, 其他同pair的线程也会死掉)
            pair_dict["alive"] = False
            raise Exception(e)

    def async_run(
            self, async_type="process", pair="BINANCE.ETHUSDT", trading_count=1,
            offset="OPEN", multiplier=1, alert_spread_rate=0.005,
            cycle_count=1000, sleep_time=0.1, to_check_balance=True, to_print=True
        ):
        """
            function: 使用'异步的方式'来执行run.. (这样可以在用一个ipython交互终端中, 执行多个run函数)
                    (两个选择: '子线程'or'子进程')
            args:
                - async_type: "process" or "thread"
        """
        # 通过子线程在执行run (可在终端控制trading变量来决定run是否被允许交易...)
        if async_type == "thread":
            t = threading.Thread(
                target=self.run,
                kwargs=({
                    'pair' : pair,
                    'offset' : offset,
                    'alert_spread_rate' : alert_spread_rate,
                    'multiplier' : multiplier,
                    'trading_count' : trading_count,
                    'to_check_balance' : to_check_balance,
                    'cycle_count' : cycle_count,
                    'sleep_time' : sleep_time,
                    'to_print' : to_print,
                    })
                )
            t.start()

        elif async_type == "process":
            t = multiprocessing.Process(
                target=self.run,
                kwargs=({
                    'pair' : pair,
                    'offset' : offset,
                    'alert_spread_rate' : alert_spread_rate,
                    'multiplier' : multiplier,
                    'trading_count' : trading_count,
                    'to_check_balance' : to_check_balance,
                    'cycle_count' : cycle_count,
                    'sleep_time' : sleep_time,
                    'to_print' : to_print,
                    })
                )
            t.start()

    def check_balance(self, pair, volume, offset):
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

        """

        # 1. 查询当前余额
        pair = pair.upper()
        pair_dict = self.pairs.get(pair)
        if not pair_dict: # 这只是用于'重新add_pair', 其实已经没啥用了... 待删...
            self.add_pair(pair=pair, to_subscribe=True)
            pair_dict = self.pairs.get(pair)
        gateway_name_spot = pair_dict.get("gateway_name_spot") # "BINANCE"
        gateway_name_futures = pair_dict.get("gateway_name_futures") # "BINANCES"
        symbol = pair_dict.get("symbol").upper() # "ETHUSDT"
        asset_name = symbol[:-4] # "ETH"
        exchange_name = pair_dict.get("exchange_name") # "BINANCE"
        if (f"{symbol.lower()}.{exchange_name}" not in list(self.oms.ticks)) or \
            (f"{symbol.upper()}.{exchange_name}" not in list(self.oms.ticks)):
            msg = f"tick数据还没订阅成功, 请通过add_pair函数订阅pair后, 再重试...."
            raise Exception(msg)
            # i. 现货USDT可用余额
        usdt_available_balance_spot = self.oms.accounts[f"{gateway_name_spot}.USDT"].balance
            # ii. 合约USDT可用余额 (即: 钱包余额) (即: 最真实的保证金, 不考虑合约的浮盈浮亏!!)
        usdt_available_balance_futures = self.oms.futures_index.get("availableBalance")
            # iii. 该币种的现货余额
        try:
            symbol_spot_balance = self.oms.accounts[f"{gateway_name_spot}.{asset_name}"].balance
        except:
            raise Exception(f"没有{asset_name}的现货余额...")
            # iv. 该币种的合约持仓数量
        try:
            symbol_futures_volume = -1 * self.oms.positions[f"{symbol}.{exchange_name}.空"].volume # 因为空仓的volume是负数, 这里先转成正数
        except:
            raise Exception(f"没有{asset_name}的空单持仓...")

        # 2. 查询当前币种的最新价格
        last_price_spot = self.oms.ticks[f"{symbol.lower()}.{exchange_name}"].last_price
        last_price_futures = self.oms.ticks[f"{symbol.upper()}.{exchange_name}"].last_price

        # 3. 计算当前待开仓的qty **(volume是指币种数量, qty是指usdt数量)
        qty_spot = last_price_spot * volume
        qty_futures = last_price_futures * volume
        if (qty_spot <= 10) or (qty_futures <= 10):
            msg = f"[不满足最低交易额] 待交易现货qty : {qty_spot}; 待交易合约qty : {qty_futures}"
            raise Exception(msg)
            # logger.log(40, msg)
            # return False

        # 4. 计算当前账户能够支付的volume
        if offset == "OPEN":
            supported_volume_spot = usdt_available_balance_spot // (last_price_spot * 1.03) # 预留3%的余量..确保价格剧烈波动中也一定能买入!
            supported_volume_futures = usdt_available_balance_futures // (last_price_futures * 1.03) # 预留3%的余量..确保价格剧烈波动中也一定能买入!
            msg = f"现货-USDT余额: {usdt_available_balance_spot:.1f};  合约-可用划转USDT余额: {usdt_available_balance_futures:.1f}"
            logger.log(10, msg)
            msg = f"现货最大交易量:{supported_volume_spot}个币;  合约最大交易量:{supported_volume_futures}个币; (当前开仓volume:{volume}, 最新价:{last_price_futures})"
            logger.log(10, msg)

            # 4. 判断是否能够买入
            if supported_volume_spot < volume:
                msg = f"############## 现货USDT不足!!!  [无法交易]\n"
                raise Exception(msg)
                # return False
            if supported_volume_futures < volume:
                msg = f"############## 合约钱包余额不足!!!  [无法交易]\n"
                raise Exception(msg)
                # return False
            msg = f"============== 余额检测通过!!  [允许交易]\n"
            logger.log(30, msg)
            return True

        elif offset == "CLOSE":
            msg = f"现货-{asset_name}余额: {symbol_spot_balance};  合约-{asset_name}空单持仓量: {symbol_futures_volume}"
            logger.log(10, msg)
            msg = f"现货最大交易量: {symbol_spot_balance}个币; 合约最大交易量: {symbol_futures_volume}个币; (当前平仓volume: {volume}, 最新价:{last_price_futures})"
            logger.log(10, msg)

            # 4. 判断是否能够买入
            if symbol_spot_balance < volume:
                msg = f"############## 现货-{asset_name}余额不足!!!  [无法交易]\n"
                raise Exception(msg)
                # return False
            if symbol_futures_volume < volume:
                msg = f"############## 合约-{asset_name}空单持仓量不足!!!  [无法交易]\n"
                raise Exception(msg)
                # return False
            msg = f"============== 余额检测通过!!  [允许交易]\n"
            logger.log(30, msg)
            return True

    def two_sides_send_order(self, pair, offset, volume, to_check_balance=True):
        """
            function:
                - 检查: 现货和期货的剩余资金是否足够下单 (双边下单)
                - 下单:
                    1.先合约下单
                    2.后现货下单
        """

        # 1. 初始化
        pair = pair.upper()
        pair_dict = self.pairs.get(pair)
        if not pair_dict:
            self.add_pair(pair=pair, to_subscribe=True)
            pair_dict = self.pairs.get(pair)
        gateway_name_spot = pair_dict.get("gateway_name_spot") # BINANCE
        gateway_name_futures = pair_dict.get("gateway_name_futures") # BINANCES
        exchange = pair_dict.get("exchange") # Exchange.BINANCE (是对象不是str)
        symbol = pair_dict.get("symbol") # "ethusdt"
        exchange_name = pair_dict.get("exchange_name") # "BINANCE"
        if (f"{symbol.lower()}.{exchange_name}" not in list(self.oms.ticks)) or \
            (f"{symbol.upper()}.{exchange_name}" not in list(self.oms.ticks)):
            msg = f"tick数据还没订阅成功, 请通过add_pair函数订阅pair后, 再重试...."
            raise Exception(msg)

        # 开仓: 做空卖出合约, 买入现货;
        if offset == "OPEN":
            # 1. 核对仓位余额
            if to_check_balance == True:
                self.check_balance(pair=pair, volume=volume, offset=offset)
            # 2. 做空卖出合约
            req_futures = OrderRequest(
                exchange=exchange, symbol=symbol, offset=Offset.OPEN, direction=Direction.SHORT,
                type=OrderType.MARKET, price=None, volume=volume
            )
            vt_orderid_futures = self.main_engine.send_order(req_futures, gateway_name=gateway_name_futures)
            # 3. 买入现货
            req_spot = OrderRequest(
                exchange=exchange, symbol=symbol, offset=Offset.OPEN, direction=Direction.LONG,
                type=OrderType.MARKET, price=None, volume=volume
            )
            vt_orderid_spot = self.main_engine.send_order(req_spot, gateway_name=gateway_name_spot)

        # 平仓: 平空买入合约, 卖出现货;
        elif offset == "CLOSE":
            # 1. 核对仓位余额
            if to_check_balance == True:
                self.check_balance(pair=pair, volume=volume, offset=offset)
            # 2. 平空买入合约
            req_futures = OrderRequest(
                exchange=exchange, symbol=symbol, offset=Offset.CLOSE, direction=Direction.LONG,
                type=OrderType.MARKET, price=None, volume=volume
            )
            vt_orderid_futures = self.main_engine.send_order(req_futures, gateway_name=gateway_name_futures)
            # 3. 卖出现货
            req_spot = OrderRequest(
                exchange=exchange, symbol=symbol, offset=Offset.CLOSE, direction=Direction.SHORT,
                type=OrderType.MARKET, price=None, volume=volume
            )
            vt_orderid_spot = self.main_engine.send_order(req_spot, gateway_name=gateway_name_spot)

        # 如果执行到这一步都没有报错, 则表示下单成功, 返回True..
        success = True
        return success

    def send_order(self, exchange, gateway_name, symbol, offset, direction, type, price=10, volume=1):
        """
            function: 封装后的send_order
            args:
                exchange:
                    Exchange.BINANCE (是个对象, 不是'BINANCE'字符串)
                gateway_name:
                    现货: 'BINANCE'
                    合约: 'BINANCES'
                symbol:
                    现货: 小写 # 'btcusdt'
                    合约: 大写 # 'BTCUSDT'
                offset:
                    开仓: "OPEN"   # 对应vnpy的 Offset.OPEN
                    平仓: "CLOSE"   # 对应vnpy的 Offset.CLOSE
                direction:
                    买入: "BUY"   # 对应vnpy的 Direction.LONG
                    卖出: "SELL"   # 对应vnpy的 Direction.SHORT
                type:
                    限价单: OrderType.LIMIT
                    市价单: OrderType.MARKET
            return:
                返回 该函数生成的req生成的order 下的 order.vt_orderid
                    # vt_orderid: "BINANCE.mUvoqJxFIILMdfAW5iGSOW"

            usage:
                eg1:
                    # 单独下单
                    symbol = "dentusdt"
                    sc.send_order(
                        exchange=Exchange.BINANCE, gateway_name="BINANCE",
                        symbol="chzusdt", offset='OPEN', direction='BUY', type="MARKET", price=15, volume=20
                    )

        """

        pair = f"{exchange.name}.{symbol.upper()}"
        self.check_balance(pair=pair, volume=volume, offset=offset)
        req = OrderRequest(
            exchange=exchange, symbol=symbol, offset=OFFSET_KW2VT[offset], direction=DIRECTION_KW2VT[direction],
            type=ORDERTYPE_KW2VT[type], price=price, volume=volume
        )
        # 发送请求 (即: 下单)
        vt_orderid = self.main_engine.send_order(req, gateway_name=gateway_name)
        msg = f"交易成功!!!\n"
        logger.log(20, msg)
        return vt_orderid

    def req_mytrade(self, pair="BINANCE.ETHUSDT", type="spot", df_type="3", query_date="today", direction=None):
        """
            function:
                - 请求历史成交记录, 复盘实际成交的价差率如何...
            args:
                - is_original: True/False  # 是否需要返回new_df, 还是过滤了不重要列的 _df
                - df_type: df的类型(根据df处理的顺序来决定):
                    - 1: 透视后的df
                    - 2: 透视表与原表联结的df (所有原字段)
                    - 3: 透视表与原表联结的df (挑选部分重要字段)
                - query_date: "today"/"2021-03-30"   # 选择某一天的数据生成df
                - direction: "BUY"/"SELL"/None    # 筛选不同买卖方向的df (None则不区分'买卖方向')

            usage:
                eg1:
                    symbol = "DENTUSDT"
                    s_df = sc.req_mytrade(symbol=symbol, type="spot", query_date="2021-03-30", is_original=False, direction="BUY")
                    f_df = sc.req_mytrade(symbol=symbol, type="futures", query_date="2021-03-30", is_original=False, direction="SELL")
                    sc.cal_avg_price(f_df) / sc.cal_avg_price(s_df)

        """

        # 1. 构造req对象, 并发送请求
        exchange_name, symbol = pair.split(".")
        req = MyTradesRequest(symbol=symbol.lower(), exchange=Exchange[exchange_name])
        if type == "spot":
            mytrade_dict = self.spot_rest_api.query_myTrades(req)
        elif type == "futures":
            mytrade_dict = self.futures_rest_api.query_myTrades(req)
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
        df = df[df["time"] >= get_timestamp(query_date)]
        # query_df = s_df.query(f"time>'{get_timestamp(queyy_date)}'")
        # df = df.iloc[query_df.index]
        if len(df) == 0:
            msg = f"日期筛选后的 mytrade_df 为空...检查交易时间或者direction..."
            raise Exception(msg)
        tmp_df = df.pivot_table(index="orderId", aggfunc={"qty":"sum", "quoteQty":"sum"})
        tmp_df["avg_price"] = tmp_df["quoteQty"] / tmp_df["qty"]
        tmp_df.rename(columns={"qty":"order_qty", "quoteQty":"order_quoteQty", "avg_price":"order_avg_price"}, inplace=True)
        new_df = pd.merge(df, tmp_df, how="left", on="orderId")
        _df = new_df[["symbol", "orderId", "qty", "price", "quoteQty", "order_qty", "order_avg_price", "commission", "time"]]

        if df_type == "1":
            return tmp_df
        elif df_type == "2":
            return new_df
        else:
            # 不管是"3"或者其他任何数字, 都返回_df
            return _df

    def get_trade_spread_rate(self, pair="BINANCE.ETHUSDT", offset="OPEN", query_date="today"):

        # 1. 请求获得现货/合约的 trade_df (每笔交易数据)
        if offset == "OPEN":
                # i. 现货的'买入'trade
            s_df = self.req_mytrade(pair=pair, type="spot", query_date=query_date, df_type="1", direction="BUY")
                # ii. 合约的'卖出'trade
            f_df = self.req_mytrade(pair=pair, type="futures", query_date=query_date, df_type="1", direction="SELL")
        elif offset == "CLOSE":
                # i. 现货的'卖出'trade
            s_df = self.req_mytrade(pair=pair, type="spot", query_date=query_date, df_type="1", direction="SELL")
                # ii. 合约的'买入'trade
            f_df = self.req_mytrade(pair=pair, type="futures", query_date=query_date, df_type="1", direction="BUY")
        else:
            raise Exception("没有此offset...")

        # 2. 计算每笔trade的价差率
        spread_rate_arr = f_df["order_avg_price"].values / s_df["order_avg_price"].values
        qty_rate_arr = f_df["order_qty"].values / s_df["order_qty"].values # 用来验证这笔交易中'现货'和'合约'是否是配平的... (值为1表示正常)
        order_qty_arr = f_df["order_qty"].values
        df = pd.DataFrame({"qty_rate":qty_rate_arr, "order_qty":order_qty_arr, "spread_rate":spread_rate_arr})
        return df

    def cal_avg_price(self, df):
        "计算这个df中交易数据的平均价格"
        avg_price = df["quoteQty"].sum() / df["qty"].sum()
        return avg_price

    def kill_all_run(self, offset_type="BOTH"):
        """
            function: 停止当前所有的run.. (比如8点刚过)
        """
        if offset_type == "BOTH":
            for pair_name, dic in self.pairs:
                dic["alive"] = False


def init_sc(spot_gateway_settings, futures_gateway_settings, exchange_name):
    """
        function: 初始化SpreadClient对象 (返回sc对象)
        args:
            setting: 网关连接的参数 (存储在'kw618.k_finance.secret.secret.py'中的密码表)
    """
    # 1. 实例化引擎 (只要一个main_engine和event_engine就可以了, 都不需要cta_engine了...)
    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)

    # 2. 添加网关实例, 并connect它 (即: ui中的连接选项)
    main_engine.add_gateway(BinanceGateway) # 已经生成了网关实例, 下挂在main_engine下
    main_engine.add_gateway(BinancesGateway)
    spot_gateway_name = exchange_name.upper()
    futures_gateway_name = exchange_name.upper() + "S"
    main_engine.connect(setting=spot_gateway_settings, gateway_name=spot_gateway_name)  # 把这个settings参数传递给对应gateway_name的网关实例, 供其建立连接
    main_engine.connect(setting=futures_gateway_settings, gateway_name=futures_gateway_name)
    # 因为连接是异步的, 要确保连接完成后才能进行下面的步骤, 所以这里要睡10s.  等待主引擎连接网关
    time.sleep(15) # 经过测试, 10s还不够connect两个网关, 需要15s才算较为足够...

    # 3. 实例化sc对象
    sc = SpreadClient(main_engine=main_engine)
    # sc.show_futures_index()
    return sc








# lzc = init_sc(spot_gateway_settings=binance_settings_lzc, futures_gateway_settings=binances_settings_lzc, exchange_name="BINANCE")
# sc = lzc

lsh = init_sc(spot_gateway_settings=binance_settings_lsh, futures_gateway_settings=binances_settings_lsh, exchange_name="BINANCE")
sc = lsh

# wyh = init_sc(spot_gateway_settings=binance_settings_wyh, futures_gateway_settings=binances_settings_wyh, exchange_name="BINANCE")
# sc = wyh













#
