
import pandas as pd
import numpy as np
import datetime
import traceback
from functools import partial
from sklearn.metrics import r2_score
import concurrent.futures
from multiprocessing import Pool
from ....data.struct import AssetTimeSpan
from ...manager.manager_fund import FundDataManager
from ...manager.score import FundScoreManager
from ...wrapper.mysql import DerivedDatabaseConnector
from ...view.derived_models import *
from .derived_data_helper import DerivedDataHelper
from ...api.derived import DerivedDataApi


class FundIndicatorProcessor(object):

    TRADING_DAYS_PER_YEAR = 242
    NATURAL_DAYS_PER_YEAR = 365
    SHORT_TIME_SPAN = TRADING_DAYS_PER_YEAR
    LONG_TIME_SPAN = TRADING_DAYS_PER_YEAR * 3
    LONG_TERM_INDEX = ['hs300', 'csi500', 'mmf']
    MIN_TIME_SPAN = int(TRADING_DAYS_PER_YEAR / 4)#为了延长基金回测范围，评分最低年限3个月
    RISK_FEE_RATE = 0.025
    RISK_FEE_RATE_PER_DAY = RISK_FEE_RATE / TRADING_DAYS_PER_YEAR

    def __init__(self, data_helper):
        self._data_helper = data_helper

    def init(self, start_date='20040101', end_date='20200630', dm=None):    
        if dm is None:
            self._dm = FundDataManager(start_time=start_date, end_time=end_date, score_manager=FundScoreManager())
            self._dm.init(score_pre_calc=False)
        else:
            self._dm = dm
        self.start_date = self._dm.start_date
        self.end_date = self._dm.end_date
        self.fund_nav = self._dm.dts.fund_nav.copy()
        self.fund_info = self._dm.dts.fund_info.copy()
        self.index_price = self._dm.dts.index_price.copy()
        
        # 指数日线价格和基金净值 时间轴对齐 ，避免join后因为日期不存在出现价格空值_rolling_alpha_beta_time_ret_r2_base
        # 指数数据历史上出现非交易日有数据，join后，基金净值出现空值，长周期时间序列算指标出空值 
        # 避免对日收益fillna(0)， 造成track error 计算不符合实际
        # 计算逻辑空值填充情况： 1. 只对基金费率空值fillna(0) 
        #                    2. manager fund 里对日线价格ffill
        #                    3. 指数数据按照基金数据重做index后ffill(有基金数据对日子,没有指数数据，比如季报出在季度末，非交易日有基金净值)
        #                    4. 有对超过基金终止日净值赋空值
        self.trading_days = self._dm.dts.trading_days.datetime
        end_date = min(self.fund_nav.index[-1], self.index_price.index[-1])
        self.fund_nav = self.fund_nav.reindex(self.trading_days).loc[:end_date]
        self.index_price = self.index_price.reindex(self.trading_days).loc[:end_date]
        fund_nav_index = self.fund_nav.index
        self.index_price = self.index_price.reindex(fund_nav_index).fillna(method = 'ffill')
        l1 = self.fund_nav.index.to_list().sort()
        l2 = self.index_price.index.to_list().sort()
        assert l1 == l2, f'date index of index price and fund nav are not identical, l1 {l1} lens {len(l1)}, l2 {l2} lens {len(l2)}'

        fund_to_enddate_dict = self.fund_info[['fund_id', 'end_date']].set_index('fund_id').to_dict()['end_date']
        self.fund_to_index_dict = self.fund_info[['fund_id', 'index_id']].set_index('fund_id').to_dict()['index_id']
        # 超过基金终止日的基金净值赋空
        for fund_id in self.fund_nav.columns:
            fund_end_date = fund_to_enddate_dict[fund_id]
            if self.end_date > fund_end_date:
                self.fund_nav.loc[fund_end_date:,fund_id] = np.nan
        self.fund_ret = np.log(self.fund_nav / self.fund_nav.shift(1))
        self.fund_ret = self.fund_ret.stack().reset_index(level=[0,1]).rename(columns={0:'ret'})
        self.fund_ret = self.fund_ret.pivot_table(index='datetime',columns='fund_id',values='ret')        
        # self.fund_ret['index_id'] = self.fund_ret.fund_id.apply(lambda x: self.fund_to_index_dict[x])
        # self.fund_ret = self.fund_ret.pivot_table(index = ['index_id','datetime'],columns='fund_id',values='ret')
        self.index_ret = np.log(self.index_price / self.index_price.shift(1))
        self.fund_to_index_dict = {fund_id:index_id for fund_id,index_id in self.fund_to_index_dict.items() if fund_id in self.fund_ret.columns}
        self.index_list = list(AssetTimeSpan.__dataclass_fields__.keys())
        self.index_fund = { index_id : [fund_idx for fund_idx, index_idx in self.fund_to_index_dict.items() if index_idx == index_id] for index_id in self.index_list}
        self.index_fund['conv_bond'] = self._dm.dts.fund_conv_list
        self.start_date_dic = self.fund_info[['fund_id','start_date']].set_index('fund_id').to_dict()['start_date']

    def get_time_range(self, index_id):
        if index_id in self.LONG_TERM_INDEX:
            return self.LONG_TIME_SPAN
        else:
            return self.SHORT_TIME_SPAN

    ''' 
    尝试过几个版本的回归函数， 计算结果一致
    1. 最早使用的是pyfinance.PandasRollingOLS  可以对一只基金直接返回beta, alpha, 可以设置滚动周期, 运算比较快， 缺点是无法设置min_periods，最小滚动周期
    2. pyfinance.PandasRollingOLS 本质是使用statsmodels.regression.rolling.RollingOLS, 需要手动增加回归常数项，函数下存在最小窗口设置，但是使用无效，
       而且window实际的含义和pandas.rolling.window有区别，导致计算有效值和nan的边界时间不一致
    3. np.polyfit 一元回归，自带回归常数项，可以设置回归最高幂
    '''

    def _rolling_alpha_beta_time_ret_r2(self, x, res, df, is_only_alpha_beta=False):
        # 回归相关的都在这里
        df_i = df.loc[x[0]:x[-1],]
        return self._rolling_alpha_beta_time_ret_r2_base(res,df_i,is_only_alpha_beta)

    def _rolling_alpha_beta_time_ret_r2_base(self, res, df_i, is_only_alpha_beta=False):
        if sum(df_i.fund) == 0:
            res.append({'alpha':np.Inf,'beta':np.Inf,'time_ret':np.Inf})
            return 1
        else:
            ploy_res = np.polyfit(y=df_i.fund, x=df_i.benchmark,deg=1)
            p = np.poly1d(ploy_res)
            r2 = r2_score(df_i.fund, p(df_i.benchmark))
            beta = ploy_res[0]
            alpha = ploy_res[1] * self.TRADING_DAYS_PER_YEAR
            if is_only_alpha_beta:
                res.append({'alpha':alpha,'beta':beta})
                return 1
            day_len = df_i.shape[0]
            bar_num = int( day_len / self.MIN_TIME_SPAN)

            _res = []
            for i in range(bar_num):
                start_i = - (i + 1) * self.MIN_TIME_SPAN
                end_i = - i * self.MIN_TIME_SPAN
                if end_i == 0:
                    dftmp = df_i.iloc[start_i:]
                else:
                    dftmp = df_i.iloc[start_i:end_i]
                _ploy_res = np.polyfit(y=dftmp.fund, x=dftmp.benchmark,deg=1)
                
                _res.append({'beta_i_no_whole_beta': _ploy_res[0] - beta,
                            'bench_r_no_risk': dftmp.benchmark.sum() - self.RISK_FEE_RATE_PER_DAY * day_len })
            time_ret = np.sum([ _['beta_i_no_whole_beta'] * _['bench_r_no_risk'] for _ in _res])
            res.append({'alpha': alpha, 
                        'beta': beta,
                        'time_ret':time_ret,
                        'r_square':r2})
            return 1

    def _rolling_mdd(self, x):
        x = pd.Series(x)
        return 1 - (x / x.cummax()).min()

    def _rolling_annual_ret(self, x):
        x = pd.Series(x).dropna()
        year = x.shape[0] / self.TRADING_DAYS_PER_YEAR
        return np.exp(np.log(x.values[-1]/x.values[0])/year) - 1
 
    def _process_fund_indicator_update(self, fund_id, time_range, fund_ret, index_id, index_ret):
        df = fund_ret[[fund_id]].join(index_ret).dropna()
        if df.empty:
            return
        df = df.rename(columns={index_id:'benchmark',fund_id:'fund'}).reset_index()
        last_day = df.datetime.values[-1]
        year_length = (last_day-self.start_date_dic[fund_id]).days / self.NATURAL_DAYS_PER_YEAR
        df = df.iloc[-time_range:].dropna()
        if df.shape[0] < self.MIN_TIME_SPAN:
            return None
        res = []
        self._rolling_alpha_beta_time_ret_r2_base(res, df)
        fund_indicator_part1 = res[0]
        if fund_indicator_part1['alpha'] in [np.Inf, -np.Inf]:
            return None
        df_hs300 = self.fund_ret[[fund_id]].join(self.index_ret['hs300']).rename(columns={'hs300':'benchmark',fund_id:'fund'}).reset_index().iloc[-time_range:].dropna()
        df_bond = self.fund_ret[[fund_id]].join(self.index_ret['national_debt']).rename(columns={'national_debt':'benchmark',fund_id:'fund'}).reset_index().iloc[-time_range:].dropna()
        res = []
        self._rolling_alpha_beta_time_ret_r2_base(res, df_hs300, is_only_alpha_beta=True)
        fund_indicator_hs300 = res[0]
        res = []
        self._rolling_alpha_beta_time_ret_r2_base(res, df_bond, is_only_alpha_beta=True)
        fund_indicator_bond = res[0]
        track_err = (df.fund - df.benchmark).std(ddof=1) * np.sqrt(self.TRADING_DAYS_PER_YEAR)
        timespan = int(time_range / self.TRADING_DAYS_PER_YEAR)
        fee_rate = self.fund_fee[fund_id]
        info_ratio = fund_indicator_part1['alpha'] / track_err
        mean_ret = df.fund.mean()
        mean_ret_no_free_ret = mean_ret - self.RISK_FEE_RATE_PER_DAY
        treynor = mean_ret_no_free_ret * time_range / fund_indicator_part1['beta']
        if self.fund_nav[[fund_id]][-time_range:].dropna().shape[0] < self.MIN_TIME_SPAN:
            return None
        mdd = self.fund_nav[[fund_id]][-time_range:].apply(self._rolling_mdd, raw=True).values[0]
        down_risk = np.abs(np.minimum(df['fund'] - self.RISK_FEE_RATE_PER_DAY, 0)).mean()* np.sqrt(self.TRADING_DAYS_PER_YEAR)
        ret_over_period = self.fund_nav[fund_id][-1] / self.fund_nav[fund_id].fillna(method='bfill')[-time_range-1] - 1
        annual_avg_daily_ret = df['fund'].mean() * self.TRADING_DAYS_PER_YEAR 
        annual_ret = self.fund_nav[[fund_id]][-time_range:].apply(self._rolling_annual_ret, raw=True)[0]
        annual_vol = df['fund'].std(ddof=1) * np.sqrt(self.TRADING_DAYS_PER_YEAR)
        vol_benchmark = df['benchmark'].std(ddof=1) * np.sqrt(self.TRADING_DAYS_PER_YEAR)
        mean_ret_benchmark = df['benchmark'].mean()
        m_square = vol_benchmark / annual_vol * mean_ret_no_free_ret + self.RISK_FEE_RATE_PER_DAY - mean_ret_benchmark
        var = np.minimum(df['fund'].quantile(0.05), 0) * -1
        sharpe = (annual_ret - self.RISK_FEE_RATE) / annual_vol
        dic = {
            'fund_id':fund_id,
            'datetime':last_day,
            'beta':fund_indicator_part1['beta'],
            'alpha':fund_indicator_part1['alpha'],
            'time_ret':fund_indicator_part1['time_ret'],
            'r_square':fund_indicator_part1['r_square'],
            'track_err':track_err,
            'timespan':timespan,
            'fee_rate':fee_rate,
            'info_ratio':info_ratio,
            'treynor':treynor,
            'mdd':mdd,
            'down_risk':down_risk,
            'ret_over_period':ret_over_period,
            'annual_avg_daily_ret':annual_avg_daily_ret,
            'annual_ret':annual_ret,
            'annual_vol':annual_vol,
            'm_square':m_square,
            'var':var,
            'sharpe':sharpe,
            'year_length':year_length,
            'alpha_bond':fund_indicator_bond['alpha'],
            'beta_bond':fund_indicator_bond['beta'],
            'alpha_hs300':fund_indicator_hs300['alpha'],
            'beta_hs300':fund_indicator_hs300['beta'],}
        return dic

    def _process_fund_indicator_one(self, time_range, fund_ret, index_id, index_ret, fund_id):
        try:
            df = fund_ret[[fund_id]].join(index_ret).dropna()
            df = df.rename(columns={index_id:'benchmark',fund_id:'fund'}).reset_index()
            df['year_length'] = df['datetime'].map(lambda x: (x-self.start_date_dic[fund_id]).days / self.NATURAL_DAYS_PER_YEAR)
            res = []
            pd.Series(df.index).rolling(
                window=time_range,min_periods=self.MIN_TIME_SPAN).apply(
                    partial(self._rolling_alpha_beta_time_ret_r2, res=res, df=df), raw=True)
            df = df.set_index('datetime')
            df = df.join(pd.DataFrame(res,index=df.index[-len(res):]))
            if 'alpha' not in df.columns:
                return None
            df_hs300 = self.fund_ret[[fund_id]].join(self.index_ret['hs300']).rename(columns={'hs300':'benchmark',fund_id:'fund'}).reset_index().dropna()
            df_bond = self.fund_ret[[fund_id]].join(self.index_ret['national_debt']).rename(columns={'national_debt':'benchmark',fund_id:'fund'}).reset_index().dropna()
            res_hs300 = []
            pd.Series(df_hs300.index).rolling(
                window=time_range,min_periods=self.MIN_TIME_SPAN).apply(
                    partial(self._rolling_alpha_beta_time_ret_r2, res=res_hs300, df=df_hs300, is_only_alpha_beta=True), raw=True)
            res_hs300 = pd.DataFrame(res_hs300, index=df_hs300.datetime[-len(res_hs300):]).rename(columns={'alpha':'alpha_hs300','beta':'beta_hs300'})
            res_bond = []
            pd.Series(df_bond.index).rolling(
                window=time_range,min_periods=self.MIN_TIME_SPAN).apply(
                    partial(self._rolling_alpha_beta_time_ret_r2, res=res_bond, df=df_bond, is_only_alpha_beta=True), raw=True)
            res_bond = pd.DataFrame(res_bond, index=df_bond.datetime[-len(res_bond):]).rename(columns={'alpha':'alpha_bond','beta':'beta_bond'})
            df = df.join(res_hs300).join(res_bond)
            df['track_err'] = (df.fund - df.benchmark).rolling(window=time_range, min_periods=self.MIN_TIME_SPAN).std(ddof=1)* np.sqrt(self.TRADING_DAYS_PER_YEAR)
            df['fund_id'] = fund_id
            df['timespan'] = int(time_range / self.TRADING_DAYS_PER_YEAR)
            df['fee_rate'] = self.fund_fee[fund_id]
            df['info_ratio'] = df.alpha / df.track_err
            df['mean_ret'] = df[['fund']].rolling(window=time_range,min_periods=self.MIN_TIME_SPAN).mean()
            df['mean_ret_no_free_ret'] = df['mean_ret'] - self.RISK_FEE_RATE_PER_DAY
            df['treynor'] = df['mean_ret_no_free_ret'] * time_range / df.beta
            df['mdd'] = self.fund_nav[[fund_id]].rolling(window=time_range,min_periods=self.MIN_TIME_SPAN).apply(self._rolling_mdd, raw=True)
            df['down_risk'] = np.abs(np.minimum(df['fund'] - self.RISK_FEE_RATE_PER_DAY, 0))
            df['down_risk'] = df['down_risk'].rolling(window=time_range,min_periods=self.MIN_TIME_SPAN).mean()* np.sqrt(self.TRADING_DAYS_PER_YEAR)
            df['ret_over_period'] = self.fund_nav[[fund_id]] / self.fund_nav[[fund_id]].fillna(method='bfill').shift(time_range) - 1
            df['annual_avg_daily_ret'] = df['fund'].rolling(window=time_range,min_periods=self.MIN_TIME_SPAN).mean() * self.TRADING_DAYS_PER_YEAR 
            df['annual_ret'] = self.fund_nav[[fund_id]].rolling(window=time_range,min_periods=self.MIN_TIME_SPAN).apply(self._rolling_annual_ret, raw=True)
            df['annual_vol'] = df['fund'].rolling(window=time_range,min_periods=self.MIN_TIME_SPAN).std(ddof=1) * np.sqrt(self.TRADING_DAYS_PER_YEAR)
            df['vol_benchmark'] = df['benchmark'].rolling(window=time_range,min_periods=self.MIN_TIME_SPAN).std(ddof=1) * np.sqrt(self.TRADING_DAYS_PER_YEAR)
            df['mean_ret_benchmark'] = df[['benchmark']].rolling(window=time_range,min_periods=self.MIN_TIME_SPAN).mean()
            df['m_square'] = df['vol_benchmark'] / df['annual_vol'] * df['mean_ret_no_free_ret'] + self.RISK_FEE_RATE_PER_DAY - df['mean_ret_benchmark']
            df['var'] = df['fund'].rolling(window=time_range,min_periods=self.MIN_TIME_SPAN).quantile(0.05)
            df['var'] = np.minimum(df['var'], 0) * -1
            df['sharpe'] = (df.annual_ret - self.RISK_FEE_RATE) / df.annual_vol
            df = df.drop(['fund','benchmark','vol_benchmark','mean_ret_no_free_ret','mean_ret_benchmark','mean_ret'], axis=1)
            # build history insert
            df = df.replace({-np.Inf:None,np.Inf:None}).dropna(subset=['beta', 'alpha','track_err']).reset_index()
            #self._data_helper._upload_derived(df, FundIndicator.__table__.name)
        except:
            print(f'fund_id {fund_id} calc indicator error')
        return df

    def calculate_history(self, index_id_list:str=None, cpu_num:int=2):
        self.fund_fee = self.fund_info[['fund_id','manage_fee','trustee_fee']].set_index('fund_id').fillna(0).sum(axis = 1)
        result = []
        index_list = self.index_list if index_id_list is None else index_id_list
        fund_index_dict = {}
        for index_id in index_list:
            time_range = self.get_time_range(index_id)
            if index_id in ['active']:
                continue
            if index_id in ['conv_bond']:
                fund_list = self.index_fund[index_id]
                fund_list = [i for i in fund_list if i not in fund_index_dict]
                fund_list = [i for i in fund_list if i in self.fund_ret.columns]
            else:
                fund_list_1 = self.index_fund[index_id]
                fund_list_2 = self._dm.dts.active_fund_info[self._dm.dts.active_fund_info['index_id'] == index_id].fund_id.tolist()
                fund_list = list(set(fund_list_1).union(set(fund_list_2)).intersection(self._dm.dts.all_fund_list))
            fund_ret = self.fund_ret[fund_list].copy()
            index_ret = self.index_ret[[index_id]]
            p = Pool()
            res = [i for i in p.imap_unordered(partial(self._process_fund_indicator_one, time_range, fund_ret, index_id, index_ret), fund_list, 256) if i is not None]
            p.close()
            p.join()
            result.extend(res)    
            print(f'index {index_id} fund number : {len(fund_list)} finish' )
            for fund_id in fund_list:
                fund_index_dict[fund_id] = index_id
        result = [ _ for _ in result if not _ is None]
        self.result = pd.concat(result, axis=0, sort=True)

    def calculate_update(self, dt):
        self.fund_fee = self.fund_info[['fund_id','manage_fee','trustee_fee']].set_index('fund_id').fillna(0).sum(axis = 1)
        result = []
        index_list = self.index_list
        fund_index_dict = {}
        for index_id in index_list:
            time_range = self.get_time_range(index_id)
            if index_id in ['active']:
                continue
            if index_id in ['conv_bond']:
                fund_list = self.index_fund[index_id]
                fund_list = [i for i in fund_list if i not in fund_index_dict]
                fund_list = [i for i in fund_list if i in self.fund_ret.columns]
            else:
                fund_list_1 = self.index_fund[index_id]
                fund_list_2 = self._dm.dts.active_fund_info[self._dm.dts.active_fund_info['index_id'] == index_id].fund_id.tolist()
                fund_list = list(set(fund_list_1).union(set(fund_list_2)).intersection(self._dm.dts.all_fund_list))
            fund_list = list(self.fund_ret.columns.intersection(fund_list))
            fund_ret = self.fund_ret[fund_list].copy()
            index_ret = self.index_ret[[index_id]]
            for fund_id in fund_list:
                result.append(self._process_fund_indicator_update(fund_id, time_range, fund_ret.loc[:dt], index_id, index_ret.loc[:dt]))
            print(f'index {index_id} finish fund number fund_list {len(fund_list)} fund_list_1 {len(fund_list_1)} fund_list_2 {len(fund_list_2)}')
            for fund_id in fund_list:
                fund_index_dict[fund_id] = index_id
        result = [ _ for _ in result if not _ is None]
        self.result = pd.DataFrame(result)
        self.result = self.result.replace({-np.Inf:None,np.Inf:None}).dropna(subset=['beta', 'alpha','track_err'])

    def process(self, start_date, end_date):
        failed_tasks = []
        try:
            start_date_dt = datetime.datetime.strptime(start_date, '%Y%m%d').date()
            end_date_dt = datetime.datetime.strptime(end_date, '%Y%m%d').date()

            start_date = start_date_dt - datetime.timedelta(days = 1150) #3年历史保险起见，多取几天 3*365=1095 
            start_date = datetime.datetime.strftime(start_date, '%Y%m%d')

            self.init(start_date=start_date, end_date=end_date)

            self._update_begin_date = self._dm.dts.trading_days[self._dm.dts.trading_days.datetime <= self.end_date] 
            update_dt_list = self._update_begin_date.datetime.values[-3:].tolist()
            self.fac_result = []
            for dt in update_dt_list:
                self.calculate_update(dt)
                self.fac_result.append(self.result)
            df = pd.concat(self.fac_result)
            df = df[df.datetime.isin(update_dt_list)]
            df = df.drop_duplicates(subset=['datetime','fund_id'])
            for date in df.datetime.unique():
                DerivedDataApi().delete_fund_indicator_with_dt(date, df[df.datetime == date].fund_id.to_list())
            self._data_helper._upload_derived(df, FundIndicator.__table__.name)
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append('fund_indicator')

        return failed_tasks


if __name__ == '__main__':
    fip = FundIndicatorProcessor(DerivedDataHelper())
    fip.process('20210602', '20210602')
