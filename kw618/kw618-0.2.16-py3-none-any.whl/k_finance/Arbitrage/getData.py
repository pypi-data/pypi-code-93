"""
导入本模块:
from kw618.k_finance.Arbitrage.getData import *
from kw618.k_finance.Arbitrage.getData import MarketDataReceiver
"""
import multiprocessing
import time
import pandas as pd

from kw618._file_path import *
from kw618.k_finance.Arbitrage.binance_gateway import *
from kw618.k_pymongo.utils_redis import *
from kw618.k_finance.secret.secret import *



class MarketDataReceiver():
    """
        行情数据接收器
        "BTCUSDT": 现货盘口价格
        "BTCUSDT_PERP": u本位合约盘口价格
        "BTCUSD_PERP": 币本位合约盘口价格
        "fBTCUSDT": u本位合约资金费率
        "pBTCUSDT": u本位合约溢价指数
    """

    def __init__(self, account_setting=LZC_BINANCE_SETTING):
        """
            args:
                - connect_types:
                    1: 代表获取'现货的盘口'数据
                    2: 代表获取'u本位的盘口'数据
                    3: 代表获取'币本位的盘口'数据
                    4: 代表获取'u本位的资金费率'数据
                    5: 代表获取'u本位溢价指数'数据
                    [1, 2, 3, 4, 5]: 表示同时订阅以上所有数据的ws推送
            notes:
                - 1. 数据系统


            todo:
                1. ws莫名其妙断开后的重连??
                2. 拓展其他交易所的网关? (aicoin的主服务器应该就是实时获取了所有主流交易所的数据; 毕竟它还提供了行情数据...)
                3. 现货盘口数据的时间戳问题!!


        """
        # 初始化必要参数:
        self.assets = [] # 存放需要推送ws数据的asset
        self.assets = {"现货盘口":{}, "U本位盘口":{}, "币本位盘口":{}, "U本位资金费率":{}, "U本位溢价指数":{}}
        self.threads_1 = [] # 存储所有'现货盘口'线程
        self.threads_2 = [] # 存储所有'u本位盘口'线程
        self.threads_3 = [] # 存储所有'币本位盘口'线程
        self.threads_4 = [] # 存储所有'u本位资金费率'线程
        self.threads_5 = [] # 存储所有'u本位溢价指数'线程
        self.r0 = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True) # 0号数据库(用于获取盘口数据) (其他restful数据)
        self.r1 = redis.StrictRedis(host="localhost", port=6379, db=1, decode_responses=True) # 1号数据库(用于存储价差率数据)
        self.r2 = redis.StrictRedis(host="localhost", port=6379, db=2, decode_responses=True) # 2号数据库(用于存储exchange_info数据)
        self.alive = False # False: 不再接收ws推送的消息; True: 正在接收ws推送的消息

        # 使用币安网关  (后续可以延展成别的网关)
        self.ba = BinanceAccount(settings=account_setting)






    def subscribe_market_data_v2(self, assets=[]):
        def on_message(ws, message):  # 服务器有数据更新时，主动推送过来的数据
            print(message)


        def on_error(ws, error):  # 程序报错时，就会触发on_error事件
            print(error)


        def on_close(ws):
            print("Connection closed ……")


        def on_open(ws):  # 连接到服务器之后就会触发on_open事件，这里用于send数据
            req = '{"event":"subscribe", "channel":"btc_usdt.deep"}'
            print(req)
            ws.send(req)


        websocket.enableTrace(True)
        ws = websocket.WebSocketApp("wss://stream.binance.com:9443/stream",
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close)
        ws.on_open = on_open
        ws.run_forever(ping_timeout=30)





    def subscribe_market_data_v3(self, assets=[]):
        # url = "wss://stream.binance.com:9443/stream"
        # proxy = config.proxy
        # session = aiohttp.ClientSession()

        url = f"wss://fstream.binance.com/stream?"
        ws = websocket.create_connection( # 该函数比 ws.connect()好用, 返回的也是一个ws对象
            url,
            sslopt={"cert_reqs": ssl.CERT_NONE}, # 我也不知道干啥用的, 不传递也能订阅成功的..
            http_proxy_host=http_proxy_host, # 代理一定要传递, 不然订阅不成功 (一直没搞懂, 为啥要翻墙才行...)
            http_proxy_port=http_proxy_port,
            # header="" # 币安接口不需要传递header
        )

        payload = {
            "method": "UNSUBSCRIBE",
            "params":
            [
            # "btcusdt@markPrice@1s",
            "!bookTicker", # 全市场挂单数据的cpu计算也只占 20%左右 (那平时看到的80%-100%是来自于calData???) (如果不打印,占比少5%)
            ],
            "id": 618 # 可以自定义的?! 用于在众多推送信息中获取目标数据的... (默认:1)
        }
        ws.send(json.dumps(payload))

        payload = {
            "method": "SUBSCRIBE",
            "params":
            [
            # "btcusdt@markPrice@1s",
            "!bookTicker", # 全市场挂单数据的cpu计算也只占 20%左右 (那平时看到的80%-100%是来自于calData???) (如果不打印,占比少5%)
            ],
            "id": 618 # 可以自定义的?! 用于在众多推送信息中获取目标数据的... (默认:1)
        }
        ws.send(json.dumps(payload))

        payload = {
            "method": "LIST_SUBSCRIPTIONS",
            "id": 3999 # 可以自定义的?! 用于在众多推送信息中获取目标数据的...
        }
        ws.send(json.dumps(payload))


        def foo(ws):
            while True:
                data = ws.recv()
                if ws.to_print:
                    print(data)

        ws.to_print = True
        t1 = threading.Thread(target=foo, kwargs=({'ws':ws}))
        t1.start()




        url = f"wss://fstream.binance.com/stream?"
        ws = websocket.create_connection( # 该函数比 ws.connect()好用, 返回的也是一个ws对象
            url,
            sslopt={"cert_reqs": ssl.CERT_NONE}, # 我也不知道干啥用的, 不传递也能订阅成功的..
            http_proxy_host=http_proxy_host, # 代理一定要传递, 不然订阅不成功 (一直没搞懂, 为啥要翻墙才行...)
            http_proxy_port=http_proxy_port,
            # header="" # 币安接口不需要传递header
        )
        assets = KEY_FUTURES_ASSETS
        channels = [f"{asset.lower()}usdt@bookTicker" for asset in assets]
        payload = {
            "method": "SUBSCRIBE",
            "params": channels,
            "id": 618 # 可以自定义的?! 用于在众多推送信息中获取目标数据的... (默认:1)
        }
        ws.send(json.dumps(payload))
        def foo(ws):
            while True:
                data = ws.recv()
                if ws.to_print:
                    print(data)
        ws.to_print = True
        t1 = threading.Thread(target=foo, kwargs=({'ws':ws}))
        t1.start()






    # 一. 获取四个关键数据源的ws
        # i. 现货的挂单数据ws
    def get_spot_marketData_ws(self, assets=[]):
        """
        todo:
            - 处理时间戳问题 (通过增量接口)
        """
        print(f"assets:{assets}")
        if assets:
            channels = [f"{asset.lower()}usdt@bookTicker" for asset in assets]
            spot_marketData_ws = self.ba.subscribe_market_data(account_type="spot", channels=channels)
        else:
            spot_marketData_ws = self.ba.subscribe_market_data(account_type="spot", channels=["!bookTicker"])
        self.spot_marketData_ws = spot_marketData_ws
        return spot_marketData_ws

        # ii. u本位合约的挂单数据ws
    def get_futures_marketData_ws(self, assets=[]):
        if assets:
            channels = [f"{asset.lower()}usdt@bookTicker" for asset in assets]
            futures_marketData_ws = self.ba.subscribe_market_data(account_type="futures", channels=channels)
        else:
            futures_marketData_ws = self.ba.subscribe_market_data(account_type="futures", channels=["!bookTicker"])
        self.futures_marketData_ws = futures_marketData_ws
        return futures_marketData_ws

        # iii. 币本位合约的挂单数据ws
    def get_dfutures_marketData_ws(self, assets=[]):
        if assets:
            channels = []
            for asset in assets:
                # 1. 如果该资产有币本位合约的'季度合约'
                if asset.upper() in DFUTURES_QUARTER_ASSETS:
                    channels.append(f"{asset.lower()}usd_perp@bookTicker") # 币本位永续
                    channels.append(f"{asset.lower()}usd_210625@bookTicker") # 币本位当季
                    channels.append(f"{asset.lower()}usd_210924@bookTicker") # 毕本我次季
                # 2. 如果该资产有币本位合约
                elif asset.upper() in DFUTURES_ASSETS:
                    channels.append(f"{asset.lower()}usd_perp@bookTicker") # 币本位永续
                # 3. 如果该资产没有币本位合约
                else:
                    pass
            if channels:
                dfutures_marketData_ws = self.ba.subscribe_market_data(account_type="dfutures", channels=channels)
            else:
                dfutures_marketData_ws = None
        else:
            dfutures_marketData_ws = self.ba.subscribe_market_data(account_type="dfutures", channels=["!bookTicker"])
        self.dfutures_marketData_ws = dfutures_marketData_ws
        return dfutures_marketData_ws

        # iv. U本位合约的资金费率ws
    def get_fundingRate_ws(self, assets=[]):
        if assets:
            channels = [f"{asset.lower()}usdt@markPrice@1s" for asset in assets]
            fundingRate_ws = self.ba.subscribe_market_data(account_type="futures", channels=channels)
        else:
            fundingRate_ws = self.ba.subscribe_market_data(account_type="futures", channels=["!markPrice@arr@1s"])
        self.fundingRate_ws = fundingRate_ws
        return fundingRate_ws

        # v. 溢价指数ws
    def get_premium_index_ws(self, assets=[]):
        """
        notes:
            - 溢价指数只能传入指定的'asset' (不能一次性订阅所有的symbol)
        """
        if assets:
            symbols = []
            for asset in assets:
                # 溢价指数不同于上面3个行情数据的ws, 这里的symbol需要大写 (上面的symbol需要小写)
                symbols.append(f"{asset.upper()}USDT") # U本位
                # symbols.append(f"{asset.upper()}USD") # 币本位 // 币本位的ws在网页上也获取不到..很神奇..暂时放弃...
            premium_index_ws = self.ba.subscribe_premium_index(account_type="spot", symbols=symbols)
        else:
            premium_index_ws = None
        self.premium_index_ws = premium_index_ws
        return premium_index_ws


    # 二. 获取最优盘口挂单/溢价指数数据 (4个ws使用多进程获取)
    def get_spot_marketData(self, assets):
        try:
            ws = self.get_spot_marketData_ws(assets=assets)
            if ws:
                print(f"正在接收'现货盘口'数据: \n{assets}\n")
                while self.alive:
                    t = ws.recv()
                    d = json.loads(t)
                    data = d.get("data")
                    symbol = data.get("s")
                    updateId = data.get("u")
                    bid_price = data.get("b")
                    bid_volume = data.get("B")
                    ask_price = data.get("a")
                    ask_volume = data.get("A")
                    self.r0.hset(symbol, "bid_price", bid_price)
                    self.r0.hset(symbol, "bid_volume", bid_volume)
                    self.r0.hset(symbol, "ask_price", ask_price)
                    self.r0.hset(symbol, "ask_volume", ask_volume)
        except Exception as e:
            print(e)
        finally:
            self.pause_assets(assets=assets, connect_types="现货盘口")

    def get_futures_marketData(self, assets):
        try:
            ws = self.get_futures_marketData_ws(assets=assets)
            if ws:
                print(f"正在接收'U本位盘口'数据: \n{assets}\n")
                while self.alive:
                    t = ws.recv()
                    d = json.loads(t)
                    data = d.get("data")
                    symbol = data.get("s")
                    if not "_" in symbol:
                        # 如果symbol是 BTCUSDT_210625 则不修改, 表示u本位的季度合约
                        kw_symbol = symbol + "_PERP" # 用 BTCUSDT_PERP 命名, 来表示u本位永续合约
                    else:
                        kw_symbol = symbol
                    updateId = data.get("u") # // 1621861778316
                    match_time = data.get("T") # 撮合时间 (可能比事件推送时间更早一些) // 1621861778316
                    event_time = data.get("E") # 事件推送时间 // 1621861778319
                    bid_price = data.get("b") # // "1.48020"
                    bid_volume = data.get("B") # // "64"
                    ask_price = data.get("a")
                    ask_volume = data.get("A")
                    self.r0.hset(kw_symbol, "bid_price", bid_price)
                    self.r0.hset(kw_symbol, "bid_volume", bid_volume)
                    self.r0.hset(kw_symbol, "ask_price", ask_price)
                    self.r0.hset(kw_symbol, "ask_volume", ask_volume)
                    self.r0.hset(kw_symbol, "server_timestamp", match_time)
        except Exception as e:
            print(e)
        finally:
            self.pause_assets(assets=assets, connect_types="U本位盘口")

    def get_dfutures_marketData(self, assets):
        """
            问题:
                - 这里的assets不是所有都有币本位的, 但是我一旦启动, 会把所有assets都标记为1 (就有问题...)
        """
        try:
            ws = self.get_dfutures_marketData_ws(assets=assets)
            if ws:
                print(f"正在接收'币本位盘口'数据: \n{assets}\n")
                while self.alive:
                    t = ws.recv()
                    d = json.loads(t)
                    data = d.get("data")
                    symbol = data.get("s") # BTCUSD_200626
                    pair = data.get("ps") # BTCUSD
                    updateId = data.get("u") # // 1621861778316
                    match_time = data.get("T") # 撮合时间 (可能比事件推送时间更早一些) // 1621861778316
                    event_time = data.get("E") # 事件推送时间 // 1621861778319
                    bid_price = data.get("b") # // "1.48020"
                    bid_volume = data.get("B") # // "64"
                    ask_price = data.get("a")
                    ask_volume = data.get("A")
                    self.r0.hset(symbol, "bid_price", bid_price)
                    self.r0.hset(symbol, "bid_volume", bid_volume)
                    self.r0.hset(symbol, "ask_price", ask_price)
                    self.r0.hset(symbol, "ask_volume", ask_volume)
                    self.r0.hset(symbol, "server_timestamp", match_time)
        except Exception as e:
            print(e)
        finally:
            self.pause_assets(assets=assets, connect_types="币本位盘口")

    def get_fundingRate(self, assets):
        try:
            ws = self.get_fundingRate_ws(assets=assets)
            if ws:
                print(f"正在接收'U本位资金费率'数据: \n{assets}\n")
                while self.alive:
                    t = ws.recv()
                    d = json.loads(t)
                    data = d.get("data")
                    symbol = data.get("s") # "BTCUSDT"
                    kw_symbol = f"f{symbol}" # 前面加个'f'代表'资金费率' // "fBTCUSDT"
                    event_time = data.get("E") # 事件推送时间 // 1621861778319
                    mark_price = data.get("p") # 标记价格 // "11794.15000000"
                    fundingRate = data.get("r") # 资金费率 // "0.00038167"
                    self.r0.hset(kw_symbol, "server_timestamp", event_time)
                    self.r0.hset(kw_symbol, "mark_price", mark_price)
                    self.r0.hset(kw_symbol, "fundingRate", fundingRate)
        except Exception as e:
            print(e)
        finally:
            self.pause_assets(assets=assets, connect_types="U本位资金费率")

    def get_premium_index(self, assets):
        """
        notes:
            - 这个ws的接收时间间隔比较长, 所以当self.alive变成False后, 它需要一定的反应时间才会停止子线程...
        """
        try:
            ws = self.get_premium_index_ws(assets=assets) # 当assets传入为[]时, 该函数是返回None的 (它只能指定symbol订阅)
            if ws:
                print(f"正在接收'U本位溢价指数'数据: \n{assets}\n")
                while self.alive:
                    t = ws.recv()
                    d = json.loads(t)
                    data = d.get("data")
                    symbol = data.get("s") # pBTCUSDT // 币安官方的命名 (p表示premium)
                    event_time = data.get("E") # 事件推送时间 // 1621861778319
                    k_data = data.get("k") # 下一层的k线数据
                    period_start_time = k_data.get("t") # 间隔的开始时间 (如: 23:59:00 整分钟的第0秒)
                    period_end_time = k_data.get("T") # 间隔的结束时间
                    open_price = k_data.get("o") # // 开盘价
                    close_price = k_data.get("c") # // 收盘价
                    high_price = k_data.get("h")
                    low_price = k_data.get("l")
                    self.r0.hset(symbol, "open_price", open_price)
                    self.r0.hset(symbol, "close_price", close_price)
                    self.r0.hset(symbol, "high_price", high_price)
                    self.r0.hset(symbol, "low_price", low_price)
                    self.r0.hset(symbol, "server_timestamp", event_time)
        except Exception as e:
            print(e)
        finally:
            self.pause_assets(assets=assets, connect_types="U本位溢价指数")


    # 三. restful类的数据请求
    # exchangeInfo数据
    def get_exchange_info(self):
        flushdb(self.r2) # 清空原有的redis库
            # 1. spot_exchange_info:
        spot_exchange_info = self.ba.req_exchange_info(account_type="spot")
        for symbol_info in spot_exchange_info.get("symbols"):
            symbol = symbol_info.get("symbol")
            for f in symbol_info["filters"]:
                if f["filterType"] == "LOT_SIZE":
                    base_asset_precision = float(f["stepSize"]) # 'stepSize': 数量精度
                elif f["filterType"] == "PRICE_FILTER":
                    quote_asset_precision = float(f["tickSize"]) # 'tickSize': 价格精度
                elif f["filterType"] == "MIN_NOTIONAL":
                    # 'notional':最小名义价值 (注意: 指的是quote_asset的最小数量)
                    min_notional = float(f.get("notional") or f.get("minNotional"))
            self.r2.hset(symbol, "base_asset_precision", base_asset_precision)
            self.r2.hset(symbol, "quote_asset_precision", quote_asset_precision)
            self.r2.hset(symbol, "min_notional", min_notional)
            symbol_info = json.dumps(symbol_info)
            self.r2.hset(symbol, "symbol_info", symbol_info)

            # 2. futures_exchange_info:
        futures_exchange_info = self.ba.req_exchange_info(account_type="futures")
        for symbol_info in futures_exchange_info.get("symbols"):
            symbol = symbol_info.get("symbol")
            if not "_" in symbol:
                # 如果symbol是 BTCUSDT_210625 则不修改, 表示u本位的季度合约
                kw_symbol = symbol + "_PERP" # 用 BTCUSDT_PERP 命名, 来表示u本位永续合约
            else:
                kw_symbol = symbol
            for f in symbol_info["filters"]:
                if f["filterType"] == "LOT_SIZE":
                    base_asset_precision = float(f["stepSize"]) # 'stepSize': 数量精度
                elif f["filterType"] == "PRICE_FILTER":
                    quote_asset_precision = float(f["tickSize"]) # 'tickSize': 价格精度
                elif f["filterType"] == "MIN_NOTIONAL":
                    # 'notional':最小名义价值 (注意: 指的是quote_asset的最小数量)
                    min_notional = float(f.get("notional") or f.get("minNotional"))
            self.r2.hset(kw_symbol, "base_asset_precision", base_asset_precision)
            self.r2.hset(kw_symbol, "quote_asset_precision", quote_asset_precision)
            self.r2.hset(kw_symbol, "min_notional", min_notional)
            symbol_info = json.dumps(symbol_info)
            self.r2.hset(kw_symbol, "symbol_info", symbol_info)

            # 3. dfutures_exchange_info:
        dfutures_exchange_info = self.ba.req_exchange_info(account_type="dfutures")
        for symbol_info in dfutures_exchange_info.get("symbols"):
            symbol = symbol_info.get("symbol")
            for f in symbol_info["filters"]:
                if f["filterType"] == "LOT_SIZE":
                    base_asset_precision = float(f["stepSize"]) # 'stepSize': 数量精度
                elif f["filterType"] == "PRICE_FILTER":
                    quote_asset_precision = float(f["tickSize"]) # 'tickSize': 价格精度
            self.r2.hset(symbol, "base_asset_precision", base_asset_precision)
            self.r2.hset(symbol, "quote_asset_precision", quote_asset_precision)
            symbol_info = json.dumps(symbol_info)
            self.r2.hset(symbol, "symbol_info", symbol_info)


    # 四. 连接交易所
    def connect(self, assets, connect_types):
        """
            notes:
                - asset一次connect, 最多可以接收6个信息推送: (有些asset没有币本位, 就只有3个数据)
                    1. 现货挂单
                    2. U本位永续合约挂单
                    3. 币本位永续合约挂单
                    4. 币本位当季合约挂单
                    5. 币本位次季合约挂单
                    6. U本位永续合约溢价指数
                    (以上6个数据由4个进程分别运行)
        """

        self.alive = True

        # I. ws推送数据
        # =========================================================
        # 记录所有assets的存货情况 (便于后面查阅哪个币种的ws已经死亡)
            # 1. 现货盘口
        if 1 in connect_types:
            assets_1 = self.active_assets(assets=assets, connect_types="现货盘口")
            # if assets_1: # 空的[]表示所有币种都要接收??
            t1 = threading.Thread(target=self.get_spot_marketData, kwargs=({'assets':assets_1}))
            t1.start()
            self.threads_1.append(t1)

            # 2. U本位盘口
        if 2 in connect_types:
            assets_2 = self.active_assets(assets=assets, connect_types="U本位盘口")
            # if assets_2:
            t2 = threading.Thread(target=self.get_futures_marketData, kwargs=({'assets':assets_2}))
            t2.start()
            self.threads_2.append(t2)

            # 3. 币本位盘口
        if 3 in connect_types:
            """
                问题:
                    - 这里的assets不是所有都有币本位的, 但是我一旦启动, 会把所有assets都标记为1 (就有问题...)
            """
            # 先剔除掉'没有币本位合约的asset'
            new_assets = []
            for asset in assets:
                if asset.upper() in DFUTURES_ASSETS:
                    new_assets.append(asset)
            # 再去激活这些asset
            assets_3 = self.active_assets(assets=new_assets, connect_types="币本位盘口")
            if assets_3:
                t3 = threading.Thread(target=self.get_dfutures_marketData, kwargs=({'assets':assets_3}))
                t3.start()
                self.threads_3.append(t3)

            # 4. U本位资金费率
        if 4 in connect_types:
            assets_4 = self.active_assets(assets=assets, connect_types="U本位资金费率")
            # if assets_4:
            t4 = threading.Thread(target=self.get_fundingRate, kwargs=({'assets':assets_4}))
            t4.start()
            self.threads_4.append(t4)

            # 5. U本位溢价指数
        if 5 in connect_types:
            assets_5 = self.active_assets(assets=assets, connect_types="U本位溢价指数")
            if assets_5:
                t5 = threading.Thread(target=self.get_premium_index, kwargs=({'assets':assets_5}))
                t5.start()
                self.threads_5.append(t5)

        # II. restful的通用数据
        # =========================================================
            # 1. exchangeInfo数据
        self.get_exchange_info()



    def keep_connect(self):
        """
        notes: 定期延长ws的有效时间
        """
        pass


    # 五. 线程管理
    def active_assets(self, assets, connect_types):
        "激活: 仅仅是修改assets字典中的True/False (起到标识作用)"
        new_assets = []
        for asset in assets:
            asset_alive_num = self.assets[connect_types].get(asset, 0)
            if asset_alive_num > 0:
                pass
            elif asset_alive_num <= 0:
                new_assets.append(asset)
                self.assets[connect_types].update({asset:asset_alive_num+1})
        return new_assets

    def pause_assets(self, assets, connect_types):
        "暂停: 仅仅是修改assets字典中的True/False (起到标识作用)"
        for asset in assets:
            asset_alive_num = self.assets[connect_types].get(asset, 0)
            if asset_alive_num > 0:
                self.assets[connect_types].update({asset:asset_alive_num-1})
            elif asset_alive_num <= 0:
                pass

    def pause(self):
        "这里的pause与上面的pause_asset不一样, 是真的会停止接收ws推送消息"
        self.alive = False

    def show_all_threads_is_alive(self):
        "展示所有子线程是否还活着"
        print("\n\n=================现货盘口===============")
        for thread in self.threads_1:
            is_alive = thread.is_alive()
            print(f"{thread}: {is_alive}")
        print("=================u本位盘口===============")
        for thread in self.threads_2:
            is_alive = thread.is_alive()
            print(f"{thread}: {is_alive}")
        print("=================币本位盘口===============")
        for thread in self.threads_3:
            is_alive = thread.is_alive()
            print(f"{thread}: {is_alive}")
        print("=================u本位资金费率===============")
        for thread in self.threads_4:
            is_alive = thread.is_alive()
            print(f"{thread}: {is_alive}")
        print("=================u本位溢价指数===============")
        for thread in self.threads_5:
            is_alive = thread.is_alive()
            print(f"{thread}: {is_alive}")

    def show(self):
        assets_dic = self.assets
        df = pd.DataFrame(assets_dic)
        return df





if __name__ == "__main__":
    mdr = MarketDataReceiver(account_setting=LZC_BINANCE_SETTING)
    assets = KEY_FUTURES_ASSETS
    assets = ["iota", "etc", "1inch", "trx"]
    assets = ["sushi", "cvc", "eth", "lit", "xmr", "alpha", "trx", "dgb", "neo"]
    assets = ["stmx", "mana", "xrp"]
    assets = ["xrp"]
    # mdr.connect(assets=assets, connect_types=[1, 2, 3, 4, 5])
    mdr.connect(assets=assets, connect_types=[1, 2, 4, 5])




#
