import pandas as pd
from ...stock.factor.fund_derived_factors import *
from ...stock.factor.fund_derived_score import *
from ...stock.factor.api import FundFactorUpdater

BK_BACKTEST = [FundMngScoreV1,RetAbilityFundScore,RiskAbilityFundScore,StableAbility,WinRateMonthlyTop50,WinRateMonthlyTop75,WinRateMonthlyI]

def combine_factor():
    n = 10
    result = []
    factor_list = BK_BACKTEST
    fac_name_list = [i().name for i in factor_list]
    td = TradingDay()
    td.calc()
    trade_day_df = td._factor
    for fac_i in factor_list:
        fac_class = fac_i()
        fac = fac_class.get()
        td_list = trade_day_df.loc[fac.index[0]:].index.tolist()
        fac = fac.reindex(td_list).ffill()
        fac_name = fac_class.name
        fac.columns = pd.MultiIndex.from_product([[fac_name], fac.columns])
        result.append(fac)
        fac = None
        fac_class.clear(recursive=True)
        txt = (f'load fac {fac_name} ')
        FundFactorUpdater.usage(txt)
    td.clear()
    df = pd.concat(result, axis=1)
    result = []
    FundFactorUpdater.usage('after concat single facs')
    df = df.sort_index()
    idx_pack = int(df.shape[0] / n) + 1
    res = []
    for i in range(n):
        idx_start = i * idx_pack
        idx_end = (i + 1) * idx_pack
        idx_end = min(df.shape[0], idx_end)
        df_i = df.iloc[idx_start:idx_end].stack()
        res.append(df_i)
    df = pd.concat(res)
    df = df.reset_index().dropna(subset=fac_name_list, how='any')
    df = df.rename(columns={'level_0':'datetime','level_1':'fund_id'})
    return df

def combine_factor_test():
    result = []
    factor_list = BK_BACKTEST
    fac_name_list = [i().name for i in BK_BACKTEST]
    for fac_i in factor_list[:2]:
        fac_class = fac_i()
        fac = fac_class.get()
        fac_name = fac_class.name
        fac.columns = pd.MultiIndex.from_product([[fac_name], fac.columns])
        result.append(fac)
        fac_class.clear(recursive=True)
    df = pd.concat(result, axis=1).stack()
    df = df.reset_index()#.dropna(subset=fac_name_list, how='any')
    df = df.rename(columns={'level_0':'datetime','level_1':'fund_id'})
    for i in BK_BACKTEST:
        fac_name = i().name
        if fac_name not in df.columns:
            df.loc[:, fac_name] = None
    return df