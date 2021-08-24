"""
导入本模块:
from kw618.k_finance.Arbitrage.sendOrder_simply import *
"""

from kw618.k_finance.Arbitrage.calData import *


class LuckinUtils():
    def __init__(self):
        # 初始化
        self.r1 = redis.StrictRedis(host="localhost", port=6379, db=1, decode_responses=True) # 1号数据库(用于存储价差率数据)
        self.r2 = redis.StrictRedis(host="localhost", port=6379, db=2, decode_responses=True) # 2号数据库(用于存储exchange_info数据)
        self.ba = BinanceAccount(settings=LSH_BINANCE_SETTING)
        self.ba.asset_price_df = self.ba.req_asset_price()
        self.asset_price_df = self.ba.asset_price_df

    def split_spread_symbol(self, spread_symbol):
        left_leg_symbol = spread_symbol.split("/")[0] # 左腿symbol
        right_leg_symbol = spread_symbol.split("/")[1] # 右腿symbol
        return left_leg_symbol, right_leg_symbol

    def get_account_types(self, spread_symbol, spot_type="spot"):
        left_leg_symbol, right_leg_symbol = self.split_spread_symbol(spread_symbol)
        account_types = []
        for leg_symbol in [left_leg_symbol, right_leg_symbol]:
            if "_" in leg_symbol:
                left_part, right_part = leg_symbol.split("_")
                if left_part == "USD":
                    account_type = "dfutures"
                else:
                    account_type = "futures"
            else:
                account_type = "spot"
                if spot_type in ["spot", "fullMargin", "isoMargin"]:
                    account_type = spot_type
                else:
                    msg = f"[输入异常] spot_type: {spot_type}"
                    raise Exception(msg)
            account_types.append(account_type)
        return account_types

    def get_asset_name(self, symbol):
        if "_" in symbol:
            symbol, _ = symbol.split("_")
        for quote_assetName in QUOTE_ASSETS:
            if quote_assetName in symbol[1:]:
                base_asset = symbol[:-len(quote_assetName)]
                quote_asset = symbol[-len(quote_assetName):]
                return base_asset, quote_asset

    def filter_lot_size(self, symbol, base_qty):
        """
        usage:
            filter_lot_size("MKRUSDT", base_qty=0.02)
        [注意]: 这个函数不能用于'币本位' (币本位的基本都是凑整"10u"才能开仓的...逻辑不一致)

        todo:
            这种近似取精度的方式太傻逼了....待优化
        """
        base_asset_precision = float(self.r2.hget(symbol, "base_asset_precision")) # 数量精度 (eg: 0.01)
        filtered_base_qty = math.floor(round(base_qty / base_asset_precision, 10)) * base_asset_precision
        filtered_base_qty = round(filtered_base_qty, 10) # 上面的计算中可能出现'python浮点精度问题', 所以这里必须再做一次round
        return filtered_base_qty



    def filter_min_notional(self, symbol, quote_qty):
        """
        [注意]: 这个函数不能用于'币本位' (币本位的基本都是凑整"10u"才能开仓的...逻辑不一致)
        """
        # 'notional':最小名义价值 (注意: 指的是quote_asset的最小数量)
        min_notional = float(self.r2.hget(symbol, "min_notional"))
        if quote_qty < min_notional:
            msg = f"[最小市值不足{min_notional}] quote_qty:{quote_qty}"
            raise Exception(msg)


    def get_base_qty(self, symbol, base_qty=0, quote_qty=0):
        """
        usage:
            get_base_qty("MKRUSDT", base_qty=0.02, quote_qty=0)
            get_base_qty("MKRUSDT_PERP", base_qty=0.02, quote_qty=0)
        [注意]: 这样默认quote_asset是usdt, 若非usdt, 则后续逻辑有问题, 先抛出异常...
        """
        base_asset, quote_asset = self.get_asset_name(symbol)
        if quote_asset != "USDT":
            msg = f"[quote_asset不是USDT] quote_asset:{quote_asset}"
            raise Exception(msg)
        # [注意]: 这里的asset_price特指usdt的价格, 如果quote_base不是usdt, 就不能使用这个asset_price_df来获取price了
        asset_price = self.asset_price_df.query(f"asset=='{base_asset}'").iloc[0].price

        # 同时计算出 base_qty和quote_qty (两者都需要经历过滤器)
            # base_qty: 只需要经历'filter_lot_size'
            # quote_qty: 只需要经历'filter_min_notional'
        if quote_qty:
            base_qty = quote_qty / asset_price
        elif base_qty:
            pass
        else:
            msg = f"[输入错误] base_qty:{base_qty}; quote_qty:{quote_qty}"
            raise Exception(msg)
        # base_asset-过滤器: 最小精度 (其实就是用近似到'几位小数')
        base_qty = self.filter_lot_size(symbol=symbol, base_qty=base_qty)

        # quote_asset-过滤器: 最小市值 (注意: 指的是quote_asset的最小数量)
        quote_qty = base_qty * asset_price
        self.filter_min_notional(symbol=symbol, quote_qty=quote_qty)

        return base_qty

# lc_utils = LuckinUtils()


class SendOrderRobot():
    "下单机器人"
    def __init__(self, settings=LSH_BINANCE_SETTING):
        # 初始化
        self.ba = BinanceAccount(settings=settings)
        self.lc_utils = LuckinUtils()

    def update_info(self, spot_type, spread_symbol, offset, target_spread_rate, quote_qty, base_qty, count):
        # 初始化
        # 输入值检验:
        self.spot_type = spot_type
        self.spread_symbol = spread_symbol.upper()
        self.offset = offset.upper()
        self.target_spread_rate = target_spread_rate
        self.quote_qty = quote_qty # USDT总金额
        self.base_qty = base_qty # 币的数量
        self.init_count = count # 初始次数
        self.count = count # 剩余次数


    def two_legs_send_order(self, spread_symbol, offset, base_qty=0, quote_qty=0, spot_type="spot"):
        """
            function: 双腿市价下单
                - 检查: 现货和期货的剩余资金是否足够下单 (双边下单) # todo
                - 下单:
                    1. 左腿下单
                    2. 右腿下单

            usage:
                eg1:
                    two_legs_send_order(spread_symbol="MKRUSDT/MKRUSDT_PERP", offset="CLOSE", base_qty=0, quote_qty=20, spot_type="isoMargin")
                    two_legs_send_order(spread_symbol="MKRUSDT/MKRUSDT_PERP", offset="CLOSE", base_qty=0.02, quote_qty=0, spot_type="isoMargin")

            [注意]: 这个函数不能用于'币本位的开仓' (币本位的基本都是凑整"10u"才能开仓的...逻辑不一致)
        """
        # 得到左右腿的 account_type
        left_leg_symbol, right_leg_symbol = self.lc_utils.split_spread_symbol(spread_symbol)
        left_leg_account_type, right_leg_account_type = self.lc_utils.get_account_types(spread_symbol=spread_symbol, spot_type=spot_type)

        # 得到左右腿的 base_asset和quote_asset (一般情况左右腿的'base_asset和quote_asset'都是一样的!)
        left_leg_base_asset, left_leg_quote_asset = self.lc_utils.get_asset_name(left_leg_symbol)
        right_leg_base_asset, right_leg_quote_asset = self.lc_utils.get_asset_name(right_leg_symbol)
        if left_leg_base_asset != right_leg_base_asset:
            msg = f"[输入异常: 左右腿的base_asset不一致]\n 左腿base_asset:{left_leg_base_asset}, 右腿base_asset:{right_leg_base_asset}"
            raise Exception(msg)
        if left_leg_quote_asset != right_leg_quote_asset:
            msg = f"[输入异常: 左右腿的quote_asset不一致]\n 左腿quote_asset:{left_leg_quote_asset}, 右腿quote_asset:{right_leg_quote_asset}"
            raise Exception(msg)

        # 得到对应base_asset的下单数量 (即: base_qty)
        left_leg_base_qty = self.lc_utils.get_base_qty(symbol=left_leg_symbol, base_qty=base_qty, quote_qty=quote_qty)
        right_leg_base_qty = self.lc_utils.get_base_qty(symbol=right_leg_symbol, base_qty=base_qty, quote_qty=quote_qty)
        final_base_qty = min(left_leg_base_qty, right_leg_base_qty)
        logger.log(10, f"最终过滤后的final_base_qty: {final_base_qty}")
        logger.log(10, f"left_leg_account_type: {left_leg_account_type}; right_leg_account_type:{right_leg_account_type}")
        logger.log(10, f"left_leg_symbol: {left_leg_symbol}; right_leg_symbol:{right_leg_symbol}")


        # 开仓 (左腿卖出, 右腿买入)
        if offset == "OPEN":
            # 左腿卖出
            self.ba.send_order(
                account_type=left_leg_account_type, symbol=left_leg_symbol, offset="OPEN", direction="SELL",
                order_type="MARKET", price=None, quantity=final_base_qty,
            )
            # 右腿买入
            self.ba.send_order(
                account_type=right_leg_account_type, symbol=right_leg_symbol, offset="OPEN", direction="BUY",
                order_type="MARKET", price=None, quantity=final_base_qty,
            )

        # 平仓 (左腿买入, 右腿卖出)
        elif offset == "CLOSE":
            # 左腿买入
            self.ba.send_order(
                account_type=left_leg_account_type, symbol=left_leg_symbol, offset="CLOSE", direction="BUY",
                order_type="MARKET", price=None, quantity=final_base_qty,
            )
            # 右腿卖出
            self.ba.send_order(
                account_type=right_leg_account_type, symbol=right_leg_symbol, offset="CLOSE", direction="SELL",
                order_type="MARKET", price=None, quantity=final_base_qty,
            )

    def capture_spread_rate(self):
        """
            args:
                base_qty: 标的币种 (XRP, LUNA...)
                quote_qty: 计价币种 (USDT, BUSD...)

            usage:
                eg1:
                    send_order(spread_symbol="MKRUSDT/MKRUSDT_PERP", target_spread_rate=0.0005, offset="CLOSE", base_qty=0, quote_qty=20, count=20, spot_type="isoMargin")
                    send_order(spread_symbol="MKRUSDT/MKRUSDT_PERP", target_spread_rate=0.0002, offset="CLOSE", base_qty=0.05, quote_qty=0, count=20, spot_type="isoMargin")
        """
        while self.count > 0:
            spread_symbol_dict = self.lc_utils.r1.hgetall(self.spread_symbol)
            open_spread_rate = float(spread_symbol_dict.get("open_spread_rate"))
            close_spread_rate = float(spread_symbol_dict.get("close_spread_rate"))
            print(f"\n[{self.spread_symbol}: {self.offset}: {self.target_spread_rate:.3%}] 开仓价差率:{open_spread_rate:.3%}; 平仓价差率:{close_spread_rate:.3%}; ----- base_qty:{self.base_qty}; quote_qty:{self.quote_qty}; (总:{self.init_count}, 剩余:{self.count})")

            # 开仓 (左腿卖出, 右腿买入)
            if self.offset == "OPEN":
                if open_spread_rate >= self.target_spread_rate:
                    self.two_legs_send_order(spread_symbol=self.spread_symbol, offset="OPEN", base_qty=self.base_qty, quote_qty=self.quote_qty, spot_type=self.spot_type)
                    self.count -= 1

            # 平仓 (左腿买入, 右腿卖出)
            elif self.offset == "CLOSE":
                if close_spread_rate <= self.target_spread_rate:
                    self.two_legs_send_order(spread_symbol=self.spread_symbol, offset="CLOSE", base_qty=self.base_qty, quote_qty=self.quote_qty, spot_type=self.spot_type)
                    self.count -= 1

            time.sleep(1)



if __name__ == "__main__":

    # 开平仓方向选择
    offset = "开仓"
    # offset = "平仓"

    settings = LSH_BINANCE_SETTING
    # settings = ZL_BINANCE_SETTING


    if offset == "开仓":
        # 开仓
        sob1 = SendOrderRobot(settings=settings)
        spot_type = "spot"
        # spread_symbol = "AXSUSDT/AXSUSDT_PERP"
        spread_symbol = "tlmUSDT_perp/tlmUSDT"
        offset = "open"
        target_spread_rate = 0.0020
        quote_qty = 200 # USDT总金额
        base_qty = 0 # 币的数量
        count = 50
        sob1.update_info(
            spread_symbol=spread_symbol, target_spread_rate=target_spread_rate,
            offset=offset, base_qty=base_qty, quote_qty=quote_qty, count=count, spot_type=spot_type
        )
        sob1.capture_spread_rate()


    elif offset == "平仓":
        # 平仓
        sob2 = SendOrderRobot(settings=settings)
        # spot_type = "fullMargin"
        spot_type = "fullMargin"
        spread_symbol = "iotaUSDT/iotaUSDT_PERP"
        offset = "close"
        target_spread_rate = 0.0020
        quote_qty = 0 # USDT总金额
        base_qty = 100 # 币的数量
        count = 22
        sob2.update_info(
            spread_symbol=spread_symbol, target_spread_rate=target_spread_rate,
            offset=offset, base_qty=base_qty, quote_qty=quote_qty, count=count, spot_type=spot_type
        )
        sob2.capture_spread_rate()

















#
