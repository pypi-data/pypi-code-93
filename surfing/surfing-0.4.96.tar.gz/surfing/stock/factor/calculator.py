import numpy as np
import pandas as pd
from statsmodels.tsa.ar_model import AutoReg
import statsmodels.api as sm

class Calculator:

    TRADING_DAYS_PER_YEAR = 242
    MIN_TIME_SPAN = int(TRADING_DAYS_PER_YEAR / 4)#为了延长基金回测范围，评分最低年限3个月
    RISK_FEE_RATE = 0.025
    RISK_FEE_RATE_PER_DAY = RISK_FEE_RATE / TRADING_DAYS_PER_YEAR
    PUNISH_RATIO = 0.8
    HARD_PUNISH_RATIO = 0.6
    FUND_CLASSIFIER = {
        'stock': ['普通股票型基金', '偏股混合型基金',  '被动指数型基金', '增强指数型基金', '平衡混合型基金', '灵活配置型基金', '股票多空'],
        'bond': ['中长期纯债型基金', '短期纯债型基金', '偏债混合型基金', '增强指数型债券基金', '被动指数型债券基金','混合债券型二级基金', '混合债券型一级基金'], 
        'QDII': ['国际(QDII)股票型基金', '国际(QDII)债券型基金', '国际(QDII)另类投资基金', '国际(QDII)混合型基金', ],
        'mmf': ['货币市场型基金'],
        'index': ['被动指数型基金', '增强指数型基金', '增强指数型债券基金', '被动指数型债券基金', '商品型基金', 'REITs'],
    }

    FILTER_NAV_RATIO = {
        'stock' : 0.1,
        'QDII'  : 0.1,
        'index' : 0.1,
        'bond'  : 0.07,
        'mmf'   : 0.01,
    }

    WIND_TYPE_DICT = {}
    for type_i, type_list in FUND_CLASSIFIER.items():
        for _ in type_list:
            WIND_TYPE_DICT.update({_:type_i})

    REPLACE_DICT = {'stock': 'csi_stockfund',
                     'bond': 'csi_boodfund', 
                     'mmf':  'mmf', 
                     'QDII': 'csi_f_qdii', 
                     'index':'hs300'}

    INDEX_DICT = { v : k for k, v in REPLACE_DICT.items()}

    @staticmethod
    def rolling_alpha_beta(x, res, df):
        df_i = df.loc[x[0]:x[-1],]
        return Calculator._rolling_alpha_beta(res, df_i)

    @staticmethod
    def rolling_cl_alpha_beta(x, res, df):
        df_i = df.loc[x[0]:x[-1],][['fund','benchmark']].to_numpy()
        return Calculator._rolling_cl_alpha_beta(res, df_i)

    @staticmethod
    def rolling_tm_alpha_beta(x, res, df):
        df_i = df.loc[x[0]:x[-1],][['fund','benchmark']].to_numpy()
        return Calculator._rolling_tm_alpha_beta(res, df_i)

    @staticmethod
    def rolling_hm_alpha_beta(x, res, df):
        df_i = df.loc[x[0]:x[-1],][['fund','benchmark']].to_numpy()
        return Calculator._rolling_hm_alpha_beta(res, df_i)

    @staticmethod
    def rolling_mdd(x):
        # fmax nanmin ignore nan
        x_max = np.fmax.accumulate(x, axis=0)
        return 1 - np.nanmin(x / x_max)

    @staticmethod
    def rolling_annual_ret(x):
        not_null_x = x[~np.isnan(x)]
        year = not_null_x.shape[0] / Calculator.TRADING_DAYS_PER_YEAR
        last_p = x[-1]
        first_p = not_null_x[0]
        return np.exp(np.log(last_p/first_p)/year) - 1
    
    @staticmethod
    def rolling_monthly_annual_ret(x):
        not_null_x = x[~np.isnan(x)]
        year = not_null_x.shape[0] / 12
        last_p = x[-1]
        first_p = not_null_x[0]
        return np.exp(np.log(last_p/first_p)/year) - 1
    
    @staticmethod
    def rolling_totol_ret(x):
        not_null_x = x[~np.isnan(x)]
        last_p = x[-1]
        first_p = not_null_x[0]
        return last_p / first_p

    @staticmethod
    def rolling_trade_year(x):
        not_null_x = x[~np.isnan(x)]
        year = not_null_x.shape[0] / Calculator.TRADING_DAYS_PER_YEAR
        return year

    @staticmethod
    def rolling_auto_reg(x):
        not_null_x = x[~np.isnan(x)]
        if len(not_null_x) < 6:
            return np.nan
        mod = AutoReg(endog=not_null_x, lags=1)
        res = mod.fit()
        continue_regress_v = res.params[0]
        return continue_regress_v

    @staticmethod
    def _rolling_alpha_beta(res, df_i):
        if sum(df_i.fund) == 0:
            res.append({'alpha':np.Inf,'beta':np.Inf})
            return 1
        else:
            ploy_res = np.polyfit(y=df_i.fund, x=df_i.benchmark,deg=1)
            p = np.poly1d(ploy_res)
            beta = ploy_res[0]
            alpha = ploy_res[1] * Calculator.TRADING_DAYS_PER_YEAR
            res.append({'alpha':alpha,'beta':beta})
            return 1
    
    @staticmethod
    def _rolling_cl_alpha_beta(res, total: np.ndarray):
        if total.shape[0] <= 1:
            res.append({'beta':np.nan,
                    'alpha':np.nan,
                    })
            return 1
        X = np.array([total[:, 1], total[:, 1]]).T
        X[:, 0][X[:, 0] < 0] = 0
        X[:, 1][X[:, 1] > 0] = 0
        if np.count_nonzero(X[:, 1]) == 0:
            res.append({'beta':np.nan,
                    'alpha':np.nan,
                    })
            return 1
        est2 = sm.OLS(total[:, 0], sm.add_constant(X, prepend=False)).fit()
        res.append({'beta':est2.params[0] - est2.params[1],
                'alpha':est2.params[-1],
                })
        return 1
    
    @staticmethod
    def _rolling_tm_alpha_beta(res, total: np.ndarray):
        if total.shape[0] <= 1:
            res.append({'beta':np.nan,
                    'alpha':np.nan,
                    })
            return 1
        X = np.array([total[:, 1], total[:, 1]]).T
        X = np.array([total[:, 1], total[:, 1] * total[:, 1]]).T
        if np.count_nonzero(X[:, 1]) == 0:
            res.append({'beta':np.nan,
                    'alpha':np.nan,
                    })
            return 1
        est2 = sm.OLS(total[:, 0], sm.add_constant(X, prepend=False)).fit()
        res.append({'beta':est2.params[1],
                'alpha':est2.params[-1],
                })
        return 1

    @staticmethod
    def _rolling_hm_alpha_beta(res, total: np.ndarray):
        if total.shape[0] <= 1:
            res.append({'beta':np.nan,
                        'alpha':np.nan,
                        })
            return 1
        X = np.array([total[:, 1], total[:, 1]]).T
        X[:, 1][X[:, 1] < 0] = 0
        if np.count_nonzero(X[:, 1]) == 0:
            res.append({'beta':np.nan,
                        'alpha':np.nan,
                        })
            return 1
        est2 = sm.OLS(total[:, 0], sm.add_constant(X, prepend=False)).fit()
        res.append({'beta':est2.params[1],
                    'alpha':est2.params[-1],
                    })
        return 1

    @staticmethod
    def data_reindex_daily_trading_day(data, tradingday):
        # 日线因子交易日对齐
        td = pd.to_datetime(data.index)
        td = [i.date() for i in td]
        data.index = td
        data = data.reindex(data.index.union(tradingday.index))
        data = data.ffill().reindex(tradingday.index)
        return data

    @staticmethod
    def data_reindex_daily_trading_day_not_fill(data, tradingday):
        td = pd.to_datetime(data.index)
        td = [i.date() for i in td]
        data.index = td
        data = data.reindex(data.index.union(tradingday.index))
        data = data.reindex(tradingday.index)
        return data

    @staticmethod
    def data_resample_monthly_ret(df, rule='1M', min_count=15):
        df = df.set_axis(pd.to_datetime(df.index), inplace=False).resample(rule).sum(min_count=min_count)
        df.index = [i.date() for i in df.index]
        df.index.name = 'datetime'
        return df

    @staticmethod
    def data_resample_weekly_ret(df, rule='1W', min_count=3):
        df = df.set_axis(pd.to_datetime(df.index), inplace=False).resample(rule).sum(min_count=min_count)
        df.index = [i.date() for i in df.index]
        df.index.name = 'datetime'
        return df

    @staticmethod
    def data_resample_monthly_nav(df, rule='1M'):
        df = df.set_axis(pd.to_datetime(df.index), inplace=False).resample(rule).last()
        df.index = [i.date() for i in df.index]
        df.index.name = 'datetime'
        return df

    @staticmethod
    def data_resample_weekly_nav(df, rule='1W'):
        df = df.set_axis(pd.to_datetime(df.index), inplace=False).resample(rule).last()
        df.index = [i.date() for i in df.index]
        df.index.name = 'datetime'
        return df

    