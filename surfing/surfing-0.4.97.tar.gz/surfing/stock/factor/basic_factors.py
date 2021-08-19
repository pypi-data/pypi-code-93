
import pandas as pd

# from typing import Optional

from ...constant import StockFactorType
from .base import Factor
from .utils import get_factor_from_stock_data, calc_ttm


class BasicFactor(Factor):
    # 所有基础因子的基类
    def __init__(self, name):
        super().__init__(f'basic/{name}', StockFactorType.BASIC)


class StockTradableFactor(BasicFactor):
    # 交易状态
    def __init__(self):
        super().__init__('stock_tradable')

    def calc(self):
        tp = get_factor_from_stock_data('get_em_stock_post_price', columns=['trade_status'])
        tp[tp == '正常交易'] = 1
        tp[tp == '复牌'] = 1
        tp[tp == '盘中停牌'] = 1
        tp[tp == '停牌半小时'] = 1
        tp[tp == '停牌一小时'] = 1
        tp[tp == '停牌半天'] = 1
        tp[tp != 1] = 0
        self._factor = tp


class StockPriceFactor(BasicFactor):
    # 未复权股价
    def __init__(self):
        super().__init__('stock_price')

    def calc(self):
        self._factor = get_factor_from_stock_data('get_em_stock_price', columns=['close'])


class StockPostPriceFactor(BasicFactor):
    # 后复权股价
    def __init__(self):
        super().__init__('stock_post_price')

    def calc(self):
        self._factor = get_factor_from_stock_data('get_em_stock_post_price', columns=['close'])
        self._factor_return = self._factor.pct_change(fill_method=None)


class StockOpenPriceFactor(BasicFactor):
    # 开盘价
    def __init__(self):
        super().__init__('stock_open_price')

    def calc(self):
        self._factor = get_factor_from_stock_data('get_em_stock_post_price', columns=['open'])


class StockHighPriceFactor(BasicFactor):
    # 最高价
    def __init__(self):
        super().__init__('stock_high_price')

    def calc(self):
        self._factor = get_factor_from_stock_data('get_em_stock_post_price', columns=['high'])


class StockLowPriceFactor(BasicFactor):
    # 最低价
    def __init__(self):
        super().__init__('stock_low_price')

    def calc(self):
        self._factor = get_factor_from_stock_data('get_em_stock_post_price', columns=['low'])


class StockVolumeFactor(BasicFactor):
    # 成交量
    def __init__(self):
        super().__init__('stock_volume')

    def calc(self):
        self._factor = get_factor_from_stock_data('get_em_stock_post_price', columns=['volume'])
        self._factor = self._factor.ffill()


class StockVWAPFactor(BasicFactor):
    # VWAP
    def __init__(self):
        super().__init__('stock_vwap')

    def calc(self):
        self._factor = get_factor_from_stock_data('get_em_stock_post_price', columns=['average'])
        self._factor = self._factor.ffill()


class TotalShareFactor(BasicFactor):
    # 总股本
    def __init__(self):
        super().__init__('total_share')

    def calc(self):
        self._factor = get_factor_from_stock_data('get_em_daily_info', columns=['total_share'])


class CirculationShareFactor(BasicFactor):
    # 流通股本
    def __init__(self):
        super().__init__('circ_share')

    def calc(self):
        self._factor = get_factor_from_stock_data('get_em_daily_info', columns=['liq_share'])


class MarketValueFactor(BasicFactor):
    # 总市值
    def __init__(self):
        super().__init__('market_value')
        self._deps.add(TotalShareFactor())
        self._deps.add(StockPostPriceFactor())

    def calc(self):
        # 总市值 = 总股本 * 每日后复权股价
        self._factor = TotalShareFactor().get() * StockPostPriceFactor().get()


class PreferredStockFactor(BasicFactor):
    # 优先股
    def __init__(self):
        super().__init__('preferred_stock')

    def calc(self):
        self._factor = get_factor_from_stock_data('get_em_stock_fin_fac', columns=['balance_statement_196'])


class AdjNetAssetAvgFactor(BasicFactor):
    # 经优先股调整的净资产最近四期均值
    def __init__(self):
        super().__init__('adj_net_asset_avg')

    def calc(self):
        self._factor = get_factor_from_stock_data('get_em_stock_fin_fac', columns=['balance_statement_141'], processor_after_pivot=lambda x: x.rolling(4, min_periods=1).mean()) - \
            get_factor_from_stock_data('get_em_stock_fin_fac', columns=['balance_statement_196'], processor_after_pivot=lambda x: x.fillna(0).rolling(4, min_periods=1).mean())


class TotalAssetAvgFactor(BasicFactor):
    # 总资产最近四期均值
    def __init__(self):
        super().__init__('total_asset_avg')

    def calc(self):
        self._factor = get_factor_from_stock_data('get_em_stock_fin_fac', columns=['balance_statement_74'], processor_after_pivot=lambda x: x.rolling(4, min_periods=1).mean())


class TotalDebtAvgFactor(BasicFactor):
    # 总负债最近四期均值
    def __init__(self):
        super().__init__('total_debt_avg')

    def calc(self):
        self._factor = get_factor_from_stock_data('get_em_stock_fin_fac', columns=['balance_statement_128'], processor_after_pivot=lambda x: x.rolling(4, min_periods=1).mean())


class NetAssetFactor(BasicFactor):
    # 净资产
    def __init__(self):
        super().__init__('net_asset')

    def calc(self):
        self._factor = get_factor_from_stock_data('get_em_stock_fin_fac', columns=['balance_statement_141'])


class FixAssetAvgFactor(BasicFactor):
    # 固定资产最近四期均值
    def __init__(self):
        super().__init__('fix_asset_avg')

    def calc(self):
        self._factor = get_factor_from_stock_data('get_em_stock_fin_fac', columns=['balance_statement_31'], processor_after_pivot=lambda x: x.rolling(4, min_periods=1).mean())


class NetProfitFactor(BasicFactor):
    # 净利润
    def __init__(self):
        super().__init__('net_profit')

    def calc(self):
        self._factor = get_factor_from_stock_data('get_em_stock_fin_fac', columns=['income_statement_60'])


class NetProfitTTMFactor(BasicFactor):
    # 净利润TTM
    def __init__(self):
        super().__init__('net_profit_ttm')

    def calc(self):
        self._factor = get_factor_from_stock_data('get_em_stock_fin_fac', columns=['np_ttmrp'])


class IncomeFactor(BasicFactor):
    # 营业收入
    def __init__(self):
        super().__init__('income')

    def calc(self):
        self._factor = get_factor_from_stock_data('get_em_stock_fin_fac', columns=['income_statement_9'])


class IncomeTTMFactor(BasicFactor):
    # 营业收入TTM
    def __init__(self):
        super().__init__('income_ttm')

    def calc(self):
        self._factor = get_factor_from_stock_data('get_em_stock_fin_fac', columns=['or_ttmr'])


class ExpenseTTMFactor(BasicFactor):
    # 营业支出TTM
    def __init__(self):
        super().__init__('expense_ttm')

    def calc(self):
        self._factor = get_factor_from_stock_data('get_em_stock_fin_fac', columns=['expense_ttmr'])


class AdjNetProfitFactor(BasicFactor):
    # 归属于上市公司股东的扣除非经常性损益后的净利润(调整前)
    def __init__(self):
        super().__init__('adj_net_profit')

    def calc(self):
        self._factor = get_factor_from_stock_data('get_em_stock_fin_fac', columns=['deducted_income_ba'])


class TotalRevenueTTMFactor(BasicFactor):
    # 营业总收入TTM
    def __init__(self):
        super().__init__('total_revenue_ttm')

    def calc(self):
        self._factor = get_factor_from_stock_data('get_em_stock_fin_fac', columns=['income_statement_83'], processor_after_pivot=lambda x: x.apply(calc_ttm, axis=1, result_type='broadcast', whole_df=x))


class DividendYearlyFactor(BasicFactor):
    # 年度累计分红总额
    def __init__(self):
        super().__init__('dividend_yearly')

    def calc(self):
        def _resample_to_date(df):
            # 年份变为日期(xxxx-01-01)
            df.index = pd.to_datetime(df.index, format='%Y')
            # 01-01变为12-31
            df = df.resample('1Y').mean()
            df.index = df.index.date
            return df

        self._factor = get_factor_from_stock_data('get_em_stock_yearly', columns=['div_annu_accum'], index='year', processor_after_pivot=_resample_to_date).fillna(0)


class EBITDAFactor(BasicFactor):
    # EBITDA
    def __init__(self):
        super().__init__('ebitda')

    def calc(self):
        self._factor = get_factor_from_stock_data('get_em_stock_fin_fac', columns=['ebitda'])


class EBITDATTMFactor(BasicFactor):
    # EBITDA TTM
    def __init__(self):
        super().__init__('ebitda_ttm')

    def calc(self):
        self._factor = get_factor_from_stock_data('get_em_stock_fin_fac', columns=['ebitda'], processor_after_pivot=lambda x: x.apply(calc_ttm, axis=1, result_type='broadcast', whole_df=x))
        # data_to_calc_ebitda_manually = get_factor_from_stock_data('get_em_stock_fin_fac', columns=[
        #     'income_statement_61',
        #     'income_statement_56',
        #     'cashflow_statement_87',
        #     'cashflow_statement_88',
        #     'cashflow_statement_89',
        #     'cashflow_statement_70',
        # ])
        # self._factor = ebitda.fillna(data_to_calc_ebitda_manually.sum(axis=1, level=0, min_count=1))


class EntValueFactor(BasicFactor):
    # 企业价值
    def __init__(self):
        super().__init__('ent_value')
        self._deps.add(TotalDebtAvgFactor())
        self._deps.add(MarketValueFactor())

    def calc(self):
        # def _resample_to_yearly(df):
        #     df.index = pd.to_datetime(df.index, infer_datetime_format=True)
        #     # 只保留年报数据
        #     df = df.resample('1Y').last()
        #     df.index = df.index.date
        #     return df

        # self._factor = get_factor_from_stock_data('get_em_daily_info', columns=['ev_without_cash'])
        # 目前没有东财的数据，我们自己计算一下
        # total_debt = get_factor_from_stock_data('get_em_stock_fin_fac', columns=['balance_statement_128'], processor_after_pivot=_resample_to_yearly)
        total_debt = TotalDebtAvgFactor().get()
        monetary_fund = get_factor_from_stock_data('get_em_stock_fin_fac', columns=['balance_statement_9'], processor_after_pivot=lambda x: x.rolling(4, min_periods=1).mean())
        self._factor = MarketValueFactor().get() + total_debt - monetary_fund


class CashFlowFactor(BasicFactor):
    # 经营性现金流
    def __init__(self):
        super().__init__('cash_flow')

    def calc(self):
        self._factor = get_factor_from_stock_data('get_em_stock_fin_fac', columns=['cashflow_statement_39'])


class CashFlowTTMFactor(BasicFactor):
    # 经营性现金流TTM
    def __init__(self):
        super().__init__('cash_flow_ttm')

    def calc(self):
        self._factor = get_factor_from_stock_data('get_em_stock_fin_fac', columns=['cashflow_statement_39'], processor_after_pivot=lambda x: x.apply(calc_ttm, axis=1, result_type='broadcast', whole_df=x))


class GrossProfitFactor(BasicFactor):
    # 毛利TTM
    def __init__(self):
        super().__init__('gross_profit')
        self._deps.add(IncomeTTMFactor())
        self._deps.add(ExpenseTTMFactor())

    def calc(self):
        df = get_factor_from_stock_data('get_em_stock_fin_fac', columns=['gross_margin_ttmr'])
        # 由于银行等金融类企业的财报里没有毛利润, 这里我们使用毛利润TTM = 营业收入TTM - 营业支出TTM来计算
        gross_profit_manullay = IncomeTTMFactor().get() - ExpenseTTMFactor().get()
        self._factor = df.fillna(gross_profit_manullay)


class FloatAssetAvgFactor(BasicFactor):
    # 流动资产最近四期均值
    def __init__(self):
        super().__init__('float_asset_avg')

    def calc(self):
        self._factor = get_factor_from_stock_data('get_em_stock_fin_fac', columns=['balance_statement_25'], processor_after_pivot=lambda x: x.rolling(4, min_periods=1).mean())


class FloatDebtAvgFactor(BasicFactor):
    # 流动负债最近四期均值
    def __init__(self):
        super().__init__('float_debt_avg')

    def calc(self):
        self._factor = get_factor_from_stock_data('get_em_stock_fin_fac', columns=['balance_statement_93'], processor_after_pivot=lambda x: x.rolling(4, min_periods=1).mean())


class MonetaryFundFactor(BasicFactor):
    # 货币资金
    def __init__(self):
        super().__init__('monetary_fund')

    def calc(self):
        self._factor = get_factor_from_stock_data('get_em_stock_fin_fac', columns=['balance_statement_9'])


class TurnoverFactor(BasicFactor):
    # 换手率
    def __init__(self):
        super().__init__('turnover')

    def calc(self):
        self._factor = get_factor_from_stock_data('get_em_stock_price', columns=['turn'])


class PredictEPSFactor(BasicFactor):
    # 分析师一致预测EPS
    pass
