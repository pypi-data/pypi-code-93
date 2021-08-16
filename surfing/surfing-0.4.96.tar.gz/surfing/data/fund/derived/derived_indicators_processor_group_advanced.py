from typing import List, Dict
import pandas as pd
import numpy as np
import math
import datetime
import traceback
import json
import statsmodels.api as sm
import time
from multiprocessing import Pool
from scipy.optimize import Bounds, minimize
import statsmodels.api as sm
from statsmodels import regression
from statsmodels.tsa.ar_model import AutoReg
from pandas.tseries.offsets import DateOffset
from ...api.raw import RawDataApi
from ...api.basic import BasicDataApi
from ...api.derived import DerivedDataApi
from ...view.derived_models import FundIndicatorGroup
from .derived_data_helper import DerivedDataHelper, normalize, score_rescale


class FundIndicatorProcessorGroup:

    TRADING_DAYS_PER_YEAR = 242
    TRADING_DAYS_PER_MONTH = 20
    RISK_FEE_RATE = 0.011
    RISK_FEE_RATE_PER_DAY = RISK_FEE_RATE / TRADING_DAYS_PER_YEAR
    NATURAL_DAYS_PER_YEAR = 360
    REPORT_DATE_LIST = ['0331', '0630', '0930', '1231']
    FUND_CLASSIFIER = {
        'QDII': ['国际(QDII)股票型基金', '国际(QDII)债券型基金', '国际(QDII)另类投资基金', '国际(QDII)混合型基金', ],
        'stock': ['普通股票型基金', '偏股混合型基金',  '被动指数型基金', '增强指数型基金', '平衡混合型基金', '灵活配置型基金', '股票多空'], 
        'bond': ['中长期纯债型基金', '短期纯债型基金', '偏债混合型基金', '增强指数型债券基金', '被动指数型债券基金','混合债券型二级基金', '混合债券型一级基金'],
        'mmf': ['货币市场型基金'],
        'index': ['被动指数型基金', '增强指数型基金', '增强指数型债券基金', '被动指数型债券基金', '商品型基金', 'REITs'],
    }
    REPLACE_DICT = {'stock': 'csi_stockfund',
                     'bond': 'csi_boodfund', 
                     'mmf':  'mmf', 
                     'QDII': 'csi_f_qdii', 
                     'index':'hs300'}

    def __init__(self, data_helper: DerivedDataHelper):
        self.data_helper = data_helper
        self.basic_api = BasicDataApi()

    def init(self, end_date: str = '20201023'):
        self.end_date = pd.to_datetime(end_date, infer_datetime_format=True).date()
        self.wind_type_dict = {}
        for type_i, type_list in self.FUND_CLASSIFIER.items():
            for _ in type_list:
                self.wind_type_dict.update({_:type_i})
        
        # 交易日
        self.trading_days = self.basic_api.get_trading_day_list().drop(columns='_update_time').set_index('datetime')
        self.trading_days = self.trading_days.loc[: self.end_date]
        self.begin_date = self.trading_days.tail(242).index[0]
        # 基金信息
        self.fund_info = self.basic_api.get_fund_info().drop(columns='_update_time')
        self.fund_info = self.fund_info[(self.fund_info.end_date >= self.end_date) 
                                       & (self.fund_info.structure_type <= 1)
                                       & (~self.fund_info.wind_class_2.isnull())
                                       & (self.fund_info.start_date <= self.begin_date)]
        self.wind_class_2_dict = self.fund_info.set_index('fund_id')['wind_class_2'].to_dict()

        # 成立半年不算 TODO
        # 基金净值
        fund_list = self.fund_info.fund_id.tolist()
        #fund_list = ['000001!0','000003!0','000004!0','000005!0','000006!0','000008!0','000009!0','000010!0']  # if test
        self.fund_nav = self.basic_api.get_fund_nav_with_date(end_date = self.end_date, fund_list = fund_list)
        self.fund_nav: pd.DataFrame = self.fund_nav.pivot_table(index='datetime', columns='fund_id', values='adjusted_net_value')
        self.fund_nav = self.fund_nav.reindex(self.trading_days.index).fillna(method='ffill').dropna(axis=0,how='all')
        self.fund_list = self.fund_nav.columns.tolist()

        self.fund_ret = np.log(self.fund_nav).diff().dropna(axis=0,how='all')
        self.fund_ret[self.fund_ret > 0.15] = 0

        # 存款利率
        bank_rate_df = self.basic_api.get_index_price(index_list=['ddir', 'nonor', 'tmd_1y', 'tmd_2y', 'tmd_3m', 'tmd_3y', 'tmd_5y', 'tmd_6m', 'tmd_7d'])
        bank_rate_df = bank_rate_df.pivot_table(index='datetime', columns='index_id', values='close')
        bank_rate_df = bank_rate_df.reindex(self.trading_days.index.union(bank_rate_df.index)).fillna(method='ffill').reindex(self.trading_days.index)
        
        # 基金基准数据
        self.index_price = self.basic_api.get_index_price_dt(end_date=end_date, columns=['close'])
        self.index_price = self.index_price.pivot_table(index='datetime', columns='index_id', values='close')
        self.index_price = self.index_price.reindex(self.trading_days.index).fillna(method='ffill')
        drop_list = [i for i in self.index_price if i in bank_rate_df]
        self.index_price = self.index_price.drop(drop_list, axis=1)
        self.index_price = pd.concat([self.index_price, bank_rate_df], axis=1)
        
        # 宏观数据
        self.macroeco = RawDataApi().get_em_macroeconomic_daily(codes=['EX_DR_RATIO']).drop(columns='_update_time')
        self.macroeco = self.macroeco.pivot_table(index='datetime', columns='codes', values='value')
        self.macroeco = self.macroeco.reindex(self.trading_days.index.union(self.macroeco.index)).fillna(method='ffill').reindex(self.trading_days.index)

        # 大类指数价格
        self.fund_type_benchmark = self.index_price[[self.REPLACE_DICT[fund_type] for fund_type in self.FUND_CLASSIFIER]]
        self.fund_type_benchmark = self.fund_type_benchmark.rename(columns={v : f'{k}_bench' for k, v in self.REPLACE_DICT.items()})
        self.fund_type_benchmark = np.log(self.fund_type_benchmark).diff().dropna(axis=0,how='all')

        # 规模
        self.fund_size: pd.DataFrame = self.basic_api.get_fund_size_range(end_date=end_date)
        self.fund_size = self.fund_size.pivot_table(index='datetime', columns='fund_id', values='size')
        self.fund_size = self.fund_size.reindex(self.trading_days.index.union(self.fund_size.index)).fillna(method='ffill').reindex(self.trading_days.index)

        # 基准计算
        self.fund_benchmark_df = self.basic_api.get_fund_benchmark().drop(columns='_update_time')
        self.benchmark_ret = self.get_benchmark_return()
        self.benchmark_ret = self.benchmark_ret.reindex(self.trading_days.index)
        benchmark_cols = self.benchmark_ret.columns.tolist()
        for fund_id in self.fund_nav.columns:
            benchmark_id = fund_id
            if not benchmark_id in benchmark_cols:    
                wind_class_2 = self.wind_class_2_dict[fund_id]
                select_type = self.wind_type_dict[wind_class_2]
                benchmark_ret = self.index_price[self.REPLACE_DICT[select_type]].pct_change(1).rename(benchmark_id)
                self.benchmark_ret = self.benchmark_ret.join(benchmark_ret)
        self.fund_ret = self.fund_ret.join(self.benchmark_ret, rsuffix='_b').join(self.fund_type_benchmark)


        # 获取年报/半年报的发布日期
        md = self.end_date.strftime('%m%d')
        sentry_date = pd.Series(self.REPORT_DATE_LIST)
        sentry = sentry_date[sentry_date <= md]
        # 为半年报/年报发布预留一个季度的缓冲时间
        if sentry.empty:
            real_date = datetime.date(self.end_date.year - 1, 6, 30)
        elif len(sentry) <= 2:
            real_date = datetime.date(self.end_date.year - 1, 12, 31)
        else:
            real_date = datetime.date(self.end_date.year, 6, 30)

        # 基金机构持仓
        self.fund_hold = self.basic_api.get_history_fund_size(start_date=real_date, end_date=real_date)
        self.fund_hold = self.fund_hold[['fund_id', 'institution_holds', 'hold_num']].set_index('fund_id')
        self.fund_hold = self.fund_hold.rename(columns={'institution_holds':'ins_hold'})

        # 货基相关风险数据
        self.risk_metric = self.basic_api.get_fund_hold_asset_by_id(start_date=real_date, end_date=real_date)
        self.risk_metric = self.risk_metric[['fund_id', 'first_repo_to_nav', 'avg_ptm']].set_index('fund_id')
        self.risk_metric = self.risk_metric.rename(columns={'first_repo_to_nav':'leverage','avg_ptm':'ptm'})

        # 月度化
        self.fund_ret_monthly = self.get_resample_ret(self.fund_ret)
        self.fund_ret_monthly.index = self.fund_ret_monthly.index.date

        # 周度化
        self.fund_ret_weekly = self.get_resample_ret(df=self.fund_ret, rule='1W', min_count=3).dropna(axis=0, how='all')
        self.fund_ret_weekly.index = self.fund_ret_weekly.index.date
        
        # 周期
        self.period = ['1y', '3y', '5y', 'history']
        # monthly ret
        _df = self.fund_nav.tail(20)
        self.monthly_ret = _df.iloc[-1] / _df.iloc[0]
        self.fund_info = self.fund_info.set_index('fund_id')

    def get_benchmark_return(self) -> pd.DataFrame:
        benchmark_list: Dict[str, float] = {}
        # 遍历每一只基金的benchmark进行处理
        for row in self.fund_benchmark_df.itertuples(index=False):
            values: List[pd.Series] = []
            cons: float = 0
            # 空的benchmark表明我们没有对应的指数或无法解析公式
            if row.benchmark_s:
                benchmark: Dict[str, float] = json.loads(row.benchmark_s)
                benchmark_raw: Dict[str, float] = eval(row.benchmark)
                for (index, weight), index_raw in zip(benchmark.items(), benchmark_raw.keys()):
                    if index == '1':
                        # 表示benchmark中该项为常数
                        cons += weight
                    elif index in ('ddir', 'nonor', 'tmd_1y', 'tmd_2y', 'tmd_3m', 'tmd_3y', 'tmd_5y', 'tmd_6m', 'tmd_7d'):
                        if weight == -1:
                            # 表示我们无法解析公式
                            # print(f'[benchmark_return] Error: Need fix {row.fund_id} {index} {index_raw}')
                            # self.log.append((row.fund_id, index))
                            break
                        else:
                            try:
                                if index == 'nonor':
                                    # 在这里我们用超额存款准备金率替代同业存款利率
                                    ra: pd.Series = self.macroeco.loc[:, 'EX_DR_RATIO']
                                else:
                                    ra: pd.Series = self.index_price.loc[:, index]
                            except KeyError:
                                # 表示我们没有该指数的价格数据
                                # print(f'[benchmark_return] Error: Data Missing: {row.fund_id} {index} {index_raw}')
                                # self.log.append((row.fund_id, index))
                                break
                            else:
                                values.append(ra.iloc[1:] * 0.01 * weight / self.TRADING_DAYS_PER_YEAR)
                    else:
                        if weight == -1:
                            # 表示我们无法解析公式
                            # print(f'[benchmark_return] Error: Need fix {row.fund_id} {index} {index_raw}')
                            # self.log.append((row.fund_id, index))
                            break
                        else:
                            try:
                                ra: pd.Series = self.index_price.loc[:, index]
                            except KeyError:
                                # 表示我们没有该指数的价格数据
                                # print(f'Error: Data Missing: {row.fund_id} {index} {index_raw}')
                                # self.log.append((row.fund_id, index))
                                break
                            else:
                                ra = np.log(ra).diff().iloc[1:]
                                values.append(ra * weight)
                else:
                    if values or cons:
                        the_sum: float = sum(values)
                        if cons:
                            the_sum += np.log(math.pow(1 + cons, 1 / self.TRADING_DAYS_PER_YEAR))
                        benchmark_list[row.fund_id] = the_sum

        return pd.DataFrame.from_dict(benchmark_list)

    def get_resample_ret(self, df, rule='1M', min_count=15):

        return df.set_axis(pd.to_datetime(df.index), inplace=False).resample(rule).sum(min_count=min_count)

    def get_begin_date(self, period: str):
        if period == '1y':
            return self.trading_days.tail(self.TRADING_DAYS_PER_YEAR * 1).index[0]

        if period == '3y':
             return self.trading_days.tail(self.TRADING_DAYS_PER_YEAR * 3).index[0]

        if period == '5y':
             return self.trading_days.tail(self.TRADING_DAYS_PER_YEAR * 5).index[0]

        if period == 'history':
            return  self.trading_days.index[0]

    def calc_stutzer(self, ex_return: np.ndarray):
        information_statistic = lambda theta: np.log(np.mean(np.exp(theta[0] * ex_return)))
        theta0 = [-1.]
        bounds = Bounds((-np.inf), (0))
        result = minimize(information_statistic, theta0, method='SLSQP', bounds=bounds, tol=1e-16)
        if result.success:
            information_statistic = -result.fun
            if information_statistic <= 0:
                return 0
            stutzer_index = np.abs(np.mean(ex_return)) / np.mean(ex_return) * np.sqrt(2 * information_statistic)
            return stutzer_index
        else:
            return np.nan
    
    def calc_cl_alpha_beta(self, total: np.ndarray):
        if total.shape[0] <= 1:
            return {'beta':np.nan,
                    'alpha':np.nan,
                    }
        X = np.array([total[:, 1], total[:, 1]]).T
        X[:, 0][X[:, 0] < 0] = 0
        X[:, 1][X[:, 1] > 0] = 0
        if np.count_nonzero(X[:, 1]) == 0:
            return {'beta':np.nan,
                    'alpha':np.nan,
                    }
        est2 = sm.OLS(total[:, 0], sm.add_constant(X, prepend=False)).fit()
        return {'beta':est2.params[0] - est2.params[1],
                'alpha':est2.params[-1],
                }

    def calc_continue_regress_v(self, df, period='monthly'):
        if period == 'monthly':
            # 半年周期
            window = 6
            yearly_multiplier = 2
            period_num = 12
        df.loc[:,'annual_ret'] = df.fund_ret.rolling(window=window).apply(lambda x : x.sum() * yearly_multiplier - self.RISK_FEE_RATE)
        df.loc[:,'annual_vol'] = df.fund_ret.rolling(window=window).apply(lambda x : x.std(ddof=1) * np.sqrt(period_num))
        df.loc[:,'sharpe'] = df.loc[:,'annual_ret'] / df.loc[:,'annual_vol']
        df = df.replace(np.Inf, 0).replace(-np.Inf, 0).dropna() # 空值sharpe赋值0
        if df.shape[0] < 6:
            return np.nan
        mod = AutoReg(endog=df['sharpe'].dropna().values, lags=1)
        res = mod.fit()
        continue_regress_v = res.params[0]
        return continue_regress_v

    def calcualtor(self, df, period='monthly'):
        if period == 'monthly':
            yearly_multiplier = 12
            period_days = self.TRADING_DAYS_PER_MONTH
        x = df.benchmark_ret.values
        y = df.fund_ret.values
        z = df.benchmark_real.values
        ex_ret_mmf = df.fund_ret - df.mmf_bench
        x = sm.add_constant(x)
        model = regression.linear_model.OLS(y,x).fit()
        x = x[:,1]
        alpha = model.params[0] * yearly_multiplier
        beta = model.params[1]
        track_err = (y - z).std(ddof=1) * np.sqrt(yearly_multiplier) 
        downside_std = y[y < (self.RISK_FEE_RATE_PER_DAY * period_days)].std(ddof=1)
        info_ratio = alpha / track_err
        treynor = (np.nanmean(y) - self.RISK_FEE_RATE_PER_DAY * period_days) / beta if beta != 0 else np.nan
        mdd_part =  df.fund_nav[:] / df.fund_nav[:].rolling(window=df.shape[0], min_periods=1).max()
        mdd = 1 - mdd_part.min()
        if np.isnan(mdd):
            mdd_len = np.nan
        else:
            mdd_date2 = mdd_part.idxmin()
            mdd_date1 = df.fund_nav[:mdd_date2].idxmax()
            mdd_len = (mdd_date2 - mdd_date1).days

        annual_ret = df.fund_ret.sum() * (yearly_multiplier / df.shape[0]) - self.RISK_FEE_RATE
        annual_vol = df.fund_ret.std(ddof=1) * np.sqrt(yearly_multiplier)
        sharpe = annual_ret / annual_vol
        calma_ratio = annual_ret / mdd if mdd != 0 else np.nan
        var = np.quantile(df.fund_ret, 0.05)
        cvar = df.fund_ret[df.fund_ret <= var].mean()
        winning_rate_mmf = len(ex_ret_mmf[ex_ret_mmf > 0]) / len(ex_ret_mmf)
        stutzer = self.calc_stutzer(df.fund_ret - self.RISK_FEE_RATE_PER_DAY * period_days) * np.sqrt(yearly_multiplier)
        cl_res = self.calc_cl_alpha_beta(df[['fund_ret','benchmark_ret']].to_numpy())
        stock_cl_alpha = cl_res['alpha']
        stock_cl_beta = cl_res['beta']
        continue_regress_v = self.calc_continue_regress_v(df, period)
        
        return {
            'alpha':alpha,
            'beta':beta,
            'track_err':track_err,
            'downside_std':downside_std,
            'info_ratio':info_ratio,
            'treynor':treynor,
            'mdd':mdd,
            'mdd_len':mdd_len,
            'annual_vol':annual_vol,
            'annual_ret':annual_ret,
            'sharpe':sharpe,
            'calma_ratio':calma_ratio,
            'var':var,
            'cvar':cvar,
            'winning_rate_mmf':winning_rate_mmf,
            'stutzer':stutzer,
            'stock_cl_alpha':stock_cl_alpha,
            'stock_cl_beta':stock_cl_beta,
            'continue_regress_v':continue_regress_v,
        }

    def loop_item(self, fund_id):
        _t0 = time.time()
        idx = self.fund_list.index(fund_id)
        wind_class_2 = self.wind_class_2_dict[fund_id]
        type_class = self.wind_type_dict[wind_class_2]
        cols = [fund_id,f'{fund_id}_b',f'{type_class}_bench']
        fund_data = self.fund_ret_monthly[cols]
        fund_data['fund_nav'] = np.exp(fund_data[fund_id].cumsum())
        fund_data = fund_data.rename(columns={fund_id:'fund_ret',f'{type_class}_bench':'benchmark_ret',f'{fund_id}_b':'benchmark_real'})
        fund_data = fund_data.join(self.fund_ret_monthly['mmf_bench'])
        fund_result = {
            'fund_id': fund_id,
            'datetime': self.end_date
        }
        for period in self.period:
            begin_date = self.get_begin_date(period)
            fund_data_period =  fund_data.loc[begin_date:].copy().dropna()
            if all(fund_data_period.fund_ret == 0):
                continue
            period_result = self.calcualtor(fund_data_period, 'monthly')
            period_result = { f'{k}~{period}_m' : v for k, v in period_result.items() }
            fund_result.update(period_result)

        cols = [fund_id, f'{type_class}_bench']
        fund_data = self.fund_ret_weekly[cols]
        df = fund_data.rename(columns={fund_id:'fund_ret',f'{type_class}_bench':'benchmark_ret'}).dropna()
        cl_res = self.calc_cl_alpha_beta(df[['fund_ret','benchmark_ret']].to_numpy())
        stock_cl_alpha = cl_res['alpha']
        stock_cl_beta = cl_res['beta']
        fund_result.update({'stock_cl_alpha~history_w':stock_cl_alpha})
        fund_result.update({'stock_cl_beta~history_w':stock_cl_beta})
        _t1 = time.time()
        #print(f'{fund_id} {idx} / {len(self.fund_list)} cost time {_t1 - _t0}')
        return fund_result

    def calc_indicator(self):
        _t00 = time.time()
        self.result = []
        self.fund_size_columns = self.fund_size.columns.tolist()
        self.fund_hold_columns = self.fund_hold.columns.tolist()
        self.risk_funds_list = self.risk_metric.index
        for fund_id in self.fund_list:
            try:
                self.result.append(self.loop_item(fund_id))
            except:
                print(f'boom fund_id {fund_id}')
        self.result_df = pd.DataFrame(self.result)
        self.result_df = pd.merge(self.result_df, self.fund_hold, on=['fund_id'])
        self.result_df = pd.merge(self.result_df, self.risk_metric, on=['fund_id']).set_index('fund_id')
        self.result_df.loc[:,'prn_hold'] = 100 - self.result_df['ins_hold']
        self.result_df.loc[:,'scale'] = self.fund_size.loc[self.end_date]
        self.result_df.loc[:,'monthly_ret'] = self.monthly_ret
        self.result_df.loc[:,'total_ret'] = np.exp(self.fund_ret.sum())
        self.result_df.loc[:,'mdd~history_daily'] = 1 - (self.fund_nav / self.fund_nav.cummax()).min()
        self.result_df = self.result_df.reset_index()

        self.fund_info.loc[:,'trade_days'] = [i.days for i in (self.end_date - self.fund_info.start_date)]
        self.fund_info.loc[:,'fund_type'] = self.fund_info.wind_class_2.map(self.wind_type_dict)
        self.result_df = self.result_df.set_index('fund_id')
        self.result_df = self.result_df.join(self.fund_info[['wind_class_2','fund_type','desc_name']])
        self.result_df = self.result_df.replace(np.Inf,np.nan).replace(-np.Inf,np.nan)
        self.result_df= self.result_df.join(self.fund_info[['trade_days']])
        self.indicator = self.result_df.copy()
        _t11 = time.time()
        print(f'total cost time {_t11 - _t00}')

    def calc_score(self):
        res = []
        for fund_type in self.FUND_CLASSIFIER:
            df = self.indicator[self.indicator['fund_type'] == fund_type].copy()
            ret = 0.1 * normalize(df['annual_ret~1y_m']) + 0.1 * normalize(df['annual_ret~3y_m']) + 0.3 * normalize(df['annual_ret~5y_m']) + 0.2 * normalize(df['annual_ret~history_m'])
            if fund_type == 'stock':
                #df.loc[:,'ret_ability'] = score_rescale(0.6 * normalize(df['alpha~history_m']) + 0.4 * ret)
                df.loc[:,'ret_ability'] = score_rescale( 0.4 * score_rescale(df['annual_ret~history_m']) + 0.6 * score_rescale(df['total_ret']))
                df.loc[:,'risk_ability'] = score_rescale(0.3 * score_rescale(-df['mdd~history_daily']) + 0.4 * score_rescale(-df['annual_vol~history_m']) + 0.3 * score_rescale(-df['downside_std~history_m']))
                df.loc[:,'stable_ability'] = score_rescale(0.4 * score_rescale(df['trade_days']) + 0.4 * score_rescale(df['continue_regress_v~history_m']) + 0.2 * score_rescale(df['scale']))
                df.loc[:,'select_time'] =  score_rescale(normalize(df['stock_cl_beta~history_w']))
                df.loc[:,'select_stock'] = score_rescale(normalize(df['stock_cl_alpha~history_w']))
                df.loc[:,'total_score'] = score_rescale(df.loc[:,'ret_ability'] + df.loc[:,'risk_ability'] + df.loc[:,'stable_ability'] + df.loc[:,'select_time'] + df.loc[:,'select_stock'] )
            
            elif fund_type == 'bond':
                df.loc[:,'ret_ability'] = score_rescale( 0.8 * score_rescale(df['annual_ret~history_m']) + 0.2 * score_rescale(df['total_ret']))
                df.loc[:,'risk_ability'] = score_rescale(0.3 * score_rescale(-df['mdd~history_daily']) + 0.4 * score_rescale(-df['annual_vol~history_m']) + 0.3 * score_rescale(-df['downside_std~history_m']))
                df.loc[:,'stable_ability'] = score_rescale(0.4 * score_rescale(df['trade_days']) + 0.4 * score_rescale(df['continue_regress_v~history_m']) + 0.2 * score_rescale(df['scale']))
                df.loc[:,'select_time'] =  score_rescale(normalize(df['stock_cl_beta~history_w']))
                df.loc[:,'select_stock'] = score_rescale(normalize(df['stock_cl_alpha~history_w']))
                df.loc[:,'total_score'] = score_rescale(df.loc[:,'ret_ability'] + df.loc[:,'risk_ability'] + df.loc[:,'stable_ability'] + df.loc[:,'select_time'] + df.loc[:,'select_stock'] )
            
            elif fund_type == 'index':
                df.loc[:,'ret_ability'] = score_rescale( 0.4 * score_rescale(df['annual_ret~history_m']) + 0.6 * score_rescale(df['total_ret']))
                #df.loc[:,'track_ability'] = score_rescale(-normalize(df['track_err~history_m']))
                df.loc[:,'risk_ability'] = score_rescale(0.3 * score_rescale(-df['mdd~history_daily']) + 0.4 * score_rescale(-df['annual_vol~history_m']) + 0.3 * score_rescale(-df['downside_std~history_m']))
                df.loc[:,'stable_ability'] = score_rescale(0.4 * score_rescale(df['trade_days']) + 0.4 * score_rescale(df['continue_regress_v~history_m']) + 0.2 * score_rescale(df['scale']))
                df.loc[:,'total_score'] = score_rescale(df.loc[:,'ret_ability'] + df.loc[:,'risk_ability'] + df.loc[:,'stable_ability'] )
            
            elif fund_type == 'QDII':
                df.loc[:,'ret_ability'] = score_rescale( 0.4 * score_rescale(df['annual_ret~history_m']) + 0.6 * score_rescale(df['total_ret']))
                df.loc[:,'risk_ability'] = score_rescale(0.3 * score_rescale(-df['mdd~history_daily']) + 0.4 * score_rescale(-df['annual_vol~history_m']) + 0.3 * score_rescale(-df['downside_std~history_m']))
                df.loc[:,'stable_ability'] = score_rescale(-normalize(df['annual_vol~history_m']))
                df.loc[:,'select_time'] = np.nan
                df.loc[:,'select_stock'] = np.nan
                df.loc[:,'total_score'] = score_rescale(df.loc[:,'ret_ability'] + df.loc[:,'risk_ability'] + df.loc[:,'stable_ability'] )
            
            elif fund_type == 'mmf':
                df.loc[:,'ret_ability'] = score_rescale(normalize(df['monthly_ret']))
                df.loc[:,'risk_ability'] = score_rescale(normalize(df['prn_hold']) + normalize(df['scale']))
                df.loc[:,'total_score'] = score_rescale(df.loc[:,'ret_ability'] + df.loc[:,'risk_ability'] )
            res.append(df)
        self.fund_indicator_score = pd.concat(res)

    def get_mng_best_fund(self):
        desc_dic = self.fund_info[['fund_id','desc_name']].set_index('fund_id').to_dict()['desc_name']
        manager_info = self.fund_manager_info[self.fund_manager_info.end  == datetime.date(2040,1,1)].copy()
        mng_name_dic = self.fund_manager_info.reset_index()[['manager_id','name']].set_index('manager_id').to_dict()['name']
        res = []
        for fund_type in self.mng_best_fund:
            _df = self.mng_best_fund['stock'].tail(1).reset_index().drop(columns=['datetime']).dropna(axis=1).replace(desc_dic).rename(columns=mng_name_dic).T
            _df = _df.reset_index().rename(columns={'index':'mng_name',0:'desc_name'})
            _df.loc[:,'fund_type'] = fund_type
            res.append(_df)
        self.mng_best_fund_now = pd.concat(res)

    def score_rescale(self, df):
        return df.rank(pct=True) * 100

    def add_mng_score(self):
        bucket_name = 'tl-fund-dm'
        _s3_bucket_uri: str = f's3://{bucket_name}/dm'
        name = 'mng_indicator_score'
        s3_uri = f'{_s3_bucket_uri}/{name}.parquet'
        score = pd.read_parquet(s3_uri)
        
        mng_info = DerivedDataApi().get_fund_manager_info().set_index('mng_id')
        mng_dic = mng_info[mng_info.end_date == datetime.date(2040,1,1)]['fund_id']

        # 找基金对应基金经理分数
        fund_type_list = list(self.fund_indicator_score.fund_type.unique())
        res = []
        for fund_type in fund_type_list:
            _score = score[score.fund_type == fund_type].copy().dropna(subset=['total_score'])
            _fund_indicator_part = self.fund_indicator_score[self.fund_indicator_score.fund_type == fund_type]#[['total_score']]
            _score = _score.set_index('mng_id').join(mng_dic)
            _score = _score.reset_index().set_index('fund_id').rename(columns={'total_score':'mng_score'})[['mng_score']]
            _score = _score.reset_index().groupby('fund_id').max()
            _fund_indicator_part = _fund_indicator_part.drop(columns='mng_score',errors='ignore').join(_score['mng_score'])
            res.append(_fund_indicator_part)
        fund_indicator = pd.concat(res,axis=0)
        dic = {
            'stock':['ret_ability','risk_ability','stable_ability','select_time','select_stock','mng_score'],
            'bond':['ret_ability','risk_ability','stable_ability','select_time','select_stock','mng_score'],
            'index':['ret_ability','risk_ability','stable_ability','mng_score'],
            'QDII':['ret_ability','risk_ability','stable_ability','mng_score'],
            'mmf':['ret_ability','risk_ability','mng_score']
        }
        res = []
        for fund_type, score_list in dic.items():
            df = fund_indicator[fund_indicator['fund_type'] == fund_type].copy()
            df['total_score'] = score_rescale(df[score_list].sum(axis=1))
            res.append(df)
        fund_indicator_result = pd.concat(res)
        self.fund_indicator_score = fund_indicator_result

    def to_s3(self):
        bucket_name = 'tl-fund-dm'
        _s3_bucket_uri: str = f's3://{bucket_name}/dm'
        name = 'fund_indicator_score'
        self.fund_indicator_score.to_parquet(f'{_s3_bucket_uri}/{name}.parquet', compression='gzip')
        
    def process(self,end_date):
        failed_tasks = []
        try:
            self.init(end_date=end_date)
            self.calc_indicator()
            self.calc_score()
            self.add_mng_score()
            self.to_s3()
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append('manager_indicator_score')
        return failed_tasks