"""
导入本模块:
from kw618.k_finance.Arbitrage.脚本03_检查实际价差率 import *
"""
from kw618 import *

lc_utils = LuckinUtils()

def get_deal_df(spread_symbol, start_time, end_time, spot_type="spot", offset="open"):
    """
    [注意]:
        - 若只传入start_time: 会自动设置end_time为7天后  (服务器支持的最大时间区间就是7天)
        - 若同时传入start_time和end_time: 时间区间不允许超过24小时 (否则报错, 请求失败...)
        - 若start_time和end_time都没有传入: 自动选择当下最新时间过去7天内的交易数据
    """
    # 输入值检验:
    spread_symbol = spread_symbol.upper() # 这里不仅需要变成大写, 还需要检测这个symbol是否拼写正确! 交割合约的日期是否还存在??
    # 得到左右腿的 account_type
    left_leg_symbol, right_leg_symbol = lc_utils.split_spread_symbol(spread_symbol)
    left_leg_account_type, right_leg_account_type = lc_utils.get_account_types(spread_symbol, spot_type=spot_type)

    # 得到左右腿的历史成交订单df
    left_df = ba.req_myTrades_df(account_type=left_leg_account_type, symbol=left_leg_symbol, start_time=start_time, end_time=end_time)
    left_df["quoteQty"] = left_df["price"] * left_df["qty"]  # 全仓/逐仓杠杆账户的交易记录不会返回'quoteQty'字段, 需要自行计算...
    right_df = ba.req_myTrades_df(account_type=right_leg_account_type, symbol=right_leg_symbol, start_time=start_time, end_time=end_time)
    right_df["quoteQty"] = right_df["price"] * right_df["qty"]  # 全仓/逐仓杠杆账户的交易记录不会返回'quoteQty'字段, 需要自行计算...

    # 开仓: 左腿卖出, 右腿买入
    if offset == "open":
        left_df = left_df.query("isBuyer!=True")
        right_df = right_df.query("isBuyer==True")
    # 平仓: 左腿买入, 右腿卖出
    elif offset == "close":
        left_df = left_df.query("isBuyer==True")
        right_df = right_df.query("isBuyer!=True")

    return left_df, right_df


def get_spread_rate_info(left_df, right_df):
    # 检查左右腿的'symbol'是否一致
    if len(left_df) == 0 or len(right_df) == 0:
        msg = f"[有一腿没有交易记录] left_df:{left_df}; right_df:{right_df}"
        raise Exception(msg)
    left_leg_symbol = left_df["symbol"].iloc[0]
    right_leg_symbol = right_df["symbol"].iloc[0]
    if left_leg_symbol != right_leg_symbol:
        msg = f"[左右腿的'标的资产'不一致] left_leg_symbol:{left_leg_symbol}; right_leg_symbol:{right_leg_symbol}"
        raise Exception(msg)
    # 左右腿'标的资产'的成交数量
    total_left_leg_base_qty = left_df["qty"].sum() # 左腿总成交数量
    total_right_leg_base_qty = right_df["qty"].sum() # 右腿总成交数量
    delta_base_qty = total_left_leg_base_qty - total_right_leg_base_qty
    # 左右腿成交均价
    left_avg_price = left_df["quoteQty"].sum() / total_left_leg_base_qty
    right_avg_price = right_df["quoteQty"].sum() / total_right_leg_base_qty
    # 计算价差率
    spread_rate = (left_avg_price - right_avg_price) / right_avg_price

    spread_rate_info = {
        "symbol":left_leg_symbol,
        "左腿成交数量":total_left_leg_base_qty, "右腿成交数量":total_right_leg_base_qty, "Delta数量":delta_base_qty,
        "左腿成交均价":left_avg_price, "右腿成交均价":right_avg_price,
        "价差率":spread_rate
    }

    return spread_rate_info


def print_spread_rate_info(offset, start_time, end_time, spread_rate_info):
    print(f"\n\n{'='*25}\n{'='*25}")
    symbol = spread_rate_info.pop("symbol")
    print(f"       [{symbol}]  ({offset})")
    print(f"时间: <{start_time} - {end_time}>")

    for k, v in spread_rate_info.items():
        # 如果是'字符串'
        if isinstance(v, str):
            print(f"{k}: {v}")
        # 如果是'数值'
        else:
            if k[-1] == "率":
                print(f"{k}: {v:.4%}")
            else:
                print(f"{k}: {v:.3f}")
    print(f"{'='*25}\n{'='*25}\n\n")



if __name__ == "__main__":
    # ba = BinanceAccount(settings=LSH_BINANCE_SETTING)
    ba = BinanceAccount(settings=ZL_BINANCE_SETTING)


    # 开平仓方向选择
    offset = "开仓"
    # offset = "平仓"

    if offset == "开仓":
        offset = "open"
        spot_type = "spot"
        spread_symbol = "dentUSDT_perp/dentUSDT"
        start_time = "2021-08-15 00:00:00"
        end_time = None
        # end_time = "2021-07-09 00:00:00"

        left_df, right_df = get_deal_df(spread_symbol=spread_symbol, start_time=start_time, end_time=end_time, spot_type=spot_type, offset=offset)
        spread_rate_info = get_spread_rate_info(left_df=left_df, right_df=right_df)
        print_spread_rate_info(offset=offset, start_time=start_time, end_time=end_time, spread_rate_info=spread_rate_info)


    elif offset == "平仓":
        offset = "close"
        spot_type = "fullMargin"
        # spread_symbol = "mkrUSDT/mkrUSDT_PERP"
        spread_symbol = "iotaUSDT/iotaUSDT_PERP"
        start_time = "2021-08-06 00:00:00"
        end_time = None
        # end_time = "2021-07-09 00:00:00"

        left_df, right_df = get_deal_df(spread_symbol=spread_symbol, start_time=start_time, end_time=end_time, spot_type=spot_type, offset=offset)
        spread_rate_info = get_spread_rate_info(left_df=left_df, right_df=right_df)
        print_spread_rate_info(offset=offset, start_time=start_time, end_time=end_time, spread_rate_info=spread_rate_info)











    ##
